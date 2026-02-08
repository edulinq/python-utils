import os

import edq.net.request
import edq.testing.unittest

THIS_DIR: str = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
TEST_EXCHANGES_DIR: str = os.path.join(THIS_DIR, "..", "testing", "testdata", "http", 'exchanges')

class TestRequest(edq.testing.unittest.BaseTest):
    """ Test HTTP requests. """

    def tearDown(self):
        """ Close any open HTTP cache servers. """

        edq.net.request._clear_cache_servers()

    def test_request_cache(self):
        """ Test making requests with a cache. """

        _, actual_body = edq.net.request.make_request("GET", "https://test.edqlinq.org/simple", cache_dir = TEST_EXCHANGES_DIR)
        self.assertEqual('simple', actual_body)
