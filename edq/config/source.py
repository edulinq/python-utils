import enum
import os
import typing

import edq.util.serial

class SourceLabel(enum.Enum):
    """ Labels for the different types of config sources. """

    CLI = 'cli argument'
    CLI_FILE = 'cli config file'
    ENV = 'environmental variable'
    GLOBAL = 'global config file'
    LOCAL = 'local config file'
    # TEST
    PROJECT = 'project config file'

class ConfigSourceSpec(edq.util.serial.DictConverter):
    """
    A source spec represents a location where config values may be stored.

    For this family of classes, an argument not set (or set to None) indicates that the value should be determined at parse time.
    These values (often paths or filenames) are often pulled from the `edq.config.settings` module
    (and therefore can be set by users of this library anytime before loading the config).
    """

    label: str = ''
    """
    A label set by each subclass to identify the type of source spec.
    Generally, a user-friendly version of the class name.
    """

    def __init__(self,
            path: typing.Union[str, None] = None,
            filename: typing.Union[str, None] = None,
            ) -> None:
        if (len(self.label) == 0):
            raise ValueError(f"ConfigSourceSpec child class ({type(self)}) did not set label.")

class CLISpec(ConfigSourceSpec):
    """ A source spec for loading from CLI arguments (but not files specified on the command-line). """

    label: str = 'cli argument'

class CLIFileSpec(ConfigSourceSpec):
    """ A source spec for loading a file that was specified as a CLI argument. """

    label: str = 'cli config file'

class ENVSpec(ConfigSourceSpec):
    """ A source spec for loading from an environmental variable. """

    label: str = 'environmental variable'

class GlobalSpec(ConfigSourceSpec):
    """ A source spec for loading from a global (user-level) config file. """

    label: str = 'global config file'

    def __init__(self,
            config_dir: typing.Union[str, None] = None,
            filename: typing.Union[str, None] = None,
            ) -> None:
        super().__init__()

        if ((config_dir is not None) and (os.path.isfile(config_dir))):
            raise ValueError(f"The specified global config dir is not a directory: '{config_dir}'.")

        self.config_dir: typing.Union[str, None] = config_dir
        """ The directory to look for the global config file in. """

        self.filename: typing.Union[str, None] = filename
        """ The filename to look for. """

class LocalSpec(ConfigSourceSpec):
    """ A source spec for loading from a local config file. """

    label: str = 'local config file'

    def __init__(self,
            config_dir: typing.Union[str, None] = None,
            filename: typing.Union[str, None] = None,
            ) -> None:
        super().__init__()

        if ((config_dir is not None) and (os.path.isfile(config_dir))):
            raise ValueError(f"The specified local config dir is not a directory: '{config_dir}'.")

        self.config_dir: typing.Union[str, None] = config_dir
        """ The directory to look for the local config file in. """

        self.filename: typing.Union[str, None] = filename
        """ The filename to look for. """
