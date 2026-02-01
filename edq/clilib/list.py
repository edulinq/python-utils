"""
Show the CLI tools available in this package.

This will look for objects that "look like" CLI tools.
A package looks like a CLI package if it has a __main__.py file.
A module looks like a CLI tool if it has the following functions:
 - `def _get_parser() -> argparse.ArgumentParser:`
 - `def run_cli(args: argparse.Namespace) -> int:`

CLI packages should always have a __main__.py file,
even if they only contain other packages.
"""

import argparse
import inspect
import os
import typing

import edq.util.dirent
import edq.util.pyimport

class CLIDirent:
    """ A dirent that looks like it is related to a CLI. """

    def __init__(self,
            path: str,
            qualified_path: str,
            pymodule: typing.Any,
            ) -> None:
        self.path: str = path
        """
        The path for the given dirent.
        For a package, this will point to `__main__.py`.
        """

        self.qualified_path: str = qualified_path
        """ The Python qualified path to this object. """

        self.pymodule: typing.Any = pymodule
        """ The loaded module for the given path. """

class CLIPackage(CLIDirent):
    """
    A CLI package.
    Must have a `__main__.py` file.
    """

    def __init__(self,
            path: str,
            qualified_path: str,
            pymodule: typing.Any,
            dirents: typing.Union[typing.List[CLIDirent], None] = None,
            ) -> None:
        super().__init__(path, qualified_path, pymodule)

        if (dirents is None):
            dirents = []

        self.dirents: typing.List[CLIDirent] = dirents
        """ Entries within this package. """

class CLIModule(CLIDirent):
    """
    A CLI module.
    Must have the following functions:
     - `def _get_parser() -> argparse.ArgumentParser:`
     - `def run_cli(args: argparse.Namespace) -> int:`
    """

def auto_list(
        recursive: bool = False,
        skip_dirs: bool = False,
        ) -> None:
    """
    Print the caller's docstring and call _list_dir() on it,
    but will figure out the package's docstring, base_dir, and command_prefix automatically.
    This will use the inspect library, so only use in places that use code normally.
    The first stack frame not in this file will be used.
    """

    this_path = os.path.realpath(__file__)

    caller_frame_info = None
    for frame_info in inspect.stack():
        if (edq.util.dirent.same(this_path, frame_info.filename)):
            # Ignore this file.
            continue

        caller_frame_info = frame_info
        break

    if (caller_frame_info is None):
        raise ValueError("Unable to determine caller's stack frame.")

    path = caller_frame_info.filename
    base_dir = os.path.dirname(path)

    try:
        module = inspect.getmodule(caller_frame_info.frame)
        if (module is None):
            raise ValueError(f"Unable to get module for '{path}'.")
    except Exception as ex:
        raise ValueError("Unable to get caller information for listing CLI information.") from ex

    if (module.__package__ is None):
        raise ValueError(f"Caller module has no package information: '{path}'.")

    if (module.__doc__ is None):
        raise ValueError(f"Caller module has no docstring: '{path}'.")

    package = collect_cli_entries(base_dir, module.__package__)
    if (package is None):
        raise ValueError(f"Caller package is not a CLI package: '{base_dir}'.")

    print(module.__doc__.strip())
    _list_dir(package, recursive, skip_dirs)

def _list_dir(package: CLIPackage, recursive: bool, skip_dirs: bool) -> None:
    """
    List/descend the given dir.
    Don't output information out this directory itself, just the entries.
    """

    for dirent in package.dirents:
        if (isinstance(dirent, CLIModule)):
            _handle_module(dirent)
        elif (isinstance(dirent, CLIPackage)):
            if (not skip_dirs):
                _handle_package(dirent)

            if (recursive):
                _list_dir(dirent, recursive, skip_dirs)

def _handle_module(module: CLIModule) -> None:
    """ Process a module. """

    parser = module.pymodule._get_parser()
    parser.prog = 'python3 -m ' + module.qualified_path

    print()
    print(module.qualified_path)
    print(parser.description)
    parser.print_usage()

def _handle_package(package: CLIPackage) -> None:
    """ Process a package. """

    description = package.pymodule.__doc__.strip()

    print()
    print(package.qualified_path + '.*')
    print(description)
    print(f"See `python3 -m {package.qualified_path}` for more information.")

def collect_cli_entries(
        base_dir: str,
        base_qualified_path: str = '.',
        ) -> typing.Union[CLIPackage, None]:
    """ Collect CLI dirents starting from the given base dir/package. """

    base_dir = os.path.abspath(base_dir)

    main_path = os.path.join(base_dir, '__main__.py')
    if (not os.path.exists(main_path)):
        return None

    try:
        main_module = edq.util.pyimport.import_path(main_path)
    except Exception as ex:
        raise ValueError(f"Failed to import module __main__.py file: '{main_path}'.") from ex

    package = CLIPackage(base_dir, base_qualified_path, main_module)

    for dirent in sorted(os.listdir(base_dir)):
        path = os.path.join(base_dir, dirent)

        qualified_path = os.path.splitext(dirent)[0]
        if (base_qualified_path != '.'):
            qualified_path = base_qualified_path + '.' + qualified_path

        if (dirent.startswith('__')):
            continue

        if (os.path.isfile(path)):
            try:
                module = edq.util.pyimport.import_path(path)
            except Exception as ex:
                raise ValueError(f"Failed to import module: '{path}'.") from ex

            # Check if this looks like a CLI module.
            if ('_get_parser' not in dir(module)):
                continue

            package.dirents.append(CLIModule(path, qualified_path, module))
        else:
            dirent_package = collect_cli_entries(path, base_qualified_path = qualified_path)
            if (dirent_package is not None):
                package.dirents.append(dirent_package)

    return package

def _get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description = __doc__.strip(),
        epilog = ("Note that you don't need to provide a package as an argument,"
            + " since you already called this on the target package."))

    parser.add_argument('-r', '--recursive', dest = 'recursive',
        action = 'store_true', default = False,
        help = 'Recur into each package to look for tools and subpackages (default: %(default)s).')

    parser.add_argument('-s', '--skip-dirs', dest = 'skip_dirs',
        action = 'store_true', default = False,
        help = ('Do not output information about directories/packages,'
            + ' only tools/files/modules (default: %(default)s).'))

    return parser

def run_cli(args: argparse.Namespace) -> int:
    """
    List the caller's dir.
    """

    auto_list(recursive = args.recursive, skip_dirs = args.skip_dirs)

    return 0

def main() -> int:
    """
    Run as if this process has been called as a executable.
    This will parse the command line and list the caller's dir.
    """

    return run_cli(_get_parser().parse_args())
