import argparse
import sys

import edq.core.argparser

DESCRIPTION = "List current configuration options."

def run_cli(args: argparse.Namespace) -> int:
    """ Run the CLI. """

    config_list = []
    for (key, value) in args._config.items():
        config_str = f"{key}\t{value}"
        if (args.show_origin):
            config_source_obj = args._config_sources.get(key)
            config_str += f"\t{config_source_obj.path}"

        config_list.append(config_str)

    print("\n".join(config_list))
    return 0

def main() -> int:
    """ Get a parser, parse the args, and call run. """

    return run_cli(_get_parser().parse_args())

def _get_parser() -> edq.core.argparser.Parser:
    """ Get the parser and add addition flags. """

    parser = edq.core.argparser.get_default_parser(DESCRIPTION)

    parser.add_argument("--show-origin", dest = 'show_origin',
        action = 'store_true',
        help = "Display where each configuration's value was obtained from.",
    )

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
