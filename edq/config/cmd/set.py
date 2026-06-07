"""
Update configuration options.

The file at the specified config location will be created if it doesn't exist.
"""

import argparse
import os
import typing

import edq.config.argparser
import edq.config.load
import edq.config.util

def run(args: argparse.Namespace) -> int:
    """ Run the target command and return the suggested exit status. """

    config_to_set: typing.Dict[str, str] = {}
    for config_option in args.config_to_set:
        (key, value) = edq.config.util.parse_string_config_option(config_option)
        config_to_set[key] = value

    out_path = edq.config.load.resolve_config_location(
        args._config_info,
        args.scope_local,
        args.scope_global,
        args.scope_file,
    )

    edq.config.util.update_options_in_config_file(out_path, config_to_set)
    print(f"Wrote config options to: '{os.path.abspath(out_path)}'.")

    return 0

def modify_parser(parser: argparse.ArgumentParser) -> None:
    """ Add this CLI's flags to the given parser. """

    parser.add_argument('config_to_set', metavar = "<KEY>=<VALUE>",
        action = 'store', nargs = '+', type = str,
        help = ("Configuration option to be set."
            +  " Expected config format is <key>=<value>."),
    )

    edq.config.argparser.add_config_location_argument_group(parser)
