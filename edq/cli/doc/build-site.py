# pylint: disable=invalid-name

"""
Create a website that contains multiple versions of documentation for a package.
"""

import argparse
import os
import sys

import edq.core.argparser
import edq.util.docs

def run_cli(args: argparse.Namespace) -> int:
    """ Run the CLI. """

    package_dir = os.path.abspath(args.package_dir)
    repo_root_dir = os.path.dirname(package_dir)
    base_package_name = os.path.basename(package_dir)

    edq.util.docs.build_site(
        repo_root_dir,
        base_package_name,
        args.out_dir,
        skip_tag_pattern = args.skip_tag_pattern,
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
        help = 'The package to generate documentation for (it is assumed that the repo root is the parent of this dir).',
    )

    parser.add_argument('--out-dir', dest = 'out_dir',
        action = 'store', type = str, default = os.path.join('build', 'site'),
        help = 'Where to write output (default: %(default)s).',
    )

    parser.add_argument('--skip-tags', dest = 'skip_tag_pattern',
        action = 'store', type = str, default = None,
        help = 'Skip any tags that match this pattern.'
    )

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
