"""
Set a configuration option.
"""

import argparse
import os
import sys
import typing

import edq.core.argparser
import edq.core.config
import edq.util.dirent
import edq.util.json

def run_cli(args: argparse.Namespace) -> int:
    """ Run the CLI. """

    if (not (args.set_is_local or args.set_is_global or (args.set_to_file_path is not None))):
        args.set_is_local = True

    if (args.set_is_local):
        local_config_path = args._config_params.get(edq.core.config.LOCAL_CONFIG_PATH_KEY)
        if (local_config_path is None):
            local_config_path = args._config_params.get(edq.core.config.FILENAME_KEY)
        edq.core.config.write_config_to_file(local_config_path, args.config_to_set)
    elif (args.set_is_global):
        global_config_path = args._config_params.get(edq.core.config.GLOBAL_CONFIG_PATH_KEY)
        edq.core.config.write_config_to_file(global_config_path, args.config_to_set)
    elif (args.set_to_file_path is not None):
        edq.core.config.write_config_to_file(args.set_to_file_path, args.config_to_set)

    return 0

def main() -> int:
    """ Get a parser, parse the args, and call run. """

    return run_cli(_get_parser().parse_args())

def _get_parser() -> argparse.ArgumentParser:
    """ Get a parser and add additional flags. """

    parser = edq.core.argparser.get_default_parser(__doc__.strip())
    modify_parser(parser)

    return parser

def modify_parser(parser: argparse.ArgumentParser) -> None:
    """ Add this CLI's flags to the given parser. """

    parser.add_argument('config_to_set', metavar = "<KEY>=<VALUE>",
        action = 'store', nargs = '+', type = str,
        help = ('Configuration option to be set.'
            +  " Expected config format is <key>=<value>."),
    )

    config_file_locations = parser.add_argument_group("set config options")
    group = config_file_locations.add_mutually_exclusive_group()

    group.add_argument('--local',
        action = 'store_true', dest = 'set_is_local',
        help = ('Set the configuration option in a local config file if one exists.'
        + ' If no local config file is found, a new one will be created in the current directory.'),
    )

    group.add_argument('--global',
        action = 'store_true', dest = 'set_is_global',
        help =  ('Set the configuration option in the global config file if it exists.'
        +  " If it doesn't exist, it will be created."
        +  " Use '--config-global' to view or change the global config file location."),
    )

    group.add_argument('--file', metavar = "<FILE>",
        action = 'store', type = str, default = None, dest = 'set_to_file_path',
        help = ('Set the config option in a specified config file.'
            +  " If the given file path doesn't exist, it will be created.")
    )

if (__name__ == '__main__'):
    sys.exit(main())
