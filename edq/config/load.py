import argparse
import os
import typing

import platformdirs

import edq.config.app
import edq.config.constants
import edq.config.settings
import edq.config.util
import edq.util.dirent
import edq.util.json
import edq.util.serial

class ConfigSource(edq.util.serial.DictConverter):
    """ A class for storing config source information. """

    def __init__(self, label: str, path: typing.Union[str, None] = None) -> None:
        self.label: str = label
        """ The label identifying the config (see edq.config.constants.CONFIG_SOURCE_* constants). """

        self.path: typing.Union[str, None] = path
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
            application_config: typing.Union[edq.config.app.BaseApplicationConfig, None] = None,
            ) -> None:
        self.config_filename: str = config_filename
        """ Config filename searched for. """

        self.local_config_path: str = local_config_path
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

        if (application_config is None):
            application_config = edq.config.app.BaseApplicationConfig()

        self.application_config: edq.config.app.BaseApplicationConfig = application_config
        """ The config typed for the specific application. """

def get_global_config_path() -> str:
    """ Get the path for the global config file. """

    return platformdirs.user_config_dir(edq.config.settings.get_config_filename())

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
        local_config_path = os.path.abspath(edq.config.settings.get_config_filename())

    _load_config_file(local_config_path, raw_config, sources, edq.config.constants.CONFIG_SOURCE_LOCAL)

    # Check for environmental variables.
    _load_env_variables(raw_config, sources)

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

    # Create an application config with all config we have seen.
    all_config = cli_arguments.copy()
    all_config.update(raw_config)

    if (serialization_context is None):
        serialization_context = edq.util.serial.SerializationContext()
    else:
        serialization_context = serialization_context.copy()

    encryption_key: typing.Union[str, None] = all_config.get(
            edq.config.constants.CONFIG_ENCRYPTION_KEY,
            edq.config.settings.get_default_encryption_key())
    if (encryption_key is None):
        encryption_key = edq.config.settings.get_default_encryption_key()

    all_config[edq.config.constants.CONFIG_ENCRYPTION_KEY] = encryption_key
    serialization_context.key = encryption_key

    application_config = edq.config.settings.get_application_config_class().from_dict(
        all_config,
        context = serialization_context,
    )

    return TieredConfigInfo(
        edq.config.settings.get_config_filename(),
        local_config_path,
        global_config_path,
        raw_config,
        sources,
        application_config = application_config,
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

def _load_env_variables(
        config: typing.Dict[str, typing.Any],
        sources: typing.Dict[str, ConfigSource],
        ) -> None:
    """
    Load config from environmental variables.
    Any variable with a matching prefix will have the prefix removed and lower-cased.
    """

    prefix = edq.config.settings.get_env_prefix()
    for (key, value) in os.environ.items():
        if (not key.startswith(prefix)):
            continue

        key = key.removeprefix(prefix).lower()

        config[key] = value
        sources[key] = ConfigSource(label = edq.config.constants.CONFIG_SOURCE_ENV)

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

    config_filename = edq.config.settings.get_config_filename()
    legacy_config_filename = edq.config.settings.get_legacy_config_filename()

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
        config_file_path = os.path.join(current_directory, edq.config.settings.get_config_filename())
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
