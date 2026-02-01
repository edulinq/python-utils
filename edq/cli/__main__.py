"""
The `edq.cli` package contains general tools for the EduLinq Python library.
Each package can be invoked to list the tools (or subpackages) it contains.
Each tool includes a help prompt that accessed with the `-h`/`--help` flag.
"""

import sys

import edq.clilib.list

def main() -> int:
    """ List this CLI dir. """

    return edq.clilib.list.main()

if (__name__ == '__main__'):
    sys.exit(main())
