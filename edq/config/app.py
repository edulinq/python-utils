import typing

import edq.util.serial

class BaseApplicationConfig(edq.util.serial.DictConverter):
    """
    A representation of the configuration options for an application, project, or use case.
    The key use of this class is to provide typing for config options.
    When creating a TieredConfigInfo, this class (or a subclass) will be constructed with from_dict() using the resulting raw config values.
    Users of this library can extend this class (and pass that class along (usually in edq.core.argparse.get_default_parser())
    to get config typed specifically for their application.
    """

    serialization_skip_fields = {
        '_extra',
    }

    def __init__(self, **kwargs: typing.Any) -> None:
        self._extra: typing.Dict[str, typing.Any] = kwargs
        """ Config options that were not explicitly handled in the constructor. """
