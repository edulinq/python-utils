import argparse
import os
import typing

import platformdirs

import edq.util.dirent
import edq.util.json

CONFIG_PATHS_KEY: str = 'config_paths'
DEFAULT_CONFIG_FILENAME = "edq-config.json"

class ConfigSource:
    """ A class for storing config source in a structured way. """

    def __init__(self, label, path = None):
        self.label = label
        self.path = path

    def to_dict(self):
        """ Return a dict that can be used to represent this object. """

        return vars(self)

    def __eq__(self, other: object) -> bool:
        """ Check for equality. This check uses to_dict() and compares the results. """

        # Note the hard type check (done so we can keep this method general).
        if (type(self) != type(other)):  # pylint: disable=unidiomatic-typecheck
            return False

        return bool(self.to_dict() == other.to_dict())  # type: ignore[attr-defined]

    def __str__(self) -> str:
        return f"label is {self.label}, path is {self.path}"

    def __repr__(self) -> str:
        return f"ConfigSource({self.to_dict()!r})"

def get_tiered_config(
        config_file_name: str = DEFAULT_CONFIG_FILENAME ,
        legacy_config_file_name: typing.Union[str, None] = None,
        global_config_path: typing.Union[str, None] = None,
        skip_keys: typing.Union[list, None] = None,
        cli_arguments: typing.Union[dict, argparse.Namespace, None] = None,
        local_config_root_cutoff: typing.Union[str, None] = None,
        )-> typing.Tuple[typing.Dict[str, str], typing.Dict[str, ConfigSource]]:
    """
    Get all the tiered configuration options (from files and CLI).
    If |show_sources| is True, then an addition dict will be returned that shows each key,
    and where that key came from.
    """

    if (global_config_path is None):
        global_config_path = platformdirs.user_config_dir(config_file_name)

    if (cli_arguments is None):
        cli_arguments = {}

    if (skip_keys is None):
        skip_keys = [CONFIG_PATHS_KEY]

    config: typing.Dict[str, str] = {}
    sources: typing.Dict[str, ConfigSource] = {}

    if (isinstance(cli_arguments, argparse.Namespace)):
        cli_arguments = vars(cli_arguments)

    # Check the global user config file.
    if (os.path.isfile(global_config_path)):
        _load_config_file(global_config_path, config, sources, "<global config file>")

    # Check the local user config file.
    local_config_path = _get_local_config_path(
        config_file_name = config_file_name,
        legacy_config_file_name = legacy_config_file_name,
        local_config_root_cutoff = local_config_root_cutoff
    )

    if (local_config_path is not None):
        _load_config_file(local_config_path, config, sources, "<local config file>")

    # Check the config file specified on the command-line.
    config_paths = cli_arguments.get(CONFIG_PATHS_KEY, [])
    if (config_paths is not None):
        for path in config_paths:
            _load_config_file(path, config, sources, "<cli config file>")

    # Finally, any command-line options.
    for (key, value) in cli_arguments.items():
        if (key in skip_keys):
            continue

        if ((value is None) or (value == '')):
            continue

        config[key] = value
        sources[key] = ConfigSource(label = "<cli argument>")

    return config, sources

def _load_config_file(
        config_path: str,
        config: typing.Dict[str, str],
        sources: typing.Dict[str, ConfigSource],
        source_label: str
        )-> None:
    """ Loads configs and the source from the given config JSON file. """

    for (key, value) in edq.util.json.load_path(config_path).items():
        config[key] = value
        sources[key] = ConfigSource(label = source_label, path = os.path.abspath(config_path))

def _get_local_config_path(
        config_file_name: str,
        legacy_config_file_name: typing.Union[str, None] = None,
        local_config_root_cutoff: typing.Union[str, None] = None
    ) -> typing.Union[str, None]:
    """
    Searches for a config file in hierarchical order.
    Begins with the provided config file name,
    optionally checks the legacy config file name if specified,
    then continues up the directory tree looking for the provided config file name.
    Returns the path to the first config file found.

    If no config file is found, returns None.

    The cutoff parameter limits the search depth, preventing detection of
    config file in higher-level directories during testing.
    """

    # The case where provided config file in current directory.
    if (os.path.isfile(config_file_name)):
        return os.path.abspath(config_file_name)

    # The case where provided legacy config file in current directory.
    if (legacy_config_file_name is not None):
        if (os.path.isfile(legacy_config_file_name )):
            return os.path.abspath(legacy_config_file_name )

    #  The case where a provided config file located in any ancestor directory on the path to root.
    parent_dir = os.path.dirname(os.getcwd())
    return _get_ancestor_config_file_path(
        parent_dir,
        config_file_name = config_file_name,
        local_config_root_cutoff = local_config_root_cutoff
    )

def _get_ancestor_config_file_path(
        current_directory: str,
        config_file_name: str,
        local_config_root_cutoff: typing.Union[str, None] = None
        )-> typing.Union[str, None]:
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

        if (local_config_root_cutoff == current_directory):
            break

        parent_dir = os.path.dirname(current_directory)
        if (parent_dir == current_directory):
            break

        current_directory = parent_dir

    return None
