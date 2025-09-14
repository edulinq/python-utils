import errno
import http.server
import socket
import time
import typing
import urllib.parse

import requests_toolbelt.multipart.decoder

import edq.util.dirent

DEFAULT_START_PORT: int = 30000
DEFAULT_END_PORT: int = 40000
DEFAULT_PORT_SEARCH_WAIT_SEC: float = 0.15

def find_open_port(
        start_port: int = DEFAULT_START_PORT, end_port: int = DEFAULT_END_PORT,
        wait_time: float = DEFAULT_PORT_SEARCH_WAIT_SEC) -> int:
    """
    Find an open port on this machine within the given range (inclusive).
    If no open port is found, an error is raised.
    """

    for port in range(start_port, end_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('127.0.0.1', port))

            # Explicitly close the port and wait a short amount of time for the port to clear.
            # This should not be required because of the socket option above,
            # but the cost is small.
            sock.close()
            time.sleep(DEFAULT_PORT_SEARCH_WAIT_SEC)

            return port
        except socket.error as ex:
            sock.close()

            if (ex.errno == errno.EADDRINUSE):
                continue

            # Unknown error.
            raise ex

    raise ValueError("Could not find open port in [%d, %d]." % (start_port, end_port))

# TEST - Files? Binary?
def parse_POST_data(requestHandler: http.server.BaseHTTPRequestHandler) -> typing.Tuple[typing.Dict[str, typing.Any], typing.Dict[str, bytes]]:
    """ Parse data and files from an HTTP POST request. """

    data = {}
    files = {}

    content_type = requestHandler.headers.get('Content-Type', '')
    length = int(requestHandler.headers['Content-Length'])
    raw_content = requestHandler.rfile.read(length)

    if (content_type == 'application/x-www-form-urlencoded'):
        request = urllib.parse.parse_qs(raw_content.decode(edq.util.dirent.DEFAULT_ENCODING))
        data = json.loads(request[autograder.api.constants.API_REQUEST_JSON_KEY][0])
        return data, files

    if (content_type.startswith('multipart/form-data')):
        decoder = requests_toolbelt.multipart.decoder.MultipartDecoder(
            raw_content, content_type, encoding = edq.util.dirent.DEFAULT_ENCODING)

        for part in decoder.parts:
            values = parse_content_dispositions(part.headers)

            if (values.get('name', ()) == autograder.api.constants.API_REQUEST_JSON_KEY):
                data = json.loads(part.text)
            else:
                # Assume everything else is a file.
                filename = values.get('filename', '')
                if (filename == ''):
                    raise ValueError("Unable to find filename for request.")

                # TEST
                files[filename] = values

        return data, files

    raise ValueError("Unknown content type: '%s'." % (content_type))

# TEST - Binary handing?
def parse_content_dispositions(headers):
    """ Parse a request's content dispositions from headers. """

    values = {}
    for (key, value) in headers.items():
        key = key.decode(edq.util.dirent.DEFAULT_ENCODING).strip()
        value = value.decode(edq.util.dirent.DEFAULT_ENCODING)

        if (key.lower() != 'content-disposition'):
            continue

        # The Python stdlib recommends using the email library for this parsing,
        # but I have not had a good experience with it.
        for part in value.strip().split(';'):
            part = part.strip()

            parts = part.split('=')
            if (len(parts) != 2):
                continue

            cd_key = parts[0].strip()
            cd_value = parts[1].strip().strip('"')

            values[cd_key] = cd_value

    return values
