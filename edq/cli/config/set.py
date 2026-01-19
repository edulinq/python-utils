"""
Set a configuration option.
"""

import argparse
import sys
import typing

import edq.core.argparser
import edq.core.config

def run_cli(args: argparse.Namespace) -> int:
    """ Run the CLI. """

    config: typing.Dict[str, str] = {}
    for config_option in args.config_to_set:
        (key, value) = edq.core.config._parse_cli_config_option(config_option)
        config[key] = value

    # Defaults to the local configuration if no configuration type is specified.
    if (not (args.write_local or args.write_global or (args.write_file_path is not None))):
        args.write_local = True

    if (args.write_local):
        local_config_path = args._config_params[edq.core.config.LOCAL_CONFIG_PATH_KEY]
        if (local_config_path is None):
            local_config_path = args._config_params[edq.core.config.FILENAME_KEY]
        edq.core.config.write_config_to_file(local_config_path, config)
    elif (args.write_global):
        global_config_path = args._config_params[edq.core.config.GLOBAL_CONFIG_PATH_KEY]
        edq.core.config.write_config_to_file(global_config_path, config)
    elif (args.write_file_path is not None):
        edq.core.config.write_config_to_file(args.write_file_path, config)

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

    group = parser.add_argument_group("set config options").add_mutually_exclusive_group()

    group.add_argument('--local',
        action = 'store_true', dest = 'write_local',
        help = ('Write config option(s) to the local config file if one exists.'
        + ' If no local config file is found, a new one will be created in the current directory.'),
    )

    group.add_argument('--global',
        action = 'store_true', dest = 'write_global',
        help =  ('Write config option(s) to the global config file if it exists.'
        +  " If it doesn't exist, it will be created."
        +  " Use '--config-global' to view or change the global config file location."),
    )

    group.add_argument('--file', metavar = "<FILE>",
        action = 'store', type = str, default = None, dest = 'write_file_path',
        help = ('Write config option(s) to the specified config file.'
            +  " If the given file path doesn't exist, it will be created.")
    )

if (__name__ == '__main__'):
    sys.exit(main())
