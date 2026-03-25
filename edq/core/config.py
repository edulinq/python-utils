import argparse
import os
import typing

import platformdirs

import edq.util.dirent
import edq.util.json
import edq.util.serial

CONFIG_SOURCE_CLI: str = "<cli argument>"
CONFIG_SOURCE_CLI_FILE: str = "<cli config file>"
CONFIG_SOURCE_GLOBAL: str = "<global config file>"
CONFIG_SOURCE_LOCAL: str = "<local config file>"

CONFIG_PATHS_KEY: str = 'config_paths'
GLOBAL_CONFIG_KEY: str = 'global_config_path'
CONFIG_OPTIONS_KEY: str = 'configs'
IGNORE_CONFIG_OPTIONS_KEY: str = 'ignore_configs'

DEFAULT_CONFIG_FILENAME: str = "edq-config.json"

_config_filename: str = DEFAULT_CONFIG_FILENAME  # pylint: disable=invalid-name
_legacy_config_filename: typing.Union[str, None] = None  # pylint: disable=invalid-name

class ConfigSource(edq.util.serial.DictConverter):
    """ A class for storing config source information. """

    def __init__(self, label: str, path: typing.Union[str, None] = None) -> None:
        self.label = label
        """ The label identifying the config (see CONFIG_SOURCE_* constants). """

        self.path = path
        """ The path of where the config was sourced from. """

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, ConfigSource)):
            return False

        return ((self.label == other.label) and (self.path == other.path))

    def __str__(self) -> str:
        return f"({self.label}, {self.path})"

class TieredConfigInfo(edq.util.serial.DictConverter):
    """ A class for storing config information read from a hierarchy of files and sources. """

    def __init__(self,
            config_filename: str,
            local_config_path: str,
            global_config_path: str,
            config: typing.Dict[str, typing.Any],
            sources: typing.Dict[str, ConfigSource],
            ) -> None:
        self.config_filename: str = config_filename
        """ Config filename searched for. """

        self.local_config_path: str  = local_config_path
        """
        Path searched for local config.
        The file might not exist.
        """

        self.global_config_path: str = global_config_path
        """
        Path searched for global config.
        The file might not exist.
        """

        self.config: typing.Dict[str, typing.Any] = config
        """ Key-value configurations. """

        self.sources: typing.Dict[str, ConfigSource] = sources
        """ Where configs came from. """

def set_config_filename(filename: str) -> None:
    """ Sets the config filename. """

    global _config_filename  # pylint: disable=global-statement
    _config_filename = filename

def set_legacy_config_filename(legacy_filename: str) -> None:
    """ Sets the legacy config filename. """

    global _legacy_config_filename  # pylint: disable=global-statement
    _legacy_config_filename = legacy_filename

def get_config_filename() -> str:
    """ Gets the config filename. """

    return _config_filename

def get_legacy_config_filename() -> typing.Union[str, None]:
    """ Gets the config legacy filename. """

    return _legacy_config_filename

def get_global_config_path() -> str:
    """ Get the path for the global config file. """

    return platformdirs.user_config_dir(get_config_filename())

def update_config_file(path: str, config_to_write: typing.Dict[str, str]) -> None:
    """
    Write configs to the specified path.
    Create the path if it does not exist.
    Existing keys in the file will be overwritten with the new values.
    """

    config = {}
    if (edq.util.dirent.exists(path)):
        config = edq.util.json.load_path(path)

    config.update(config_to_write)

    edq.util.dirent.mkdir(os.path.dirname(path))
    edq.util.json.dump_path(config, path, indent = 4)

def get_tiered_config(
        cli_arguments: typing.Union[dict, argparse.Namespace, None] = None,
        local_config_root_cutoff: typing.Union[str, None] = None,
    ) -> TieredConfigInfo:
    """
    Load all configuration options from files and command-line arguments.
    """

    if (cli_arguments is None):
        cli_arguments = {}

    config: typing.Dict[str, typing.Any] = {}
    sources: typing.Dict[str, ConfigSource] = {}

    # Ensure CLI arguments are always a dict,
    # even if provided as argparse.Namespace.
    if (isinstance(cli_arguments, argparse.Namespace)):
        cli_arguments = vars(cli_arguments)

    # Load the global user config file.
    global_config_path = cli_arguments.get(GLOBAL_CONFIG_KEY, get_global_config_path())
    _load_config_file(global_config_path, config, sources, CONFIG_SOURCE_GLOBAL)

    # Get and load local user config path.
    local_config_path = _get_local_config_path(
        local_config_root_cutoff = local_config_root_cutoff,
    )

    if (local_config_path is None):
        local_config_path = os.path.abspath(get_config_filename())

    _load_config_file(local_config_path, config, sources, CONFIG_SOURCE_LOCAL)

    # Check the config file specified on the command-line.
    config_paths = cli_arguments.get(CONFIG_PATHS_KEY, [])
    for path in config_paths:
        if (not os.path.exists(path)):
            raise FileNotFoundError(f"Specified config file does not exist: '{path}'.")

        _load_config_file(path, config, sources, CONFIG_SOURCE_CLI_FILE)

    # Check the command-line config options.
    cli_configs = cli_arguments.get(CONFIG_OPTIONS_KEY, [])
    for cli_config_option in cli_configs:
        (key, value) = parse_string_config_option(cli_config_option)

        config[key] = value
        sources[key] = ConfigSource(label = CONFIG_SOURCE_CLI)

    # Finally, ignore any configs that is specified from CLI command.
    cli_ignore_configs = cli_arguments.get(IGNORE_CONFIG_OPTIONS_KEY, [])
    for ignore_config in cli_ignore_configs:
        config.pop(ignore_config, None)
        sources.pop(ignore_config, None)

    return TieredConfigInfo(get_config_filename(), local_config_path, global_config_path, config, sources)

def parse_string_config_option(
        config_option: str,
    ) -> typing.Tuple[str, str]:
    """
    Parse and validate a configuration option string in the format of '<key>=<value>'.
    Returns the resulting config option as a key-value pair.
    """

    if ("=" not in config_option):
        raise ValueError(
            f"Invalid configuration option string '{config_option}'."
            + " Configuration options must be provided in the format '<key>=<value>'.")

    (key, value) = config_option.split('=', maxsplit = 1)
    key = _validate_config_key(key, value)

    return key, value

def _validate_config_key(config_key: str, config_value: str) -> str:
    """ Validate a configuration key and return its clean version. """

    key = config_key.strip()
    if (key == ''):
        raise ValueError(f"Found an empty configuration option key associated with the value '{config_value}'.")

    return key

def _load_config_file(
        config_path: str,
        config: typing.Dict[str, typing.Any],
        sources: typing.Dict[str, ConfigSource],
        source_label: str,
    ) -> None:
    """
    Loads config variables and the source from the given config JSON file.
    If the given config JSON file deosn't exit loads nothing.
    """

    if (not edq.util.dirent.exists(config_path)):
        return

    if (os.path.isdir(config_path)):
        raise IsADirectoryError(f"Failed to read config file, expected a file but got a directory at '{config_path}'.")

    config_path = os.path.abspath(config_path)
    for (key, value) in edq.util.json.load_path(config_path).items():
        key = _validate_config_key(key, value)

        config[key] = value
        sources[key] = ConfigSource(label = source_label, path = config_path)

def _get_local_config_path(
        local_config_root_cutoff: typing.Union[str, None] = None,
    ) -> typing.Union[str, None]:
    """
    Search for a config file in hierarchical order.
    Begins with the provided config file name,
    then legacy config file name (if set),
    then continues up the directory tree looking for the provided config file name.
    Returns the absolute path to the first config file found.

    Returns None if no config file is found.

    The cutoff parameter limits the search depth,
    preventing detection of config file in higher-level directories during testing.
    """

    config_filename = get_config_filename()
    legacy_config_filename = get_legacy_config_filename()

    # Provided config file is in current directory.
    if (os.path.isfile(config_filename)):
        return os.path.abspath(config_filename)

    # Provided legacy config file is in current directory.
    if (legacy_config_filename is not None):
        if (os.path.isfile(legacy_config_filename)):
            return os.path.abspath(legacy_config_filename)

    # Provided config file is found in an ancestor directory up to the root or cutoff limit.
    parent_dir = os.path.dirname(os.getcwd())
    return _get_ancestor_config_file_path(
        parent_dir,
        local_config_root_cutoff = local_config_root_cutoff,
    )

def _get_ancestor_config_file_path(
        current_directory: str,
        local_config_root_cutoff: typing.Union[str, None] = None,
    ) -> typing.Union[str, None]:
    """
    Search through the parent directories (until root or a given cutoff directory(inclusive)) for a config file.
    Stops at the first occurrence of the specified config file along the path to root.
    Returns the path if a config file is found.
    Otherwise, returns None.
    """

    if (local_config_root_cutoff is not None):
        local_config_root_cutoff = os.path.abspath(local_config_root_cutoff)

    current_directory = os.path.abspath(current_directory)
    for _ in range(edq.util.dirent.DEPTH_LIMIT):
        config_file_path = os.path.join(current_directory, get_config_filename())
        if (os.path.isfile(config_file_path)):
            return config_file_path

        # Check if current directory is root.
        parent_dir = os.path.dirname(current_directory)
        if (parent_dir == current_directory):
            break

        if (local_config_root_cutoff == current_directory):
            break

        current_directory = parent_dir

    return None

def set_cli_args(parser: argparse.ArgumentParser, extra_state: typing.Dict[str, typing.Any],
        **kwargs: typing.Any,
    ) -> None:
    """
    Set common CLI arguments for configuration.
    """

    group = parser.add_argument_group('config options')

    group.add_argument('--config', dest = CONFIG_OPTIONS_KEY, metavar = "<KEY>=<VALUE>",
        action = 'append', type = str, default = [],
        help = ('Set a configuration option from the command-line.'
            + ' Specify options as <key>=<value> pairs.'
            + ' This flag can be specified multiple times.'
            + ' The options are applied in the order provided and later options override earlier ones.'
            + ' Will override options form all config files.')
    )

    group.add_argument('--config-file', dest = CONFIG_PATHS_KEY,
        action = 'append', type = str, default = [],
        help = ('Load config options from a JSON file.'
            + ' This flag can be specified multiple times.'
            + ' Files are applied in the order provided and later files override earlier ones.'
            + ' Will override options form both global and local config files.')
    )

    group.add_argument('--config-global', dest = GLOBAL_CONFIG_KEY,
        action = 'store', type = str, default = get_global_config_path(),
        help = 'Set the default global config file path (default: %(default)s).',
    )

    group.add_argument('--ignore-config-option', dest = IGNORE_CONFIG_OPTIONS_KEY,
        action = 'append', type = str, default = [],
        help = ('Ignore any config option with the specified key.'
            + ' The system-provided default value will be used for that option if one exists.'
            + ' This flag can be specified multiple times.'
            + ' Ignored options are processed last.')
    )

def load_config_into_args(
        parser: argparse.ArgumentParser,
        args: argparse.Namespace,
        extra_state: typing.Dict[str, typing.Any],
        cli_arg_config_map: typing.Union[typing.Dict[str, str], None] = None,
        **kwargs: typing.Any,
    ) -> None:
    """
    Take in args from a parser that was passed to set_cli_args(),
    and get the tired configuration with the appropriate parameters, and attache it to args.

    Arguments that appear on the CLI as flags (e.g. `--foo bar`) can be copied over to the config options via `cli_arg_config_map`.
    The keys of `cli_arg_config_map` represent attributes in the CLI arguments (`args`),
    while the values represent the desired config name this argument should be set as.
    For example, a `cli_arg_config_map` of `{'foo': 'baz'}` will make the CLI argument `--foo bar`
    be equivalent to `--config baz=bar`.
    """

    if (cli_arg_config_map is None):
        cli_arg_config_map = {}

    for (cli_key, config_key) in cli_arg_config_map.items():
        value = getattr(args, cli_key, None)
        if (value is not None):
            getattr(args, CONFIG_OPTIONS_KEY).append(f"{config_key}={value}")

    config_info = get_tiered_config(cli_arguments = args)
    setattr(args, "_config_info", config_info)
