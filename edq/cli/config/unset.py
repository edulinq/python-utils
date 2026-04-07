"""
Unset configuration options.

Does nothing if the file at the specified config location doesn't exist.
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
        args.scope_local,
        args.scope_global,
        args.scope_file,
    )

    if (not (edq.util.dirent.exists(out_path))):
        print(f"Config file does not exist: '{os.path.abspath(out_path)}'.")
        return 0

    edq.core.config.remove_options_in_config_file(out_path, args.config_to_unset)
    print(f"Unset config options from: '{os.path.abspath(out_path)}'.")

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

    parser.add_argument('config_to_unset', metavar = "KEY",
        action = 'store', nargs = '+', type = str,
        help = ("Configuration key to unset."),
    )

    edq.core.config.add_config_location_argument_group(parser)

if (__name__ == '__main__'):
    sys.exit(main())
