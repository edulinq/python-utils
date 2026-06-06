import argparse
import os
import typing

import platformdirs

import edq.config.app
import edq.config.constants
import edq.config.util
import edq.util.dirent
import edq.util.json
import edq.util.serial

_config_filename: str = edq.config.constants.DEFAULT_CONFIG_FILENAME  # pylint: disable=invalid-name
_legacy_config_filename: typing.Union[str, None] = None  # pylint: disable=invalid-name

class ConfigSource(edq.util.serial.DictConverter):
    """ A class for storing config source information. """

    def __init__(self, label: str, path: typing.Union[str, None] = None) -> None:
        self.label = label
        """ The label identifying the config (see edq.config.constants.CONFIG_SOURCE_* constants). """

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
            raw_config: typing.Dict[str, edq.util.serial.PODType],
            sources: typing.Dict[str, ConfigSource],
            config_class: typing.Union[typing.Type[edq.config.app.BaseApplicationConfig], None] = None,
            serialization_context: typing.Union[edq.util.serial.SerializationContext, None] = None,
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

        self.raw_config: typing.Dict[str, edq.util.serial.PODType] = raw_config
        """ Key-value configurations. """

        self.sources: typing.Dict[str, ConfigSource] = sources
        """ Where configs came from. """

        # Note that we set the default value here instead of in the arguments because of a bug in mypy with defaults on generic types:
        # https://github.com/python/mypy/issues/3737.
        if (config_class is None):
            config_class = edq.config.app.BaseApplicationConfig

        self.application_config: edq.config.app.BaseApplicationConfig = config_class.from_dict(
            raw_config.copy(),
            context = serialization_context,
        )
        """ The config typed for the specific application. """

def set_config_filename(filename: str) -> None:
    """ Sets the config filename. """

    global _config_filename  # pylint: disable=global-statement
    _config_filename = filename

def set_legacy_config_filename(legacy_filename: typing.Union[str, None]) -> None:
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

def resolve_config_location(
        config_info: TieredConfigInfo,
        is_local: bool,
        is_global: bool,
        config_file_path: typing.Union[str, None],
        ) -> str:
    """
    Resolve the config location from the given scope information.
    Defaults to local config location if unspecified.
    Raises an exception if an unknown config scope is given.
    """

    # Default to the local configuration if no configuration type is specified.
    if ((not is_local) and (not is_global) and (config_file_path is None)):
        is_local = True

    if (config_file_path is not None):
        return config_file_path

    if (is_global):
        return config_info.global_config_path

    if (is_local):
        local_config_path = config_info.local_config_path

        # Fall back to the default config file name if no local config exists.
        if (local_config_path is None):
            local_config_path = config_info.config_filename

        return local_config_path

    raise ValueError("Unknown config location (e.g., not local or global).")

def get_tiered_config(
        cli_arguments: typing.Union[dict, argparse.Namespace, None] = None,
        local_config_root_cutoff: typing.Union[str, None] = None,
        config_class: typing.Union[typing.Type[edq.config.app.BaseApplicationConfig], None] = None,
        serialization_context: typing.Union[edq.util.serial.SerializationContext, None] = None,
        ) -> TieredConfigInfo:
    """
    Load all configuration options from files and command-line arguments.
    """

    if (cli_arguments is None):
        cli_arguments = {}

    raw_config: typing.Dict[str, edq.util.serial.PODType] = {}
    sources: typing.Dict[str, ConfigSource] = {}

    # Ensure CLI arguments are always a dict,
    # even if provided as argparse.Namespace.
    if (isinstance(cli_arguments, argparse.Namespace)):
        cli_arguments = vars(cli_arguments)

    # Load the global user config file.
    global_config_path = cli_arguments.get(edq.config.constants.GLOBAL_CONFIG_KEY, get_global_config_path())
    _load_config_file(global_config_path, raw_config, sources, edq.config.constants.CONFIG_SOURCE_GLOBAL)

    # Get and load local user config path.
    local_config_path = _get_local_config_path(
        local_config_root_cutoff = local_config_root_cutoff,
    )

    if (local_config_path is None):
        local_config_path = os.path.abspath(get_config_filename())

    _load_config_file(local_config_path, raw_config, sources, edq.config.constants.CONFIG_SOURCE_LOCAL)

    # Check the config file specified on the command-line.
    config_paths = cli_arguments.get(edq.config.constants.CONFIG_PATHS_KEY, [])
    for path in config_paths:
        if (not os.path.exists(path)):
            raise FileNotFoundError(f"Specified config file does not exist: '{path}'.")

        _load_config_file(path, raw_config, sources, edq.config.constants.CONFIG_SOURCE_CLI_FILE)

    # Check the command-line config options.
    cli_configs = cli_arguments.get(edq.config.constants.CONFIG_OPTIONS_KEY, [])
    for cli_config_option in cli_configs:
        (key, value) = edq.config.util.parse_string_config_option(cli_config_option)

        raw_config[key] = value
        sources[key] = ConfigSource(label = edq.config.constants.CONFIG_SOURCE_CLI)

    # Finally, ignore any configs that is specified from CLI command.
    cli_ignore_configs = cli_arguments.get(edq.config.constants.IGNORE_CONFIG_OPTIONS_KEY, [])
    for ignore_config in cli_ignore_configs:
        raw_config.pop(ignore_config, None)
        sources.pop(ignore_config, None)

    return TieredConfigInfo(
        get_config_filename(),
        local_config_path,
        global_config_path,
        raw_config,
        sources,
        config_class = config_class,
        serialization_context = serialization_context,
    )

def _load_config_file(
        config_path: str,
        config: typing.Dict[str, typing.Any],
        sources: typing.Dict[str, ConfigSource],
        source_label: str,
        ) -> None:
    """
    Loads config variables and the source from the given config JSON file.
    If the given config JSON file doesn't exit loads nothing.
    """

    if (not edq.util.dirent.exists(config_path)):
        return

    if (os.path.isdir(config_path)):
        raise IsADirectoryError(f"Failed to read config file, expected a file but got a directory at '{config_path}'.")

    config_path = os.path.abspath(config_path)
    for (key, value) in edq.util.json.load_path(config_path).items():
        key = edq.config.util.validate_config_key(key, value)

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
