import typing

import edq.config.constants
import edq.config.source
import edq.util.serial

DEFAULT_LOAD_ORDER: typing.List[edq.config.source.ConfigSource] = [
    edq.config.source.ConfigSource(edq.config.source.SourceLabel.GLOBAL),
    edq.config.source.ConfigSource(edq.config.source.SourceLabel.LOCAL),
    edq.config.source.ConfigSource(edq.config.source.SourceLabel.ENV),
    edq.config.source.ConfigSource(edq.config.source.SourceLabel.CLI_FILE),
    edq.config.source.ConfigSource(edq.config.source.SourceLabel.CLI),
]

# Private module-level options.
# See edq.config.settings for outside access to these.

# This type is extra abstracted due to a circular dependency with edq.config.app.
# edq.config.settings will ensure this value is properly set when used..
_application_config_class: typing.Union[typing.Type[edq.util.serial.DictConverter], None] = None  # pylint: disable=invalid-name

_config_filename: str = edq.config.constants.DEFAULT_CONFIG_FILENAME  # pylint: disable=invalid-name

_default_encryption_key: str = edq.config.constants.DEFAULT_ENCRYPTION_KEY  # pylint: disable=invalid-name

_env_prefix: str = edq.config.constants.DEFAULT_ENV_PREFIX  # pylint: disable=invalid-name

_legacy_config_filename: typing.Union[str, None] = None  # pylint: disable=invalid-name

_load_order: typing.List[edq.config.source.ConfigSource] = DEFAULT_LOAD_ORDER.copy()
