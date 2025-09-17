import os
import typing

import edq.testing.httpserver

THIS_DIR: str = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
TEST_EXCHANGES_DIR: str = os.path.join(THIS_DIR, "testdata", "http", 'exchanges')

class HTTPTestServerTest(edq.testing.httpserver.HTTPServerTest):
    """ Test the HTTP test server. """

    @classmethod
    def setup_server(cls, server: edq.testing.httpserver.HTTPTestServer) -> None:
        edq.testing.httpserver.HTTPServerTest.setup_server(server)
        server.load_exchanges_dir(TEST_EXCHANGES_DIR)

    def test_exchange_matching_base(self):
        """ Test matching exchanges against queries. """

        # {<file basename no ext>: exchange, ...}
        exchanges = {os.path.splitext(os.path.basename(exchange.source_path))[0]: exchange for exchange in self._server.get_exchanges()}

        # TEST - Cases for POST: multipart vs urlencoded

        # [(target, query, match?, hint substring), ...]
        test_cases = [
            # Base
            (
                exchanges['simple'],
                edq.testing.httpserver.HTTPExchange(
                    method = 'GET',
                    url = 'simple',
                ),
                {},
                True,
                None,
            ),

            # Params
            (
                exchanges['simple_params'],
                edq.testing.httpserver.HTTPExchange(
                    method = 'GET',
                    url = 'simple',
                    parameters = {
                        'a': '1',
                        'b': '2',
                    },
                ),
                {},
                True,
                None,
            ),

            # Params, skip missing.
            (
                exchanges['simple'],
                exchanges['simple_params'],
                {
                    'params_to_skip': ['a', 'b'],
                },
                True,
                None,
            ),

            # Headers, skip missing.
            (
                exchanges['simple'],
                exchanges['simple_headers'],
                {
                    'headers_to_skip': ['a'],
                },
                True,
                None,
            ),

            # Param, skip unmatching.
            (
                exchanges['simple_params'],
                edq.testing.httpserver.HTTPExchange(
                    method = 'GET',
                    url = 'simple',
                    parameters = {
                        'a': '1',
                        'b': 'ZZZ',
                    },
                ),
                {
                    'params_to_skip': ['b'],
                },
                True,
                None,
            ),

            # Varaints
            (
                exchanges['simple_params'],
                exchanges['simple_urlparams'],
                {},
                True,
                None,
            ),
            (
                exchanges['simple_post_params'],
                exchanges['simple_post_urlparams'],
                {},
                True,
                None,
            ),
            (
                exchanges['specialcase_listparams_url'],
                exchanges['specialcase_listparams_explicit'],
                {},
                True,
                None,
            ),
            (
                exchanges['simple'],
                exchanges['simple_headers'],
                {
                    'match_headers': False,
                },
                True,
                None,
            ),

            # Misses

            # Missed method.
            (
                exchanges['simple'],
                edq.testing.httpserver.HTTPExchange(
                    method = 'POST',
                    url = 'simple',
                ),
                {},
                False,
                'method does not match',
            ),
            (
                exchanges['simple'],
                exchanges['simple_post'],
                {},
                False,
                'method does not match',
            ),

            # Missed URL path.
            (
                exchanges['simple'],
                edq.testing.httpserver.HTTPExchange(
                    method = 'GET',
                    url = 'ZZZ',
                ),
                {},
                False,
                'URL path does not match',
            ),

            # Missed URL anchor.
            (
                exchanges['simple'],
                edq.testing.httpserver.HTTPExchange(
                    method = 'GET',
                    url = 'simple#1',
                ),
                {},
                False,
                'URL anchor does not match',
            ),

            # Missed number of params.
            (
                exchanges['simple'],
                edq.testing.httpserver.HTTPExchange(
                    method = 'GET',
                    url = 'simple',
                    parameters = {'a': '1'},
                ),
                {},
                False,
                'Number of parameters does not match',
            ),
            (
                exchanges['simple_post'],
                exchanges['simple_post_params'],
                {},
                False,
                'Number of parameters does not match',
            ),
            (
                exchanges['simple_post'],
                exchanges['simple_post_urlparams'],
                {},
                False,
                'Number of parameters does not match',
            ),

            # Missed param value.
            (
                exchanges['simple_params'],
                edq.testing.httpserver.HTTPExchange(
                    method = 'GET',
                    url = 'simple',
                    parameters = {
                        'a': '1',
                        'b': 'ZZZ',
                    },
                ),
                {},
                False,
                "Parameter 'b' has a non-matching value",
            ),

            # Missed number of headers.
            (
                exchanges['simple'],
                exchanges['simple_headers'],
                {
                    'match_headers': True,
                },
                False,
                'Number of headers does not match',
            ),

            # Missed header value.
            (
                exchanges['simple_headers'],
                edq.testing.httpserver.HTTPExchange(
                    method = 'GET',
                    url = 'simple',
                    headers = {
                        'a': 'ZZZ',
                    },
                ),
                {
                    'match_headers': True,
                },
                False,
                "Header 'a' has a non-matching value",
            ),

            # Param, with skip.
            (
                exchanges['simple_params'],
                edq.testing.httpserver.HTTPExchange(
                    method = 'GET',
                    url = 'simple',
                    parameters = {
                        'a': '1',
                        'b': 'ZZZ',
                    },
                ),
                {
                    'params_to_skip': ['a'],
                },
                False,
                "Parameter 'b' has a non-matching value",
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            (target, query, match_options, expected_match, hint_substring) = test_case
            base_name = os.path.splitext(os.path.basename(target.source_path))[0]

            with self.subTest(msg = f"Case {i} ('{base_name}'):"):
                actual_match, hint = target.match(query, **match_options)

                self.assertEqual(expected_match, actual_match, f"Match status does not agree (hint: '{hint}').")

                if (hint is not None):
                    if (hint_substring is None):
                        self.fail(f"Unexpected hint: '{hint}'.")

                    self.assertIn(hint_substring, hint, 'Hint is not as expected.')
                elif (hint_substring is not None):
                    self.fail(f"Did not get expected hint: '{hint_substring}'.")

    def test_exchanges_base(self):
        """ Test making a request with each of the exchanges. """

        for (i, exchange) in enumerate(self._server.get_exchanges()):
            base_name = os.path.splitext(os.path.basename(exchange.source_path))[0]
            with self.subTest(msg = f"Case {i} ({base_name}):"):
                self.assert_exchange(exchange, exchange)
