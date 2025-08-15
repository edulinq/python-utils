import argparse

import os
import platformdirs

import edq.util.dirent
import edq.util.json

CONFIG_PATHS_KEY = 'config_paths'
LEGACY_CONFIG_FILENAME = 'config.json'
DEFAULT_CONFIG_FILENAME = 'autograder.json'
DEFAULT_GLOBAL_CONFIG_PATH = platformdirs.user_config_dir(DEFAULT_CONFIG_FILENAME)
CONFIG_TYPE_DELIMITER = "::"

def get_tiered_config(
        cli_arguments,
        skip_keys = [CONFIG_PATHS_KEY],
        global_config_path = DEFAULT_GLOBAL_CONFIG_PATH,
        local_config_root_cutoff = None):
    """
    Get all the tiered configuration options (from files and CLI).
    If |show_sources| is True, then an addition dict will be returned that shows each key,
    and where that key came from.
    """

    config = {}
    sources = {}

    if (isinstance(cli_arguments, argparse.Namespace)):
        cli_arguments = vars(cli_arguments)

    # Check the global user config file.
    if (os.path.isfile(global_config_path)):
        _load_config_file(global_config_path, config, sources, "<global config file>")

    # Check the local user config file.
    local_config_path = _get_local_config_path(local_config_root_cutoff = local_config_root_cutoff)
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
        sources[key] = "<cli argument>"

    return config, sources

def _load_config_file(config_path, config, sources, source_label):
    with open(config_path, 'r') as file:
        for (key, value) in edq.util.json.load(file).items():
            config[key] = value
            sources[key] = f"{source_label}{CONFIG_TYPE_DELIMITER}{os.path.abspath(config_path)}"

def _get_local_config_path(local_config_root_cutoff = None):
    """
    Searches for a configuration file in a hierarchical order,
    starting with DEFAULT_CONFIG_FILENAME, then LEGACY_CONFIG_FILENAME,
    and continuing up the directory tree looking for DEFAULT_CONFIG_FILENAME.
    Returns the path to the first configuration file found.

    If no configuration file is found, returns None.
    The cutoff limits config search depth.
    This helps to prevent detection of a config file in higher directories during testing.
    """

    # The case where DEFAULT_CONFIG_FILENAME file in current directory.
    if (os.path.isfile(DEFAULT_CONFIG_FILENAME)):
        return os.path.abspath(DEFAULT_CONFIG_FILENAME)

    # The case where LEGACY_CONFIG_FILENAME file in current directory.
    if (os.path.isfile(LEGACY_CONFIG_FILENAME)):
        return os.path.abspath(LEGACY_CONFIG_FILENAME)

    #  The case where a DEFAULT_CONFIG_FILENAME file located in any ancestor directory on the path to root.
    parent_dir = os.path.dirname(os.getcwd())
    return _get_ancestor_config_file_path(
        parent_dir,
        local_config_root_cutoff = local_config_root_cutoff
    )

def _get_ancestor_config_file_path(
        current_directory,
        config_file = DEFAULT_CONFIG_FILENAME,
        local_config_root_cutoff = None):
    """
    Search through the parent directories (until root or a given cutoff directory(inclusive)) for a configuration file.
    Stops at the first occurrence of the specified config file (default: DEFAULT_CONFIG_FILENAME) along the path to root.
    Returns the path if a configuration file is found.
    Otherwise, returns None.
    """

    current_directory = os.path.abspath(current_directory)
    if (local_config_root_cutoff is not None):
        local_config_root_cutoff = os.path.abspath(local_config_root_cutoff)

    for _ in range(edq.util.dirent.DEPTH_LIMIT):
        config_file_path = os.path.join(current_directory, config_file)
        if (os.path.isfile(config_file_path)):
            return config_file_path

        if (local_config_root_cutoff == current_directory):
            break

        parent_dir = os.path.dirname(current_directory)
        if (parent_dir == current_directory):
            break

        current_directory = parent_dir

    return None
