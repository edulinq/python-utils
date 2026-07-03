# pylint: disable=global-statement,invalid-name

"""
This module holds options that persist the lifetime of the program.
Most options can be overwritten in specific calls, e.g., in edq.net.request.make_request().
"""

import typing

DEFAULT_HTTPS_VERIFICATION: bool = True

DEFAULT_CONNECTION_TIMEOUT_SECS: float = 30.0

DEFAULT_READ_TIMEOUT_SECS: float = 60.0 * 30

_exchanges_out_dir: typing.Union[str, None] = None
""" If not None, all requests made via make_request() will be saved as an HTTPExchange in this directory. """

_http_verification: bool = DEFAULT_HTTPS_VERIFICATION
"""
Whether to verify HTTPS requests.
Should be set to false when using fake/testing certificates.
"""

_connection_timeout_secs: float = DEFAULT_CONNECTION_TIMEOUT_SECS
""" The timeout for establishing a connection. """

_read_timeout_secs: float = DEFAULT_READ_TIMEOUT_SECS
""" The timeout for reading from a connection. """

def get_exchanges_out_dir() -> typing.Union[str, None]:
    """ Get the directory to write HTTP exchanges (if any). """

    return _exchanges_out_dir

def set_exchanges_out_dir(value: typing.Union[str, None] = None) -> None:
    """ Set the directory to write HTTP exchanges. """

    global _exchanges_out_dir
    _exchanges_out_dir = value

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
