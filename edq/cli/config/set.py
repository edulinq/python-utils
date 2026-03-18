"""
Update configuration options.
"""

import argparse
import os
import sys
import typing

import edq.core.argparser
import edq.core.config

def run_cli(args: argparse.Namespace) -> int:
    """ Run the CLI. """

    config_to_set: typing.Dict[str, str] = {}
    for config_option in args.config_to_set:
        (key, value) = edq.core.config.parse_string_config_option(config_option)
        config_to_set[key] = value

    config_info = args._config_info

    # Default to the local configuration if no configuration type is specified.
    if (not (args.write_local or args.write_global or (args.write_file_path is not None))):
        args.write_local = True

    path_to_write_config = None
    if (args.write_local):
        local_config_path = config_info.local_config_path

        # If no local config file was found on the path to root.
        # Set local config path to the default config filename in the current directory.
        if (local_config_path is None):
            local_config_path = config_info.config_filename

        path_to_write_config = os.path.join(os.getcwd(), local_config_path)
    elif (args.write_global):
        path_to_write_config = config_info.global_config_path
    elif (args.write_file_path is not None):
        path_to_write_config = args.write_file_path
    else:
        raise ValueError("Trying to write to a unknown config scope.")

    edq.core.config.update_config_file(path_to_write_config, config_to_set)
    print(f"Wrote config options to: {path_to_write_config}")

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
            +  ' Expected config format is <key>=<value>.'),
    )

    group = parser.add_argument_group("config scope options").add_mutually_exclusive_group()

    group.add_argument('--local',
        action = 'store_true', dest = 'write_local',
        help = ('Write config option(s) to the local config file if one exists.'
            + ' If no local config file is found, a new one will be created in the current directory.'),
    )

    group.add_argument('--global',
        action = 'store_true', dest = 'write_global',
        help =  ('Write config option(s) to the global config file if it exists.'
            +  " If it doesn't exist, a new one will be created."),
    )

    group.add_argument('--file', metavar = "<FILE>",
        action = 'store', type = str, default = None, dest = 'write_file_path',
        help = ('Write config option(s) to the specified config file.'
            +  " If the given file doesn't exist, it will be created.")
    )

if (__name__ == '__main__'):
    sys.exit(main())
