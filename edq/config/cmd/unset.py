"""
Unset configuration options.

Does nothing if the file at the specified config location doesn't exist.
"""

import argparse
import os

import edq.config.argparser
import edq.config.load
import edq.config.util

def run(args: argparse.Namespace) -> int:
    """ Run the target command and return the suggested exit status. """

    out_path = edq.config.load.resolve_config_location(
        args._config_info,
        args.scope_local,
        args.scope_global,
        args.scope_file,
    )

    if (not (edq.util.dirent.exists(out_path))):
        print(f"Config file does not exist: '{os.path.abspath(out_path)}'.")
        return 0

    edq.config.util.remove_options_in_config_file(out_path, args.config_to_unset)
    print(f"Unset config options from: '{os.path.abspath(out_path)}'.")

    return 0

def modify_parser(parser: argparse.ArgumentParser) -> None:
    """ Add this CLI's flags to the given parser. """

    parser.add_argument('config_to_unset', metavar = "KEY",
        action = 'store', nargs = '+', type = str,
        help = ("Configuration key to unset."),
    )

    edq.config.argparser.add_config_location_argument_group(parser)
