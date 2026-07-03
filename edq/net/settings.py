# pylint: disable=global-statement,invalid-name

import typing

DEFAULT_HTTPS_VERIFICATION: bool = True

DEFAULT_CONNECTION_TIMEOUT_SECS: float = 30.0

DEFAULT_READ_TIMEOUT_SECS: float = 60.0 * 30

_http_verification: bool = DEFAULT_HTTPS_VERIFICATION

_connection_timeout_secs: float = DEFAULT_CONNECTION_TIMEOUT_SECS

_read_timeout_secs: float = DEFAULT_READ_TIMEOUT_SECS

def get_https_verification() -> bool:
    """ Get whether to check the SSL certificate for HTTPS requests. """

    return _http_verification

def set_https_verification(value: typing.Union[bool, None] = None) -> None:
    """ Set whether to check the SSL certificate for HTTPS requests. """

    global _http_verification

    if (value is None):
        value = DEFAULT_HTTPS_VERIFICATION

    _http_verification = value

def get_connection_timeout_secs() -> float:
    """ Get the timeout for establishing a connection. """

    return _connection_timeout_secs

def set_connection_timeout_secs(value: typing.Union[float, None] = None) -> None:
    """ Set the timeout for establishing a connection. """

    global _connection_timeout_secs

    if (value is None):
        value = DEFAULT_CONNECTION_TIMEOUT_SECS

    _connection_timeout_secs = value

def get_read_timeout_secs() -> float:
    """ Get the timeout for reading from a connection. """

    return _read_timeout_secs

def set_read_timeout_secs(value: typing.Union[float, None] = None) -> None:
    """ Set the timeout for reading from a connection. """

    global _read_timeout_secs

    if (value is None):
        value = DEFAULT_READ_TIMEOUT_SECS

    _read_timeout_secs = value
