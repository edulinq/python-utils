import argparse
import os
import typing

import platformdirs

import edq.util.dirent
import edq.util.json

CONFIG_SOURCE_GLOBAL: str = "<global config file>"
CONFIG_SOURCE_LOCAL: str = "<local config file>"
CONFIG_SOURCE_CLI: str = "<cli config file>"
CONFIG_SOURCE_CLI_BARE: str = "<cli argument>"

CONFIG_PATHS_KEY: str = 'config_paths'
DEFAULT_CONFIG_FILENAME: str = "edq-config.json"
DEFAULT_GLOBAL_CONFIG_PATH: str = platformdirs.user_config_dir(DEFAULT_CONFIG_FILENAME)

class ConfigSource:
    """ A class for storing config source information. """

    def __init__(self, label: str, path: typing.Union[str, None] = None) -> None:
        self.label = label
        """ The label identifying the config (see CONFIG_SOURCE_* constants). """

        self.path = path
        """ The path of where the config was soruced from. """

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, ConfigSource)):
            return False

        return ((self.label == other.label) and (self.path == other.path))

    def __str__(self) -> str:
        return f"({self.label}, {self.path})"

def get_tiered_config(
        config_file_name: str = DEFAULT_CONFIG_FILENAME,
        legacy_config_file_name: typing.Union[str, None] = None,
        global_config_path: typing.Union[str, None] = None,
        skip_keys: typing.Union[list, None] = None,
        cli_arguments: typing.Union[dict, argparse.Namespace, None] = None,
        local_config_root_cutoff: typing.Union[str, None] = None,
    ) -> typing.Tuple[typing.Dict[str, str], typing.Dict[str, ConfigSource]]:
    """
    Load all configuration options from files and command-line arguments.
    Returns a configuration dictionary with the values based on tiering rules and a source dictionary mapping each key to its origin.
    """

    if (global_config_path is None):
        global_config_path = platformdirs.user_config_dir(config_file_name)

    if (skip_keys is None):
        skip_keys = [CONFIG_PATHS_KEY]

    if (cli_arguments is None):
        cli_arguments = {}

    config: typing.Dict[str, str] = {}
    sources: typing.Dict[str, ConfigSource] = {}

    # Ensure CLI arguments are always a dict, even if provided as argparse.Namespace.
    if (isinstance(cli_arguments, argparse.Namespace)):
        cli_arguments = vars(cli_arguments)

    # Check the global user config file.
    if (os.path.isfile(global_config_path)):
        _load_config_file(global_config_path, config, sources, CONFIG_SOURCE_GLOBAL)

    # Check the local user config file.
    local_config_path = _get_local_config_path(
        config_file_name = config_file_name,
        legacy_config_file_name = legacy_config_file_name,
        local_config_root_cutoff = local_config_root_cutoff,
    )

    if (local_config_path is not None):
        _load_config_file(local_config_path, config, sources, CONFIG_SOURCE_LOCAL)

    # Check the config file specified on the command-line.
    config_paths = cli_arguments.get(CONFIG_PATHS_KEY, [])
    if (config_paths is not None):
        for path in config_paths:
            _load_config_file(path, config, sources, CONFIG_SOURCE_CLI)

    # Finally, any command-line options.
    for (key, value) in cli_arguments.items():
        if (key in skip_keys):
            continue

        if ((value is None) or (value == '')):
            continue

        config[key] = value
        sources[key] = ConfigSource(label = CONFIG_SOURCE_CLI_BARE)

    return config, sources

def _load_config_file(
        config_path: str,
        config: typing.Dict[str, str],
        sources: typing.Dict[str, ConfigSource],
        source_label: str,
    ) -> None:
    """ Loads config variables and the source from the given config JSON file. """

    config_path = os.path.abspath(config_path)
    for (key, value) in edq.util.json.load_path(config_path).items():
        config[key] = value
        sources[key] = ConfigSource(label = source_label, path = config_path)

def _get_local_config_path(
        config_file_name: str,
        legacy_config_file_name: typing.Union[str, None] = None,
        local_config_root_cutoff: typing.Union[str, None] = None,
    ) -> typing.Union[str, None]:
    """
    Search for a config file in hierarchical order.
    Begins with the provided config file name,
    optionally checks the legacy config file name if specified,
    then continues up the directory tree looking for the provided config file name.
    Returns the path to the first config file found.

    If no config file is found, returns None.

    The cutoff parameter limits the search depth, preventing detection of config file in higher-level directories during testing.
    """

    # Provided config file is in current directory.
    if (os.path.isfile(config_file_name)):
        return os.path.abspath(config_file_name)

    # Provided legacy config file is in current directory.
    if (legacy_config_file_name is not None):
        if (os.path.isfile(legacy_config_file_name)):
            return os.path.abspath(legacy_config_file_name)

    # Provided config file is found in an ancestor directory up to the root or cutoff limit.
    parent_dir = os.path.dirname(os.getcwd())
    return _get_ancestor_config_file_path(
        parent_dir,
        config_file_name = config_file_name,
        local_config_root_cutoff = local_config_root_cutoff,
    )

def _get_ancestor_config_file_path(
        current_directory: str,
        config_file_name: str,
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
        config_file_path = os.path.join(current_directory, config_file_name)
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

def set_cli_args(parser: argparse.ArgumentParser, extra_state: typing.Dict[str, typing.Any]) -> None:
    """
    Set common CLI arguments for configuration.
    """

    parser.add_argument('--config-global', dest = 'global_config_path',
        action = 'store', type = str, default = DEFAULT_GLOBAL_CONFIG_PATH,
        help = 'Override the default global config file path (default: %(default)s).',
    )

    parser.add_argument('--config-file', dest = 'config_paths',
        action = 'append', type = str, default = None,
        help = "Load config options from a JSON file. "
        + "When this flag is given multiple times files are applied in the order provided, and later files override earlier ones. "
        + "This will override options form both global and local configs."
    )

    parser.add_argument('--config', dest = 'config',
        action = 'append', type = str, default = None,
        help = "Provide additional options to a CLI command. "
        + "Specify configuration options as <key>=<value> pairs. "
        + "This will override options form all config files."
    )

def config_from_parsed_args(
        parser: argparse.ArgumentParser,
        args: argparse.Namespace,
        extra_state: typing.Dict[str, typing.Any]
    ) -> None:
    """
    Take in args from a parser that was passed to set_cli_args(),
    and gets the tired configurations with the appropriate parameters, and attaches it to args.
    """

    (config_dict, sources_dict) = get_tiered_config(
        global_config_path = args.global_config_path,
        cli_arguments = args,
        skip_keys = [
            'local',
            'show_origin',
            edq.core.config.CONFIG_PATHS_KEY,
            'global_config_path',
            'log_level',
            'quiet',
            'debug',
            'config',
        ]
    )

    setattr(args, "_config", config_dict)
    setattr(args, "_config_sources", sources_dict)
