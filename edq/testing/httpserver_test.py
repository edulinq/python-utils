import os

import edq.testing.httpserver

THIS_DIR: str = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
TEST_EXCHANGES_DIR: str = os.path.join(THIS_DIR, "testdata", "http", 'exchanges')

class HTTPTestServerTest(edq.testing.httpserver.HTTPServerTest):
    """ Test the HTTP test server. """

    @classmethod
    def setup_server(cls, server: edq.testing.httpserver.HTTPTestServer) -> None:
        edq.testing.httpserver.HTTPServerTest.setup_server(server)
        server.load_exchanges_dir(TEST_EXCHANGES_DIR)

    def test_exchanges_base(self):
        """ Test making a request with each of the exchanges. """

        for (i, exchange) in enumerate(self._server.get_exchanges()):
            base_name = os.path.splitext(os.path.basename(exchange.source_path))[0]
            with self.subTest(msg = f"Case {i} ({base_name}):"):
                # TEST
                print(edq.util.json.dumps(exchange, indent = 4))


        ''' TEST
        # [(path, write kwargs, read kwargs, write contents, expected contents, error substring), ...]
        # All conent should be strings that will be encoded.
        test_cases = [
            # Base
            (
                "test.txt",
                {},
                {},
                "test",
                "test",
                None,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            (path, write_options, read_options, write_contents, expected_contents, error_substring) = test_case

            with self.subTest(msg = f"Case {i} ('{path}'):"):
                temp_dir = self._prep_temp_dir()
                path = os.path.join(temp_dir, path)

                if (write_contents is not None):
                    write_contents = bytes(write_contents, edq.util.dirent.DEFAULT_ENCODING)

                expected_contents = bytes(expected_contents, edq.util.dirent.DEFAULT_ENCODING)

                try:
                    edq.util.dirent.write_file_bytes(path, write_contents, **write_options)
                    actual_contents = edq.util.dirent.read_file_bytes(path, **read_options)
                except Exception as ex:
                    error_string = self.format_error_string(ex)
                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{error_string}'.")

                    self.assertIn(error_substring, error_string, 'Error is not as expected.')

                    continue

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")

                self.assertEqual(expected_contents, actual_contents)
        '''
