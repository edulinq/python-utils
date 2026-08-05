# pylint: disable=invalid-name

"""
Create HTML documentation for a package.
"""

import argparse
import os
import sys

import edq.core.argparser
import edq.util.docs

def run_cli(args: argparse.Namespace) -> int:
    """ Run the CLI. """

    edq.util.docs.generate_docs(
        args.package_dir,
        args.out_dir,
        file_pattern = args.file_pattern,
    )

    return 0

def main() -> int:
    """ Get a parser, parse the args, and call run. """

    return run_cli(_get_parser().parse_args())

def _get_parser() -> argparse.ArgumentParser:
    """ Get a parser and add addition flags. """

    parser = edq.core.argparser.get_default_parser(__doc__.strip())

    parser.add_argument('package_dir', metavar = 'PACKAGE_DIR',
        action = 'store', type = str,
        help = 'The package to generate documentation for.',
    )

    parser.add_argument('--out-dir', dest = 'out_dir',
        action = 'store', type = str, default = os.path.join('build', 'html'),
        help = 'Where to write output (default: %(default)s).',
    )

    parser.add_argument('--file-pattern', dest = 'file_pattern',
        action = 'store', type = str, default = edq.util.docs.DEFAULT_FILE_PATTERNS,
        help = (
            'Only use files that match this pattern'
            + ' (see `https://pdoc.dev/docs/pdoc.html#exclude-submodules-from-being-documented`)'
            + ' (default: %(default)s).'
        ),
    )

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
