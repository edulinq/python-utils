# pylint: disable=global-statement,invalid-name

import typing

DEFAULT_HTTPS_VERIFICATION: bool = True

_http_verification: bool = DEFAULT_HTTPS_VERIFICATION

def get_https_verification() -> bool:
    """ Get whether to check the SSL certificate for HTTPS requests. """

    return _http_verification

def set_https_verification(value: typing.Union[bool, None] = None) -> None:
    """ Set whether to check the SSL certificate for HTTPS requests. """

    global _http_verification

    if (value is None):
        value = DEFAULT_HTTPS_VERIFICATION

    _http_verification = value
