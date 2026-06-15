"""
Update configuration options.

The file at the specified config location will be created if it doesn't exist.
"""

import argparse
import os
import typing

import edq.config.argparser
import edq.config.constants
import edq.config.load
import edq.config.settings
import edq.config.source
import edq.config.util

def run(args: argparse.Namespace) -> int:
    """ Run the target command and return the suggested exit status. """

    path = _get_target_path(args)
    if (path is None):
        print("Unable to determine where to write the config to. Consider supplying a file on the command-line.")
        return 1

    path = os.path.abspath(path)

    config_to_set: typing.Dict[str, str] = {}
    for config_option in args.config_to_set:
        (key, value) = edq.config.util.parse_string_config_option(config_option)
        config_to_set[key] = value

    edq.config.util.update_options_in_config_file(path, config_to_set)
    print(f"Wrote {len(config_to_set)} config option(s) to: '{path}'.")

    return 0

def modify_parser(parser: argparse.ArgumentParser) -> None:
    """ Add this CLI's flags to the given parser. """

    parser.add_argument('config_to_set', metavar = "<KEY>=<VALUE>",
        action = 'store', nargs = '+', type = str,
        help = "Configuration option to be set. Expected config format is <key>=<value>.",
    )

    edq.config.argparser.add_config_location_argument_group(parser)

def _get_target_path(args: argparse.Namespace) -> typing.Union[str, None]:
    """
    Decide where to write the given config to.
    If no source is explicitly specified, write to the first local config.
    If no config location can be determined, return None.
    """

    if (args.scope_file is not None):
        return args.scope_file

    # Use a local path if no source is specified or if local is explicitly specified.
    use_local = (args.scope_local or (not args.scope_global))

    for spec in edq.config.settings.get_load_order():
        # Skip specs that do not have a path.
        if (not isinstance(spec, edq.config.source.AbstractPathSpec)):
            continue

        if (use_local and isinstance(spec, edq.config.source.LocalSpec)):
            return spec.resolve_path()

        if (args.scope_global and isinstance(spec, edq.config.source.GlobalSpec)):
            return spec.resolve_path(getattr(args, edq.config.constants.GLOBAL_CONFIG_KEY, None))

    return None
