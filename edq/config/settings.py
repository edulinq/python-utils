import typing

import edq.config.app
import edq.config.common
import edq.config.constants
import edq.util.serial

def get_application_config_class() -> typing.Type[edq.config.app.BaseApplicationConfig]:
    """ Get the application config class. """

    if (edq.config.common._application_config_class is None):
        edq.config.common._application_config_class = edq.config.app.BaseApplicationConfig

    return typing.cast(typing.Type[edq.config.app.BaseApplicationConfig], edq.config.common._application_config_class)

def set_application_config_class(config_class: typing.Union[typing.Type[edq.config.app.BaseApplicationConfig], None] = None) -> None:
    """ Set the application config class. """

    if (config_class is None):
        config_class = edq.config.app.BaseApplicationConfig

    edq.config.common._application_config_class = config_class

def get_config_filename() -> str:
    """ Get the config filename. """

    return edq.config.common._config_filename

def set_config_filename(filename: str) -> None:
    """ Set the config filename. """

    edq.config.common._config_filename = filename

def get_default_encryption_key() -> str:
    """ Get the default encryption key. """

    return edq.config.common._default_encryption_key

def set_default_encryption_key(encryption_key: typing.Union[str, None] = None) -> None:
    """ Set the default encryption key. """

    if (encryption_key is None):
        encryption_key = edq.config.constants.DEFAULT_ENCRYPTION_KEY

    edq.config.common._default_encryption_key = encryption_key

def get_env_prefix() -> str:
    """ Get the environmental variable prefix. """

    return edq.config.common._env_prefix

def set_env_prefix(prefix: typing.Union[str, None] = None) -> None:
    """ Set the environmental variable prefix. """

    if (prefix is None):
        prefix = edq.config.constants.DEFAULT_ENV_PREFIX

    edq.config.common._env_prefix = prefix

def get_legacy_config_filename() -> typing.Union[str, None]:
    """ Get the config legacy filename. """

    return edq.config.common._legacy_config_filename

def set_legacy_config_filename(legacy_filename: typing.Union[str, None]) -> None:
    """ Set the legacy config filename. """

    edq.config.common._legacy_config_filename = legacy_filename
