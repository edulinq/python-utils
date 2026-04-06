"""
Update configuration options.

The file at the specified config location will be created if it doesn't exist.
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
        args.scope_local,
        args.scope_global,
        args.scope_file,
    )

    edq.core.config.update_options_in_config_file(out_path, config_to_set)
    print(f"Wrote config options to: '{os.path.abspath(out_path)}'.")

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

    edq.core.config.add_config_location_argument_group(parser)

if (__name__ == '__main__'):
    sys.exit(main())
