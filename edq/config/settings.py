import typing

import edq.config.app
import edq.config.constants

_config_filename: str = edq.config.constants.DEFAULT_CONFIG_FILENAME  # pylint: disable=invalid-name
_legacy_config_filename: typing.Union[str, None] = None  # pylint: disable=invalid-name

_application_config_class: typing.Type[edq.config.app.BaseApplicationConfig] = edq.config.app.BaseApplicationConfig  # pylint: disable=invalid-name

_env_prefix: str = edq.config.constants.DEFAULT_ENV_PREFIX  # pylint: disable=invalid-name

def get_config_filename() -> str:
    """ Get the config filename. """

    return _config_filename

def set_config_filename(filename: str) -> None:
    """ Set the config filename. """

    global _config_filename  # pylint: disable=global-statement
    _config_filename = filename

def get_legacy_config_filename() -> typing.Union[str, None]:
    """ Get the config legacy filename. """

    return _legacy_config_filename

def set_legacy_config_filename(legacy_filename: typing.Union[str, None]) -> None:
    """ Set the legacy config filename. """

    global _legacy_config_filename  # pylint: disable=global-statement
    _legacy_config_filename = legacy_filename

def get_application_config_class() -> typing.Type[edq.config.app.BaseApplicationConfig]:
    """ Get the application config class. """

    return _application_config_class

def set_application_config_class(config_class: typing.Union[typing.Type[edq.config.app.BaseApplicationConfig], None] = None) -> None:
    """ Set the application config class. """

    if (config_class is None):
        config_class = edq.config.app.BaseApplicationConfig

    global _application_config_class  # pylint: disable=global-statement
    _application_config_class = config_class

def get_env_prefix() -> str:
    """ Get the environmental variable prefix. """

    return _env_prefix

def set_env_prefix(prefix: typing.Union[str, None] = None) -> None:
    """ Set the environmental variable prefix. """

    if (prefix is None):
        prefix = edq.config.constants.DEFAULT_ENV_PREFIX

    global _env_prefix  # pylint: disable=global-statement
    _env_prefix = prefix
