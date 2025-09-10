"""
List current configuration options.
"""

import argparse
import sys

import edq.core.argparser

def run_cli(args: argparse.Namespace) -> int:
    """ Run the CLI. """

    config_list = []
    for (key, value) in args._config.items():
        config = [key, value]
        if (args.show_origin):
            config_source_obj = args._config_sources.get(key)

            if (config_source_obj.path is None):
                config.append(config_source_obj.label)
            else:
                config.append(config_source_obj.path)

        config_list.append("\t".join(config))

    if (not args.skip_header):
        config_list.insert(0, "Key\tValue")
        if (args.show_origin):
            config_list[0] = config_list[0] + "\tOrigin"

    print("\n".join(config_list))
    return 0

def main() -> int:
    """ Get a parser, parse the args, and call run. """

    return run_cli(_get_parser().parse_args())

def _get_parser() -> edq.core.argparser.Parser:
    """ Get a parser and add addition flags. """

    parser = edq.core.argparser.get_default_parser(__doc__.strip())

    parser.add_argument("--show-origin", dest = 'show_origin',
        action = 'store_true',
        help = "Display where each configuration's value was obtained from.",
    )

    parser.add_argument("--skip-header", dest = 'skip_header',
        action = 'store_true',
        help = "Skip headers when displaying configs.",
    )

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
