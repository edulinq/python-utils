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

    out_path = edq.core.config.resolve_config_location(
        args._config_info,
        args.write_local,
        args.write_global,
        args.write_file_path
    )

    edq.core.config.update_options_in_config_file(out_path, config_to_set)
    print(f"Wrote config options to: {os.path.abspath(out_path)}")

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
        help = ("Configuration option to be set."
            +  " Expected config format is <key>=<value>."),
    )

    group = parser.add_argument_group("config location options").add_mutually_exclusive_group()

    group.add_argument('--local',
        action = 'store_true', dest = 'write_local',
        help = ("Write config option(s) to the local config file if one exists."
            + " If no local config file is found, a new one will be created in the current directory."),
    )

    group.add_argument('--global',
        action = 'store_true', dest = 'write_global',
        help =  ("Write config option(s) to the global config file if one exists."
            +  f" If no global config file is found, a new one will be created at {edq.core.config.get_global_config_path()}"),
    )

    group.add_argument('--file', metavar = "<FILE>",
        action = 'store', type = str, default = None, dest = 'write_file_path',
        help = ("Write config option(s) to the specified config file if it exists."
            +  " If the given file doesn't exist, it will be created.")
    )

if (__name__ == '__main__'):
    sys.exit(main())
