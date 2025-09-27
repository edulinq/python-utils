#  # pylint: disable=invalid-name

"""
Start an HTTP test server with the specified exchanges.
"""

import argparse
import os
import sys

import edq.core.argparser
import edq.testing.httpserver

def run_cli(args: argparse.Namespace) -> int:
    """ Run the CLI. """

    server = edq.testing.httpserver.HTTPTestServer(
            port = args.port,
            verbose = True,
            raise_on_404 = False,
    )

    for path in args.paths:
        path = os.path.abspath(path)

        if (os.path.isfile(path)):
            server.load_exchange(path)
        else:
            server.load_exchanges_dir(path)

    server.start_and_wait()

    return 0

def main() -> int:
    """ Get a parser, parse the args, and call run. """
    return run_cli(_get_parser().parse_args())

def _get_parser() -> edq.core.argparser.Parser:
    """ Get the parser. """

    parser = edq.core.argparser.get_default_parser(__doc__.strip())

    parser.add_argument('paths', metavar = 'PATH',
        type = str, nargs = '+',
        help = 'Path to exchange files or dirs (which will be recursively searched for all JSON files).')

    parser.add_argument('--port', dest = 'port',
        action = 'store', type = int, default = None,
        help = 'The port to run this test server on. If not set, a random open port will be chosen.')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
