"""
Discover and run unit tests (via Python's unittest package)
that live in this project's base package
(the parent of this package).
"""

import argparse
import os
import re
import sys
import typing
import unittest

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))
BASE_PACKAGE_DIR: str = os.path.join(THIS_DIR, '..')
PROJECT_ROOT_DIR: str = os.path.join(BASE_PACKAGE_DIR, '..')

DEFAULT_TEST_FILENAME_PATTERN: str = '*_test.py'

def _collect_tests(suite: typing.Union[unittest.TestCase, unittest.suite.TestSuite]) -> typing.List[unittest.TestCase]:
    """
    Collect and return tests (unittest.TestCase) from the target directory.
    """

    if (isinstance(suite, unittest.TestCase)):
        return [suite]

    if (not isinstance(suite, unittest.suite.TestSuite)):
        raise ValueError(f"Unknown test type: '{str(type(suite))}'.")

    test_cases = []
    for test_object in suite:
        test_cases += _collect_tests(test_object)

    return test_cases

def run(args: argparse.Namespace) -> int:
    """
    Discover and run unit tests.
    This function may change your working directory.
    Will raise if tests fail to load (e.g. syntax errors) and a suggested exit code otherwise.
    """

    # Start in the project's root and add it in the path.
    os.chdir(PROJECT_ROOT_DIR)
    sys.path.append(PROJECT_ROOT_DIR)

    runner = unittest.TextTestRunner(verbosity = 3)
    discovered_suite = unittest.TestLoader().discover(BASE_PACKAGE_DIR, pattern = args.filename_pattern)
    test_cases = _collect_tests(discovered_suite)

    tests = unittest.suite.TestSuite()

    for test_case in test_cases:
        if (isinstance(test_case, unittest.loader._FailedTest)):  # type: ignore[attr-defined]
            raise ValueError(f"Failed to load test: '{test_case.id()}'.") from test_case._exception

        if (args.pattern is None or re.search(args.pattern, test_case.id())):
            tests.addTest(test_case)
        else:
            print(f"Skipping {test_case.id()} because of match pattern.")

    result = runner.run(tests)
    faults = len(result.errors) + len(result.failures)

    if (not result.wasSuccessful()):
        # This value will be used as an exit status, so don't larger than a byte.
        # (Some higher values are used specially, so just keep it at a round number.)
        return max(1, min(faults, 100))

    return 0

def main() -> int:
    args = _get_parser().parse_args()
    return run(args)

def _get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description = 'Run unit tests discovered in this project.')

    parser.add_argument('pattern',
        action = 'store', type = str, default = None, nargs = '?',
        help = 'If supplied, only tests with names matching this pattern will be run. This pattern is used directly in re.search().')

    parser.add_argument('--filename-pattern', dest = 'filename_pattern',
        action = 'store', type = str, default = DEFAULT_TEST_FILENAME_PATTERN,
        help = 'The pattern to use to find test files (default: %(default)s).')

    return parser

if __name__ == '__main__':
    sys.exit(main())
