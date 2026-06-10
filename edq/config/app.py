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

    def __init__(self,
            configs: typing.Union[typing.List[str], None] = None,
            config_paths: typing.Union[typing.List[str], None] = None,
            global_config_path: typing.Union[str, None] = None,
            ignore_configs: typing.Union[typing.List[str], None] = None,
            encryption_key: typing.Union[str, None] = None,
            debug: typing.Union[bool, None] = None,
            log_level: typing.Union[str, None] = None,
            quiet: typing.Union[bool, None] = None,
            **kwargs: typing.Any) -> None:
        self.configs: typing.Union[typing.List[str], None] = configs
        """ Config options set directly on the command-line. """

        self.config_paths: typing.Union[typing.List[str], None] = config_paths
        """ Config file paths specified on the command-line. """

        self.global_config_path: typing.Union[str, None] = global_config_path
        """ The path to the used global config file. """

        self.ignore_configs: typing.Union[typing.List[str], None] = ignore_configs
        """ Config keys to ignore. """

        self.encryption_key: typing.Union[str, None] = encryption_key
        """ The encryption key to use for config secrets. """

        self.debug: typing.Union[bool, None] = debug
        """ If extra debugging (e.g., logging) information should be provided. """

        self.log_level: typing.Union[str, None] = log_level
        """ The log level this program was started with. """

        self.quiet: typing.Union[bool, None] = quiet
        """ If the logs should give reduced output. """

        self._extra: typing.Dict[str, typing.Any] = kwargs
        """ Config options that were not explicitly handled in the constructor. """

    def to_dict(self,
            context: typing.Union[edq.util.serial.SerializationContext, None] = None,
            ) -> typing.Dict[str, edq.util.serial.PODType]:
        if (context is None):
            context = edq.util.serial.SerializationContext()
        else:
            context = context.copy()

        if (context.key is None):
            context.key = self.encryption_key

        return super().to_dict(context)
