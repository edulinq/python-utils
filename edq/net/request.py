import http
import logging
import os
import typing
import urllib.parse
import urllib3

import requests

import edq.net.exchange
import edq.net.exchangeserver
import edq.util.dirent
import edq.util.encoding
import edq.util.json
import edq.util.pyimport

_logger = logging.getLogger(__name__)

DEFAULT_REQUEST_TIMEOUT_SECS: float = 10.0
""" Default timeout for an HTTP request. """

_exchanges_out_dir: typing.Union[str, None] = None  # pylint: disable=invalid-name
""" If not None, all requests made via make_request() will be saved as an HTTPExchange in this directory. """

_module_makerequest_options: typing.Union[typing.Dict[str, typing.Any], None] = None  # pylint: disable=invalid-name
"""
Module-wide options for requests.request().
These should generally only be used in testing.
"""

_make_request_exchange_complete_func: typing.Union[edq.net.exchange.HTTPExchangeComplete, None] = None  # pylint: disable=invalid-name
""" If not None, call this func after make_request() has created its HTTPExchange. """

@typing.runtime_checkable
class ResponseModifierFunction(typing.Protocol):
    """
    A function that can be used to modify an exchange's response.
    Exchanges can use these functions to normalize their responses before saving.
    """

    def __call__(self,
            response: requests.Response,
            body: str,
            ) -> str:
        """
        Modify the http response.
        Headers may be modified in the response directly,
        while the modified (or same) body must be returned.
        """

def make_request(method: str, url: str,
        headers: typing.Union[typing.Dict[str, typing.Any], None] = None,
        data: typing.Union[typing.Dict[str, typing.Any], None] = None,
        files: typing.Union[typing.List[typing.Any], None] = None,
        raise_for_status: bool = True,
        timeout_secs: float = DEFAULT_REQUEST_TIMEOUT_SECS,
        output_dir: typing.Union[str, None] = None,
        send_anchor_header: bool = True,
        headers_to_skip: typing.Union[typing.List[str], None] = None,
        params_to_skip: typing.Union[typing.List[str], None] = None,
        http_exchange_extension: str = edq.net.exchange.DEFAULT_HTTP_EXCHANGE_EXTENSION,
        add_http_prefix: bool = True,
        additional_requests_options: typing.Union[typing.Dict[str, typing.Any], None] = None,
        exchange_complete_func: typing.Union[edq.net.exchange.HTTPExchangeComplete, None] = None,
        allow_redirects: typing.Union[bool, None] = None,
        use_module_options: bool = True,
        **kwargs: typing.Any) -> typing.Tuple[requests.Response, str]:
    """
    Make an HTTP request and return the response object and text body.
    """

    if (add_http_prefix and (not url.lower().startswith('http'))):
        url = 'http://' + url

    if (output_dir is None):
        output_dir = _exchanges_out_dir

    if (headers is None):
        headers = {}

    if (data is None):
        data = {}

    if (files is None):
        files = []

    if (additional_requests_options is None):
        additional_requests_options = {}

    # Add in the anchor as a header (since it is not traditionally sent in an HTTP request).
    if (send_anchor_header):
        headers = headers.copy()

        parts = urllib.parse.urlparse(url)
        headers[edq.net.exchange.ANCHOR_HEADER_KEY] = parts.fragment.lstrip('#')

    options = {}

    if (use_module_options and (_module_makerequest_options is not None)):
        options.update(_module_makerequest_options)

    options.update(additional_requests_options)

    options.update({
        'headers': headers,
        'files': files,
        'timeout': timeout_secs,
    })

    if (allow_redirects is not None):
        options['allow_redirects'] = allow_redirects

    if (method == 'GET'):
        options['params'] = data
    else:
        options['data'] = data

    _logger.debug("Making %s request: '%s' (options = %s).", method, url, options)
    response = requests.request(method, url, **options)  # pylint: disable=missing-timeout

    body = response.text
    _logger.debug("Response:\n%s", body)

    if (raise_for_status):
        # Handle 404s a little special, as their body may contain useful information.
        if ((response.status_code == http.HTTPStatus.NOT_FOUND) and (body is not None) and (body.strip() != '')):
            response.reason += f" (Body: '{body.strip()}')"

        response.raise_for_status()

    exchange = None
    if ((output_dir is not None) or (exchange_complete_func is not None) or (_make_request_exchange_complete_func is not None)):
        exchange = edq.net.exchange.HTTPExchange.from_response(response,
                headers_to_skip = headers_to_skip, params_to_skip = params_to_skip,
                allow_redirects = options.get('allow_redirects', None))

    if ((output_dir is not None) and (exchange is not None)):
        relpath = exchange.compute_relpath(http_exchange_extension = http_exchange_extension)
        path = os.path.abspath(os.path.join(output_dir, relpath))

        edq.util.dirent.mkdir(os.path.dirname(path))
        edq.util.json.dump_path(exchange, path, indent = 4, sort_keys = False)

    if ((exchange_complete_func is not None) and (exchange is not None)):
        exchange_complete_func(exchange)

    if ((_make_request_exchange_complete_func is not None) and (exchange is not None)):
        _make_request_exchange_complete_func(exchange)  # pylint: disable=not-callable

    return response, body

def make_with_exchange(
        exchange: edq.net.exchange.HTTPExchange,
        base_url: str,
        raise_for_status: bool = True,
        **kwargs: typing.Any,
        ) -> typing.Tuple[requests.Response, str]:
    """ Perform the HTTP request described by the given exchange. """

    files = []
    for file_info in exchange.files:
        content = file_info.content

        # Content is base64 encoded.
        if (file_info.b64_encoded and isinstance(content, str)):
            content = edq.util.encoding.from_base64(content)

        # Content is missing and must be in a file.
        if (content is None):
            content = open(file_info.path, 'rb')  # type: ignore[assignment,arg-type]  # pylint: disable=consider-using-with

        files.append((file_info.name, content))

    url = f"{base_url}/{exchange.get_url()}"

    response, body = make_request(exchange.method, url,
            headers = exchange.headers,
            data = exchange.parameters,
            files = files,
            raise_for_status = raise_for_status,
            allow_redirects = exchange.allow_redirects,
            **kwargs,
    )

    if (exchange.response_modifier is not None):
        modify_func = edq.util.pyimport.fetch(exchange.response_modifier)
        body = modify_func(response, body)

    return response, body


def make_get(url: str, **kwargs: typing.Any) -> typing.Tuple[requests.Response, str]:
    """
    Make a GET request and return the response object and text body.
    """

    return make_request('GET', url, **kwargs)

def make_post(url: str, **kwargs: typing.Any) -> typing.Tuple[requests.Response, str]:
    """
    Make a POST request and return the response object and text body.
    """

    return make_request('POST', url, **kwargs)

def _disable_https_verification() -> None:
    """ Disable checking the SSL certificate for HTTPS requests. """

    global _module_makerequest_options  # pylint: disable=global-statement

    if (_module_makerequest_options is None):
        _module_makerequest_options = {}

    _module_makerequest_options['verify'] = False

    # Ignore insecure warnings.
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
