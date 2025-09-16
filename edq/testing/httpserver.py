import glob
import http.server
import os
import threading
import time
import typing
import urllib.parse

import requests

import edq.testing.unittest
import edq.util.dirent
import edq.util.json
import edq.util.net

SERVER_THREAD_START_WAIT_SEC = 0.05
SERVER_THREAD_REAP_WAIT_SEC = 0.15

ALLOWED_METHODS: typing.List[str] = [
    'GET',
    'POST',
    'PUT'
]

class HTTPExchange(edq.util.json.DictConverter):
    """
    The request and response making up a full HTTP exchange.
    """

    # TEST - Response body has not been worked out.

    def __init__(self,
            method: str = 'GET',
            url: typing.Union[str, None] = None,
            url_path: typing.Union[str, None] = None,
            url_anchor: typing.Union[str, None] = None,
            parameters: typing.Union[typing.Dict[str, typing.Any], None] = None,
            files: typing.Union[typing.List[str], None] = None,
            headers: typing.Union[typing.Dict[str, typing.Any], None] = None,
            response_code: int = http.HTTPStatus.OK,
            response_headers: typing.Union[typing.Dict[str, typing.Any], None] = None,
            response_body: typing.Union[typing.Any, None] = None,
            json_body: bool = False,
            read_write: bool = False,
            modify_exchange: typing.Union[str, None] = None,
            source_path: typing.Union[str, None] = None,
            **kwargs: typing.Any) -> None:
        method = method.upper()
        if (method not in ALLOWED_METHODS):
            raise ValueError(f"Got unknown/disallowed method: '{method}'.")

        self.method: str = method
        """ The HTTP method for this exchange. """

        url_path, url_anchor, parameters = self._parse_url_components(url, url_path, url_anchor, parameters)

        self.url_path: str = url_path
        """
        The path portion of the request URL.
        Only the path (not domain, port, params, anchor, etc) should be included.
        """

        self.url_anchor: typing.Union[str, None] = url_anchor
        """
        The anchor portion of the request URL (if it exists).
        """

        self.parameters: typing.Dict[str, typing.Any] = parameters
        """
        The parameters/arguments for this request.
        Parameters should be provided here and not encoded into URLs,
        regardless of the request method.
        With the exception of files, all parameters should be placed here.
        """

        if (files is None):
            files = []

        # TEST
        self.files: typing.List[str] = files

        if (headers is None):
            headers = {}

        self.headers: typing.Dict[str, typing.Any] = headers
        """ Headers in the request. """

        self.response_code: int = response_code
        """ The HTTP status code of the response. """

        if (response_headers is None):
            response_headers = {}

        self.response_headers: typing.Dict[str, typing.Any] = response_headers
        """ Headers in the response. """

        # TODO - Limit type? string, blob, list, dict
        self.response_body: typing.Any = response_body
        """
        The response that should be sent in this exchange.
        """

        self.json_body: bool = json_body
        """ Indicates that the response is JSON and should be converted to/from a string. """

        self.read_write: bool = read_write
        """
        Indicates that this exchange will change data on the server (regardless of the HTTP method).
        This field may be ignored by test servers,
        but may be observed by tools that generate or validate test data.
        """

        # TEST - This needs to be a reflection reference.
        self.modify_exchange: typing.Union[str, None] = modify_exchange
        """ If supplied, call this function to modify this exchange before saving. """

        self.source_path: typing.Union[str, None] = source_path
        """
        The path that this exchange was loaded from (if it was loaded from a file).
        This value should never be serialized, but can be useful for testing.
        """

    def _parse_url_components(self,
            url: typing.Union[str, None] = None,
            url_path: typing.Union[str, None] = None,
            url_anchor: typing.Union[str, None] = None,
            parameters: typing.Union[typing.Dict[str, typing.Any], None] = None,
            ) -> typing.Tuple[str, typing.Union[str, None], typing.Dict[str, typing.Any]]:
        """
        Parse out all URL-based components from raw inputs.
        The URL's path and anchor can either be supplied separately, or as part of the full given URL.
        If content is present in both places, they much match (or an error will be raised).
        Query parameters may be provided in the full URL,
        but will be overwritten by any that are provided separately.
        Any information from the URL aside from the path, anchor/fragment, and query will be ignored.
        Note that path parameters (not query parameters) will be ignored.
        The final url path, url anchor, and parameters will be returned.
        """

        # Do base initialization and cleanup.

        if (url_path is not None):
            url_path = url_path.strip()
            if (url_path == ''):
                url_path = None
            else:
                url_path = url_path.lstrip('/')

        if (url_anchor is not None):
            url_anchor = url_anchor.strip()
            if (url_anchor == ''):
                url_anchor = None
            else:
                url_anchor = url_anchor.lstrip('#')

        if (parameters is None):
            parameters = {}

        # Parse the URL (if present).

        if ((url is not None) and (url.strip() != '')):
            parts = urllib.parse.urlparse(url)

            # Handle the path.

            path = parts.path.lstrip('/')

            if ((url_path is not None) and (url_path != path)):
                raise ValueError(f"Mismatched URL paths where supplied implicitly ('{path}') and explicitly ('{url_path}').")

            url_path = path

            # Check the optional anchor/fragment.

            if (parts.fragment != ''):
                fragment = parts.fragment.lstrip('#')

                if ((url_anchor is not None) and (url_anchor != fragment)):
                    raise ValueError(f"Mismatched URL anchors where supplied implicitly ('{fragment}') and explicitly ('{url_anchor}').")

                url_anchor = fragment

            # Check for any parameters.

            url_params = urllib.parse.parse_qs(parts.query)
            for (key, value) in url_params.items():
                # urllib.parse.parse_qs() will always return values as lists.
                # If there is only one item, then pull that value out of the list.
                if (len(value) == 1):
                    value = value[0]

                if (key not in parameters):
                    parameters[key] = value

        return url_path, url_anchor, parameters

    def match(self, query: 'HTTPExchange',
            match_headers: bool = False,
            headers_to_skip: typing.Union[typing.List[str], None] = None,
            params_to_skip: typing.Union[typing.List[str], None] = None,
            **kwargs: typing.Any) -> typing.Tuple[bool, typing.Union[str, None]]:
        """
        Check if this exchange matches the query exchange.
        If they match, `(True, None)` will be returned.
        If they do not match, `(False, <hint>)` will be returned, where `<hint>` points to where the mismatch is.

        Note that this is not an equality check,
        as a query exchange is often missing the response components.
        This method is often invoked the see if an incoming HTTP request (the query) matches an existing exchange.
        """

        if (query.method != self.method):
            return False, f"HTTP method does not match (query = {query.method}, target = {self.method})."

        if (query.url_path != self.url_path):
            return False, f"URL path does not match (query = {query.url_path}, target = {self.url_path})."

        if (query.url_anchor != self.url_anchor):
            return False, f"URL anchor does not match (query = {query.url_anchor}, target = {self.url_anchor})."

        if (headers_to_skip is None):
            headers_to_skip = []

        if (params_to_skip is None):
            params_to_skip = []

        if (match_headers):
            match, hint = self._match_dict('header', self.headers, query.headers, headers_to_skip)
            if (not match):
                return False, hint

        match, hint = self._match_dict('parameter', self.parameters, query.parameters, params_to_skip)
        if (not match):
            return False, hint

        return True, None

    def _match_dict(self, label: str,
            target_dict: typing.Dict[str, typing.Any], query_dict: typing.Dict[str, typing.Any],
            keys_to_skip: typing.List[str],
            ) -> typing.Tuple[bool, typing.Union[str, None]]:
        """ A subcheck in match(), specifically for a dictionary. """

        query_keys = set(query_dict.keys()) - set(keys_to_skip)
        target_keys = set(target_dict.keys()) - set(keys_to_skip)

        if (len(query_keys) != len(target_keys)):
            return False, f"Number of {label}s does not match (query = {len(query_keys)}, target = {len(target_keys)})."

        for key in sorted(query_keys):
            query_value = query_dict[key]
            target_value = target_dict[key]

            if (query_value != target_value):
                return False, f"{label.title()} '{key}' has a non-matching value (query = '{query_value}', target = '{target_value}')."

        return True, None

    def get_url(self) -> str:
        """ Get the URL path and anchor combined. """

        url = self.url_path

        if (self.url_anchor is not None):
            url += ('#' + self.url_anchor)

        return url

    def make_request(self, base_url: str, raise_on_status: bool = True) -> requests.Response:
        """ Perform the HTTP request described by this exchange. """

        url = f"{base_url}/{self.get_url()}"
        response = requests.request(self.method, url, headers = self.headers, data = self.parameters)

        if (raise_on_status):
            response.raise_for_status()

        return response

    def match_response(self, response: requests.Response) -> typing.Tuple[bool, typing.Union[str, None]]:
        """
        Check if this exchange matches the given response.
        If they match, `(True, None)` will be returned.
        If they do not match, `(False, <hint>)` will be returned, where `<hint>` points to where the mismatch is.
        """

        if (self.response_code != response.status_code):
            return False, f"http status code does match (expected: {self.response_code}, actual: {response.status_code})"

        body = None
        if (self.json_body):
            body = response.json()
        else:
            body = response.text

        if (self.response_body != body):
            return False, 'body does not match'

        # TEST - Match Headers

        # TEST - Match Files

        return True, None

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return vars(self)

    @classmethod
    def from_dict(cls, data: typing.Dict[str, typing.Any]) -> typing.Any:
        return HTTPExchange(**data)

class HTTPTestServer():
    """
    An HTTP server meant for testing.
    This server is generally meant to already know about all the requests that will be made to it,
    and all the responses it should make in reaction to those respective requests.
    This allows the server to respond very quickly, and makes it ideal for testing.
    This makes it easy to mock external services for testing.

    If a request is not found in the predefined requests,
    then missing_request() will be called.
    If a response is still not available (indicated by a None return from missing_request()),
    then an error will be raised.
    """

    # TEST - Option for matching against headers?
    # TEST - Option for matching without specific params.

    def __init__(self, match_options: typing.Union[typing.Dict[str, typing.Any], None] = None) -> None:
        self.port: typing.Union[None, int] = None
        """
        The active port this server is using.
        Will not be set until the server has been started.
        """

        self._http_server: typing.Union[http.server.HTTPServer, None] = None
        """ The HTTP server listening for connections. """

        self._thread: typing.Union[threading.Thread, None] = None
        """ The thread running the HTTP server. """

        self._exchanges: typing.Dict[str, typing.Dict[typing.Union[str, None], typing.Dict[str, typing.List[HTTPExchange]]]] = {}
        """
        The HTTP exchanges (requests+responses) that this server knows about.
        Exchanges are stored in layers to help make errors for missing requests easier.
        Exchanges are stored as: {url_path: {anchor: {method: [exchange, ...]}, ...}, ...}.
        """

        if (match_options is None):
            match_options = {}

        self._match_options: typing.Dict[str, typing.Any] = match_options.copy()
        """ Options to use when matching HTTP exchanges. """

    def get_exchanges(self) -> typing.List[HTTPExchange]:
        """
        Get a shallow list of all the exchanges in this server.
        Ordering is not guaranteed.
        """

        exchanges = []

        for url_exchanges in self._exchanges.values():
            for anchor_exchanges in url_exchanges.values():
                for method_exchanges in anchor_exchanges.values():
                    exchanges += method_exchanges

        return exchanges

    def start(self) -> None:
        """ Start this server in a thread and return the port. """

        # Created a nested handler to bind this server object to the handler.
        class NestedHTTPHandler(_TestHTTPHandler):
            _server = self

        self.port = edq.util.net.find_open_port()
        self._http_server = http.server.HTTPServer(('', self.port), NestedHTTPHandler)

        # Use a barrier to ensure that the server thread has started.
        server_startup_barrier = threading.Barrier(2)

        def _run_server(server, server_startup_barrier):
            server_startup_barrier.wait()
            server._http_server.serve_forever(poll_interval = 0.1)
            server._http_server.server_close()

        self._thread = threading.Thread(target = _run_server, args = (self, server_startup_barrier))
        self._thread.start()

        # Wait for the server to startup.
        server_startup_barrier.wait()
        time.sleep(SERVER_THREAD_START_WAIT_SEC)

    def stop(self) -> None:
        """ Stop this server. """

        self.port = None

        if (self._http_server is not None):
            self._http_server.shutdown()
            self._http_server = None

        if (self._thread is not None):
            if (self._thread.is_alive()):
                self._thread.join(SERVER_THREAD_REAP_WAIT_SEC)

            self._thread = None

    def missing_request(self, query: HTTPExchange) -> typing.Union[HTTPExchange, None]:
        """
        Provide the server (specifically, child classes) one last chance to resolve an incoming HTTP request
        before the server raises an exception.
        Usually exchanges are loaded from disk, but technically a server can resolve all requests with this method.

        Exchanges returned from this method are not cached/saved.
        """

        return None

    def modify_exchanges(self, exchanges: typing.List[HTTPExchange]) -> typing.List[HTTPExchange]:
        """
        Modify any exchanges before they are saved into this server's cache.
        The returned exchanges will be saved in this server's cache.

        This method may be called multiple times with different collections of exchanges.
        """

        return exchanges

    def lookup_exchange(self,
            query: HTTPExchange,
            match_options: typing.Union[typing.Dict[str, typing.Any], None] = None,
            ) -> typing.Tuple[typing.Union[HTTPExchange, None], typing.Union[str, None]]:
        """
        Lookup the query exchange to see if it exists in this server.
        If a match exists, the matching exchange (likely a full version of the query) will be returned along with None.
        If a match does not exist, a None will be returned along with a message indicating how the query missed
        (e.g., the URL was matched, but the method was not).
        """

        if (match_options is None):
            match_options = {}

        hint_display = query.url_path
        target = self._exchanges

        if (query.url_path not in target):
            return None, f"Could not find matching URL path for '{hint_display}'."

        hint_display = f"{query.url_path}#{query.url_anchor}"
        target = target[query.url_path]

        if (query.url_anchor not in target):
            return None, f"Found URL path, but could not find matching anchor for '{hint_display}'."

        hint_display = f"{query.url_path}#{query.url_anchor} ({query.method})"
        target = target[query.url_anchor]

        if (query.method not in target):
            return None, f"Found URL, but could not find matching method for '{hint_display}'."

        params = list(sorted(query.parameters.keys()))
        hint_display = f"{query.url_path}#{query.url_anchor} ({query.method}, param keys = {params})"
        target = target[query.method]

        full_match_options = self._match_options.copy()
        full_match_options.update(match_options)

        for exchange in target:
            match, _ = exchange.match(query, **full_match_options)
            if (match):
                return exchange, None

        return None, f"Found matching URL and method, but could not find matching params for '{hint_display}'."

    def load_exchange(self, exchange: HTTPExchange) -> None:
        """ Load an exchange into this server. """

        if (exchange is None):
            raise ValueError("Cannot load a None exchange.")

        target = self._exchanges
        if (exchange.url_path not in target):
            target[exchange.url_path] = {}

        target = target[exchange.url_path]
        if (exchange.url_anchor not in target):
            target[exchange.url_anchor] = {}

        target = target[exchange.url_anchor]
        if (exchange.method not in target):
            target[exchange.method] = []

        target = target[exchange.method]
        target.append(exchange)

    def load_exchange_file(self, path: str) -> None:
        exchange = edq.util.json.load_object_path(path, HTTPExchange)
        exchange.source_path = os.path.abspath(path)
        self.load_exchange(exchange)

    def load_exchanges_dir(self, base_dir: str, extension: str = '.json') -> None:
        paths = list(sorted(glob.glob(os.path.join(base_dir, "**", f"*{extension}"), recursive = True)))
        for path in paths:
            self.load_exchange_file(path)

class _TestHTTPHandler(http.server.BaseHTTPRequestHandler):
    _server: typing.Union[HTTPTestServer, None] = None
    """ The test server this handler is being used for. """

    # Quiet logs.
    def log_message(self, format, *args):
        return

    def do_POST(self):
        if (self._server is None):
            raise ValueError("Server has not been initialized.")

        request_data, request_files = edq.util.net.parse_POST_data(self)

        exchange = self._get_exchange('POST', parameters = request_data, files = request_files)

        code = exchange.response_code
        headers = exchange.response_headers
        payload = exchange.response_body

        if (payload is None):
            payload = ''

        self.send_response(code)
        for (key, value) in headers:
            self.send_header(key, value)
        self.end_headers()

        self.wfile.write(payload.encode(edq.util.dirent.DEFAULT_ENCODING))

    def do_GET(self):
        if (self._server is None):
            raise ValueError("Server has not been initialized.")

        raw_content = urllib.parse.urlparse(self.path).query
        request_data = urllib.parse.parse_qs(raw_content)

        exchange = self._get_exchange('GET', parameters = request_data)

        code = exchange.response_code
        headers = exchange.response_headers
        payload = exchange.response_body

        if (payload is None):
            payload = ''

        self.send_response(code)
        for (key, value) in headers:
            self.send_header(key, value)
        self.end_headers()

        self.wfile.write(payload.encode(edq.util.dirent.DEFAULT_ENCODING))

    def _get_exchange(self, method: str,
            parameters: typing.Union[typing.Dict[str, typing.Any], None] = None,
            files: typing.Union[typing.List[str], None] = None,
            ) -> HTTPExchange:
        """ Get the matching exchange or raise an error. """

        query = HTTPExchange(method = method,
                url = self.path, headers = self.headers,
                parameters = parameters, files = files)

        exchange, hint = self._server.lookup_exchange(query)
        if (exchange is None):
            raise ValueError(f"Failed to lookup exchange: '{hint}'.")

        return exchange

class HTTPServerTest(edq.testing.unittest.BaseTest):
    """
    A unit test class that requires a testing HTTP server to be running.
    """

    _server: typing.Union[HTTPTestServer, None] = None

    @classmethod
    def setUpClass(cls):
        HTTPServerTest._server = HTTPTestServer()
        cls.setup_server(HTTPServerTest._server)
        HTTPServerTest._server.start()

    @classmethod
    def tearDownClass(cls):
        HTTPServerTest._server.stop()
        HTTPServerTest._server = None

    @classmethod
    def setup_server(cls, server: HTTPTestServer) -> None:
        """ An opportunity for child classes to configure the test server before starting it. """

    def get_server_url(self) -> str:
        """ Get the URL for this test's test server. """

        if (self._server.port is None):
            raise ValueError("Test server port has not been set.")

        return f"http://127.0.0.1:{HTTPServerTest._server.port}"

    def assert_exchange(self, request: HTTPExchange, response: HTTPExchange,
            base_url: typing.Union[str, None] = None,
            ) -> requests.Response:
        """
        Assert that the result of making the provided request matches the provided response.
        The same HTTPExchange may be supplied for both the request and response.
        By default, the server's URL will be used as the base URL.
        The full response will be returned (if no assertion is raised).
        """

        if (base_url is None):
            base_url = self.get_server_url()

        full_response = request.make_request(base_url)

        match, hint = response.match_response(full_response)
        if (not match):
            raise AssertionError(f"Exchange does not match: '{hint}'.")

        return full_response
