import atexit
import http
import logging
import os
import time
import typing
import urllib.parse
import urllib3

import requests

import edq.core.errors
import edq.net.exchange
import edq.net.exchangeserver
import edq.util.dirent
import edq.util.encoding
import edq.util.json
import edq.util.pyimport

_logger = logging.getLogger(__name__)

DEFAULT_REQUEST_TIMEOUT_SECS: float = 10.0
""" Default timeout for an HTTP request. """

RETRY_BACKOFF_SECS: float = 0.5

_exchanges_cache_dir: typing.Union[str, None] = None  # pylint: disable=invalid-name
""" If not None, all requests made via make_request() will attempt to look in this directory for a matching exchange first. """

_exchanges_out_dir: typing.Union[str, None] = None  # pylint: disable=invalid-name
""" If not None, all requests made via make_request() will be saved as an HTTPExchange in this directory. """

_module_makerequest_options: typing.Union[typing.Dict[str, typing.Any], None] = None  # pylint: disable=invalid-name
"""
Module-wide options for requests.request().
These should generally only be used in testing.
"""

_cache_servers: typing.Dict[str, edq.net.exchangeserver.HTTPExchangeServer] = {}
""" A mapping of cache dirs to their active cache server. """

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
        cache_dir: typing.Union[str, None] = None,
        ignore_cache: bool = False,
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
        retries: int = 0,
        **kwargs: typing.Any) -> typing.Tuple[requests.Response, str]:
    """
    Make an HTTP request and return the response object and text body.
    """

    if (add_http_prefix and (not url.lower().startswith('http'))):
        url = 'http://' + url

    retries = max(0, retries)

    if (cache_dir is None):
        cache_dir = _exchanges_cache_dir

    if (ignore_cache):
        cache_dir = None

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

    options: typing.Dict[str, typing.Any] = {
        'timeout': timeout_secs,
    }

    if (use_module_options and (_module_makerequest_options is not None)):
        options.update(_module_makerequest_options)

    options.update(additional_requests_options)

    options.update({
        'headers': headers,
        'files': files,
    })

    if (allow_redirects is not None):
        options['allow_redirects'] = allow_redirects

    if (method == 'GET'):
        options['params'] = data
    else:
        options['data'] = data

    _logger.debug("Making %s request: '%s' (options = %s).", method, url, options)
    response = _make_request_with_cache(method, url, options, cache_dir, retries)

    body = response.text
    if (_logger.level <= logging.DEBUG):
        log_body = body
        if (response.encoding is None):
            log_body = f"<hash> {edq.util.hash.sha256_hex(response.content)}"

        _logger.debug("Response:\n%s", log_body)

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

def _make_request_with_cache(
        method: str,
        url: str,
        options: typing.Dict[str, typing.Any],
        cache_dir: typing.Union[str, None],
        retries: int,
        ) -> requests.Response:
    """ Make a request, potentially using a cache. """

    response: typing.Union[requests.Response, None] = None
    if (cache_dir is not None):
        response = _cache_lookup(method, url, options, cache_dir)

    if (response is None):
        # Try once and then the number of allowed retries.
        attempt_count = 1 + retries

        errors = []
        for attempt_index in range(attempt_count):
            if (attempt_index > 0):
                # Wait before the next retry.
                time.sleep(attempt_index * RETRY_BACKOFF_SECS)

            try:
                response = requests.request(method, url, **options)  # pylint: disable=missing-timeout
                break
            except Exception as ex:
                errors.append(ex)

        if (len(errors) > 0):
            raise edq.core.errors.RetryError(f"Network request failed after {attempt_count} tries.", retry_errors = errors)

    return response

def _cache_lookup(
        method: str,
        url: str,
        options: typing.Dict[str, typing.Any],
        cache_dir: str,
        ) -> typing.Union[requests.Response, None]:
    """ Attempt to lookup an exchange from the cache. """

    if (not os.path.isdir(cache_dir)):
        _logger.warning("Cache dir does not exist or is not a dir: '%s'.", cache_dir)
        return None

    cache_dir = os.path.abspath(cache_dir)

    server = _ensure_cache_server(cache_dir)

    # Create a URL that points to the cache server.
    parts = urllib.parse.urlparse(url)
    cache_url = parts._replace(scheme = 'http', netloc = f"127.0.0.1:{server.port}").geturl()

    response = requests.request(method, cache_url, **options)  # pylint: disable=missing-timeout
    if (response.status_code == http.HTTPStatus.NOT_FOUND):
        return None

    return response

def _ensure_cache_server(cache_dir: str) -> edq.net.exchangeserver.HTTPExchangeServer:
    """
    Ensure that a cache server is runner on the specified dir.
    Return the cache server.
    """

    server = _cache_servers.get(cache_dir, None)
    if (server is not None):
        return server

    edq.util.dirent.mkdir(cache_dir)

    server = edq.net.exchangeserver.HTTPExchangeServer()
    server.load_exchanges_dir(cache_dir)
    server.start()
    atexit.register(_cleanup_cache_server, cache_dir)

    _cache_servers[cache_dir] = server

    return server

def _cleanup_cache_server(cache_dir: str) -> None:
    """ Stop a cache server and remove it from the mapping. """

    server = _cache_servers.get(cache_dir, None)
    if (server is None):
        return

    server.stop()
    del _cache_servers[cache_dir]

def _clear_cache_servers() -> None:
    """ Stop and remove any cache servers. """

    for cache_dir in list(_cache_servers.keys()):
        _cleanup_cache_server(cache_dir)

def _disable_https_verification() -> None:
    """ Disable checking the SSL certificate for HTTPS requests. """

    global _module_makerequest_options  # pylint: disable=global-statement

    if (_module_makerequest_options is None):
        _module_makerequest_options = {}

    _module_makerequest_options['verify'] = False

    # Ignore insecure warnings.
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
