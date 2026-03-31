"""
Unset configuration options.
"""

import argparse
import os
import sys

import edq.core.argparser
import edq.core.config

def run_cli(args: argparse.Namespace) -> int:
    """ Run the CLI. """

    out_path = edq.core.config.resolve_config_location(
        args._config_info,
        args.unset_from_local,
        args.unset_from_global,
        args.unset_from_file_path
    )

    if (out_path is None):
        raise ValueError("Failed to unset from a unknown config location (e.g., not local or global).")

    if (not (edq.util.dirent.exists(out_path))):
        return 0

    edq.core.config.remove_options_in_config_file(out_path, args.config_to_unset)
    print(f"Unset config options from: {os.path.abspath(out_path)}")

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

    parser.add_argument('config_to_unset', metavar = "<KEY>",
        action = 'store', nargs = '+', type = str,
        help = ("Configuration option to be unset."
            +  " Expected config format is <key>."),
    )

    group = parser.add_argument_group("config location options").add_mutually_exclusive_group()

    group.add_argument('--local',
        action = 'store_true', dest = 'unset_from_local',
        help = ("Unset config option(s) from the local config file if one exists."
            + " If no local config file is found, does nothing."),
    )

    group.add_argument('--global',
        action = 'store_true', dest = 'unset_from_global',
        help =  ("Unset config option(s) from the global config file if one exists."
            +  " If no global config file is found, does nothing."),
    )

    group.add_argument('--file', metavar = "<FILE>",
        action = 'store', type = str, default = None, dest = 'unset_from_file_path',
        help = ("Unset config option(s) from the specified config file if it exists."
            +  " If the given file doesn't exist, does nothing.")
    )

if (__name__ == '__main__'):
    sys.exit(main())
