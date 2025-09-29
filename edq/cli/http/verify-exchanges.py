# pylint: disable=invalid-name

"""
Verify that exchanges sent to a given server have the same response.
"""

import argparse
import glob
import logging
import os
import sys
import typing
import unittest

import edq.core.argparser
import edq.testing.unittest
import edq.util.net

class ExchangeVerification(edq.testing.unittest.BaseTest):
    """ Verify that exchanges match their content. """

def run_cli(args: argparse.Namespace) -> int:
    """ Run the CLI. """

    paths = _collect_exchange_paths(args.paths)

    _attach_tests(paths, args.server)

    runner = unittest.TextTestRunner(verbosity = 2)
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(ExchangeVerification)
    results = runner.run(tests)

    return len(results.errors) + len(results.failures)

def _attach_tests(
        paths: typing.List[str],
        server: str,
        extension: str = edq.util.net.DEFAULT_HTTP_EXCHANGE_EXTENSION,
        ) -> None:
    """ Create tests for each path and attach them to the ExchangeVerification class. """

    common_prefix = os.path.commonprefix(paths)

    for path in paths:
        name = path.replace(common_prefix, '').replace(extension, '')
        test_name = f"test_verify_exchange__{name}"

        setattr(ExchangeVerification, test_name, _get_test_method(path, server))

def _get_test_method(path: str, server: str,
        match_options: typing.Union[typing.Dict[str, typing.Any], None] = None,
        ) -> typing.Callable:
    """ Create a test method for the given path. """

    if (match_options is None):
        match_options = {}

    def __method(self: edq.testing.unittest.BaseTest) -> None:
        exchange = edq.util.net.HTTPExchange.from_path(path)
        response = exchange.make_request(server, raise_for_status = False, **match_options)

        match, hint = exchange.match_response(response, **match_options)
        if (not match):
            raise AssertionError(f"Exchange does not match: '{hint}'.")

    return __method

def _collect_exchange_paths(
        paths: typing.List[str],
        extension: str = edq.util.net.DEFAULT_HTTP_EXCHANGE_EXTENSION,
        ) -> typing.List[str]:
    """ Collect exchange files by matching extensions and descending dirs. """

    final_paths = []

    for path in paths:
        path = os.path.abspath(path)

        if (os.path.isfile(path)):
            if (path.endswith(extension)):
                final_paths.append(path)
            else:
                logging.warning("Path does not look like an exchange file: '%s'.", path)
        else:
            dirent_paths = glob.glob(os.path.join(path, "**", f"*{extension}"), recursive = True)
            for dirent_path in dirent_paths:
                final_paths.append(dirent_path)

    final_paths.sort()
    return final_paths

def main() -> int:
    """ Get a parser, parse the args, and call run. """
    return run_cli(_get_parser().parse_args())

def _get_parser() -> argparse.ArgumentParser:
    """ Get the parser. """

    parser = edq.core.argparser.get_default_parser(__doc__.strip())

    parser.add_argument('server', metavar = 'SERVER',
        action = 'store', type = str, default = None,
        help = 'Address of the server to send exchanges to.')

    parser.add_argument('paths', metavar = 'PATH',
        type = str, nargs = '+',
        help = 'Path to exchange files or dirs (which will be recursively searched for all exchange files).')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
