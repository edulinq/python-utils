"""
Set a configuration option.
"""

import argparse
import sys
import typing

import edq.core.argparser
import edq.core.config
import edq.util.dirent
import edq.util.json

def write_configs_to_file(file_path: str, configs_to_write: typing.List[str]) -> None:
    """ Write configs to a specified file path. Create the path if it do not exist. """

    if (not (edq.util.dirent.exists(file_path))):
        edq.util.json.dump_path({}, file_path)

    config = edq.util.json.load_path(file_path)

    for config_option in  configs_to_write:
        if ("=" not in config_option):
            raise ValueError(
                f"Invalid configuration option '{config_option}'."
                + " Configuration options must be provided in the format `<key>=<value>` when passed via the CLI.")

        (key, value) = config_option.split("=", maxsplit = 1)

        key = key.strip()
        if (key == ""):
            raise ValueError(f"Found an empty configuration option key associated with the value '{value}'.")

        config[key] = value

    edq.util.json.dump_path(config, file_path, indent = 4)

def run_cli(args: argparse.Namespace) -> int:
    """ Run the CLI. """

    if (not (args.write_to_local or args.write_to_global or (args.file_to_write is not None))):
        args.write_to_local = True

    if (args.write_to_local):
        local_config_path = args._config_params.get(edq.core.config.LOCAL_CONFIG_PATH_KEY)
        if (local_config_path is None):
            local_config_path = args._config_params.get(edq.core.config.FILENAME_KEY)
        write_configs_to_file(local_config_path, args.config_to_set)
    elif (args.write_to_global):
        global_config_path = args._config_params.get(edq.core.config.GLOBAL_CONFIG_PATH_KEY)
        write_configs_to_file(global_config_path, args.config_to_set)
    elif (args.file_to_write is not None):
        write_configs_to_file(args.file_to_write, args.config_to_set)

    return 0

def main() -> int:
    """ Get a parser, parse the args, and call run. """

    return run_cli(_get_parser().parse_args())

def _get_parser() -> argparse.ArgumentParser:
    """ Get a parser and add addition flags. """

    parser = edq.core.argparser.get_default_parser(__doc__.strip())
    modify_parser(parser)

    return parser

def modify_parser(parser: argparse.ArgumentParser) -> None:
    """ Add this CLI's flags to the given parser. """

    parser.add_argument('config_to_set', metavar = "<KEY>=<VALUE>",
        action = 'store', nargs = '+', type = str,
        help = 'Configuration option to be set. Expected config format is <key>=<value>.',
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument('--local',
        action = 'store_true', dest = 'write_to_local',
        help = 'Sets the variable in local config file.',
    )

    group.add_argument('--global',
        action = 'store_true', dest = 'write_to_global',
        help = 'Sets the variable in global config file.',
    )

    group.add_argument('--file',
        action = 'store', type = str, default = None, dest = 'file_to_write',
        help = 'Sets the variable in a specified config file.',
    )

if (__name__ == '__main__'):
    sys.exit(main())
