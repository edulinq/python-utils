import argparse
import typing

import edq.net.exchange
import edq.net.request

def set_cli_args(parser: argparse.ArgumentParser, extra_state: typing.Dict[str, typing.Any]) -> None:
    """
    Set common CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    parser.add_argument('--http-exchanges-out-dir', dest = 'http_exchanges_out_dir',
        action = 'store', type = str, default = None,
        help = 'If set, write all outgoing HTTP requests as exchanges to this directory.')

    parser.add_argument('--http-exchanges-clean-func', dest = 'http_exchanges_clean_func',
        action = 'store', type = str, default = None,
        help = 'If set, default all created exchanges to this modifier function.')

    parser.add_argument('--http-exchanges-finalize-func', dest = 'http_exchanges_finalize_func',
        action = 'store', type = str, default = None,
        help = 'If set, default all created exchanges to this finalize.')

    parser.add_argument('--https-no-verify', dest = 'https_no_verify',
        action = 'store_true', default = False,
        help = 'If set, skip HTTPS/SSL verification.')

def init_from_args(
        parser: argparse.ArgumentParser,
        args: argparse.Namespace,
        extra_state: typing.Dict[str, typing.Any]) -> None:
    """
    Take in args from a parser that was passed to set_cli_args(),
    and call init() with the appropriate arguments.
    """

    if (args.http_exchanges_out_dir is not None):
        edq.net.request._exchanges_out_dir = args.http_exchanges_out_dir

    if (args.http_exchanges_clean_func is not None):
        edq.net.exchange._exchanges_clean_func = args.http_exchanges_clean_func

    if (args.http_exchanges_finalize_func is not None):
        edq.net.exchange._exchanges_finalize_func = args.http_exchanges_finalize_func

    if (args.https_no_verify):
        edq.net.request._disable_https_verification()
