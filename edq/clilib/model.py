"""
This will look for objects that "look like" CLI tools.
A package looks like a CLI package if it has a __main__.py file.
A module looks like a CLI tool if it has the following functions:
 - `def _get_parser() -> argparse.ArgumentParser:`
 - `def run_cli(args: argparse.Namespace) -> int:`

CLI packages should always have a __main__.py file,
even if they only contain other packages.
"""

import argparse
import os
import typing

import edq.util.dirent
import edq.util.pyimport

class CLIDirent:
    """ A dirent that looks like it is related to a CLI. """

    def __init__(self,
            path: str,
            qualified_name: str,
            pymodule: typing.Any,
            ) -> None:
        self.path: str = path
        """
        The path for the given dirent.
        For a package, this will point to `__main__.py`.
        """

        self.qualified_name: str = qualified_name
        """ The Python qualified path to this object. """

        self.pymodule: typing.Any = pymodule
        """ The loaded module for the given path. """

    @staticmethod
    def from_path(path: str, qualified_name: str = '.') -> typing.Union['CLIDirent', None]:
        """ Load a representation of the CLI path (or None if the path is not a CLI dirent). """

        path = os.path.abspath(path)

        if (not os.path.exists(path)):
            return None

        base_name = os.path.basename(path)
        if (base_name.startswith('__')):
            return None

        if (os.path.isfile(path)):
            return CLIModule.from_path(path, qualified_name = qualified_name)

        return CLIPackage.from_path(path, qualified_name = qualified_name)

class CLIPackage(CLIDirent):
    """
    A CLI package.
    Must have a `__main__.py` file.
    """

    def __init__(self,
            path: str,
            qualified_name: str,
            pymodule: typing.Any,
            dirents: typing.Union[typing.List[CLIDirent], None] = None,
            ) -> None:
        super().__init__(path, qualified_name, pymodule)

        if (dirents is None):
            dirents = []

        self.dirents: typing.List[CLIDirent] = dirents
        """ Entries within this package. """

    @staticmethod
    def from_path(path: str, qualified_name: str = '.') -> typing.Union['CLIPackage', None]:
        """ Load a representation of the CLI package (or None if the path is not a CLI dirent). """

        path = os.path.abspath(path)

        if (not os.path.isdir(path)):
            raise ValueError(f"CLI package path does not point to a dir: '{path}'.")

        main_path = os.path.join(path, '__main__.py')
        if (not os.path.exists(main_path)):
            return None

        try:
            main_module = edq.util.pyimport.import_path(main_path)
        except Exception as ex:
            raise ValueError(f"Failed to import module __main__.py file: '{main_path}'.") from ex

        package = CLIPackage(path, qualified_name, main_module)

        for dirent in sorted(os.listdir(path)):
            dirent_path = os.path.join(path, dirent)

            dirent_qualified_name = os.path.splitext(dirent)[0]
            if (qualified_name != '.'):
                dirent_qualified_name = qualified_name + '.' + dirent_qualified_name

            cli_dirent = CLIDirent.from_path(dirent_path, dirent_qualified_name)
            if (cli_dirent is not None):
                package.dirents.append(cli_dirent)

        return package

class CLIModule(CLIDirent):
    """
    A CLI module.
    Must have the following functions:
     - `def _get_parser() -> argparse.ArgumentParser:`
     - `def run_cli(args: argparse.Namespace) -> int:`
    """

    def __init__(self,
            path: str,
            qualified_name: str,
            pymodule: typing.Any,
            parser: argparse.ArgumentParser,
            ) -> None:
        super().__init__(path, qualified_name, pymodule)

        self.parser: argparse.ArgumentParser = parser
        """ The argument parser for this CLI module. """

    @staticmethod
    def from_path(path: str, qualified_name: str = '.') -> typing.Union['CLIModule', None]:
        """ Load a representation of the CLI module (or None if the path is not a CLI dirent). """

        path = os.path.abspath(path)

        if (not os.path.isfile(path)):
            raise ValueError(f"CLI module path does not point to a file: '{path}'.")

        try:
            module = edq.util.pyimport.import_path(path)
        except Exception as ex:
            raise ValueError(f"Failed to import module: '{path}'.") from ex

        # Check if this looks like a CLI module.
        if ('_get_parser' not in dir(module)):
            return None

        parser = module._get_parser()
        parser.prog = 'python3 -m ' + qualified_name

        return CLIModule(path, qualified_name, module, parser)
