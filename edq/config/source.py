import enum
import typing

import edq.util.serial

class SourceLabel(enum.Enum):
    """ Labels for the differnt types of config sources. """

    CLI = 'cli argument'
    CLI_FILE = 'cli config file'
    ENV = 'environmental variable'
    GLOBAL = 'global config file'
    LOCAL = 'local config file'
    PROJECT = 'project config file'

# TEST - Filename
# TEST - Difference between a source to be loaded and one that already was loaded? SourceSpec vs Source?
class ConfigSource(edq.util.serial.DictConverter):
    """ A representation of where a config value can be taken from. """

    def __init__(self,
            label: SourceLabel,
            path: typing.Union[str, None] = None,
            ) -> None:
        self.label: SourceLabel = label
        """ The label identifying the source type. """

        self.path: typing.Union[str, None] = path
        """ The path of where the config was sourced from. """

    def __repr__(self) -> str:
        if (self.path is not None):
            return f"<{self.label.value} ({self.path})>"

        return f"<{self.label.value}>"
