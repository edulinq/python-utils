import os
import typing

import edq.config.common
import edq.util.serial

class ConfigSourceSpec(edq.config.common.InternalConfigSourceSpec):
    """
    A source spec represents a location where config values may be stored.
    """

class CLISpec(ConfigSourceSpec):
    """ A source spec for loading from CLI arguments (but not files specified on the command-line). """

    label: str = 'cli argument'

class CLIFileSpec(ConfigSourceSpec):
    """ A source spec for loading a file that was specified as a CLI argument. """

    label: str = 'cli config file'

class ENVSpec(ConfigSourceSpec):
    """ A source spec for loading from an environmental variable. """

    label: str = 'environmental variable'

class AbstractPathSpec(ConfigSourceSpec):
    """
    An abstract source spec that includes a target directory and filename.

    An argument not set (or set to None) indicates that the value should be determined at parse time.
    These values (generally paths or filenames) are often pulled from the `edq.config.settings` module
    (and therefore can be set by users of this library anytime before loading the config).
    """

    def __init__(self,
            base_dir: typing.Union[str, None] = None,
            filename: typing.Union[str, None] = None,
            **kwargs: typing.Any) -> None:
        super().__init__()

        if ((base_dir is not None) and (os.path.isfile(base_dir))):
            raise ValueError(f"The specified config dir is not a directory: '{base_dir}'.")

        self.base_dir: typing.Union[str, None] = base_dir
        """ The directory to look for the global config file in. """

        self.filename: typing.Union[str, None] = filename
        """ The filename to look for. """

    def get_default_base_dir(self) -> typing.Union[str, None]:
        """ Retrieve the default base dir (usually from edq.config.settings) for use when no base dir is explicitly set. """

        return None

    def get_default_filename(self) -> typing.Union[str, None]:
        """ Retrieve the default filename (usually from edq.config.settings) for use when no filename is explicitly set. """

        return None

    def resolve_path(self,
            override_path: typing.Union[str, None] = None,
            ) -> str:
        """
        Get the path that should be use to load config.
        This method is free to traverse the disk to find the desired path.
        """

        if (override_path is not None):
            return override_path

        base_dir = self.base_dir
        if (base_dir is None):
            base_dir = self.get_default_base_dir()

        if (base_dir is None):
            raise ValueError(f"Unable to resolve a config base dir for class {type(self)}.")

        filename = self.filename
        if (filename is None):
            filename = self.get_default_filename()

        if (filename is None):
            raise ValueError(f"Unable to resolve a config filename for class {type(self)}.")

        return os.path.join(base_dir, filename)

class GlobalSpec(AbstractPathSpec):
    """ A source spec for loading from a global (user-level) config file. """

    label: str = 'global config file'

    def get_default_base_dir(self) -> typing.Union[str, None]:
        return edq.config.common._global_dir

    def get_default_filename(self) -> typing.Union[str, None]:
        return edq.config.common._config_filename

class LocalSpec(AbstractPathSpec):
    """ A source spec for loading from a local config file. """

    label: str = 'local config file'

    def get_default_base_dir(self) -> typing.Union[str, None]:
        return os.path.abspath(os.getcwd())

    def get_default_filename(self) -> typing.Union[str, None]:
        return edq.config.common._config_filename

class ProjectSpec(AbstractPathSpec):
    """
    A source spec for loading from a project, which will look in the current directory and all parents until a matching file is found.
    """

    label: str = 'project config file'

    def __init__(self,
            root_cutoff: typing.Union[str, None] = None,
            filename: typing.Union[str, None] = None,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        self.root_cutoff: typing.Union[str, None] = root_cutoff
        """ If set, stop searching parents if this directory is encountered. """

    def get_default_base_dir(self) -> typing.Union[str, None]:
        return os.path.abspath(os.getcwd())

    def get_default_filename(self) -> typing.Union[str, None]:
        return edq.config.common._config_filename

    def resolve_path(self,
            override_path: typing.Union[str, None] = None,
            ) -> str:
        if (override_path is not None):
            return override_path

        base_dir = self.base_dir
        if (base_dir is None):
            base_dir = self.get_default_base_dir()

        if (base_dir is None):
            raise ValueError(f"Unable to resolve a config base dir for class {type(self)}.")

        filename = self.filename
        if (filename is None):
            filename = self.get_default_filename()

        if (filename is None):
            raise ValueError(f"Unable to resolve a config filename for class {type(self)}.")

        current_dir = base_dir
        for _ in range(edq.util.dirent.DEPTH_LIMIT):
            path = os.path.join(current_dir, filename)
            if (os.path.isfile(path)):
                return path

            # Check if current directory is root.
            parent_dir = os.path.dirname(current_dir)
            if (parent_dir == current_dir):
                break

            if ((self.root_cutoff is not None) and (self.root_cutoff == current_dir)):
                break

            current_dir = parent_dir

        # If no file was found, use the base dir.
        return os.path.join(base_dir, filename)

edq.config.common._DEFAULT_LOAD_ORDER = [
    GlobalSpec(),
    ProjectSpec(),
    LocalSpec(),
    ENVSpec(),
    CLIFileSpec(),
    CLISpec(),
]
edq.config.common._load_order = edq.config.common._DEFAULT_LOAD_ORDER.copy()
