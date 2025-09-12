import typing

import edq.testing.unittest
import edq.util.json

class HTTPServerTest(edq.testing.unittest):
    """
    A unit test class that requires a testing HTTP server to be running.
    """

    @classmethod
    def setUpClass(cls):
        # TEST - Start server
        pass

    @classmethod
    def tearDownClass(cls):
        # TEST - Stop server
        pass

    # TEST
    @classmethod
    def modify_request():
        pass

    # TEST
    @classmethod
    def modify_response():
        pass

class HTTPExchangeQuery():
    """
    The components of an HTTPExcahnge that can be used to find a matching exchange.
    This object will generally be constructed from HTTPExcahnges when building a server,
    and then from incoming HTTP requests when running the test server.
    """

    # TEST - Ignore missing?

    def __eq__(self, other: object) -> bool:
        # TEST
        return False

    def __hash__(self) -> int:
        # TEST
        return 0

    def __lt__(self, other: object) -> bool:
        # TEST
        return False

class HTTPExcahnge(edq.util.json.DictConverter):
    """
    The request and response making up a full HTTP exchange.
    """

    def __init__(self) -> None:
        self.method: str = method
        """ The HTTP method for this exchange. """

        self.url_path: str = url_path
        """
        The path portion of the request URL.
        Only the path (not domain, port, params, anchor, etc) should be included.
        """

        self.url_anchor: typeing.Union[str, None] = anchor
        """
        The anchor portion of the request URL (if it exists).
        """

        if (parameters is None):
            parameters = {}

        self.parameters: typing.Dict[str, typing.Any] = parameters
        """
        The parameters/arguments for this request.
        Parameters should be provided here and not encoded into URLs,
        regardless of the request method.
        With the exception of files, all parameters should be placed here.
        """

        if (headers is None):
            headers = {}

        self.headers: typing.Dict[str, typing.Any] = headers
        """ Headers in the request. """

        if (response_headers is None):
            response_headers = {}

        self.response_headers: typing.Dict[str, typing.Any] = response_headers
        """ Headers in the response. """

        self.read_write: bool = read_write
        """
        Indicates that this exchange will change data on the server (regardless of the HTTP method).
        This field may be ignored by test servers,
        but may be observed by tools that generate or validate test data.
        """

        # TODO - Limit type? string, blob, list, dict
        self.response_body: typing.Any = response_body
        """
        The response that should be sent in this exchange.
        """

        self.json_response: bool = json_response
        """ Indicates that the response is JSON and should be converted to/from a string. """

        # TEST - This needs to be a reflection reference.
        self.modify_response: typing.Union[str, None] = modify_response
        """ If supplied, call this function to modify the response from this exchange before sending. """

        # TEST - This needs to be a reflection reference.
        self.modify_excahnge: typing.Union[str, None] = modify_excahnge
        """ If supplied, call this function to modify this exchange before saving. """

    # TEST
    def to_query(self) -> HTTPExcahngeQuery:
        # TEST
        return None

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        # TEST
        return None

    @classmethod
    def from_dict(cls, data: typing.Dict[str, typing.Any]) -> typing.Any:
        # TEST
        return None

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

    # TEST - Match headers?

    def missing_request(self, query: HTTPExcahngeQuery) -> typing.Union[HTTPExcahnge, None]:
        """
        Provide the server (specifically, child classes) one last chance to resolve an incoming HTTP request
        before the server raises an exception.
        Usually exchanges are loaded from disk, but technically a server can resolve all requests with this method.

        Exchanges returned from this method are not cached/saved.
        """

        return None

    def modify_exchanges(self, exchanges: typing.List[HTTPExcahnge]) -> typing.List[HTTPExcahnge]:
        """
        Modify any exchanges before they are saved into this server's cache.
        The returned exchanges will be saved in this server's cache.

        This method may be called multiple times with different collections of exchanges.
        """

        return exchanges
