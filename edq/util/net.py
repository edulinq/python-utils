import email.message
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
DEFAULT_PORT_SEARCH_WAIT_SEC: float = 0.01

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

    raise ValueError(f"Could not find open port in [{start_port}, {end_port}].")

def parse_request_body_data(
        request_handler: http.server.BaseHTTPRequestHandler,
        ) -> typing.Tuple[typing.Dict[str, typing.Any], typing.Dict[str, bytes]]:
    """ Parse data and files from an HTTP request body. """

    data: typing.Dict[str, typing.Any] = {}
    files: typing.Dict[str, bytes] = {}

    length = int(request_handler.headers.get('Content-Length', 0))
    if (length == 0):
        return data, files

    content_type = request_handler.headers.get('Content-Type', '')
    raw_content = request_handler.rfile.read(length)

    if (content_type in ['', 'application/x-www-form-urlencoded']):
        data = parse_query_string(raw_content.decode(edq.util.dirent.DEFAULT_ENCODING).strip())
        return data, files

    if (content_type.startswith('multipart/form-data')):
        decoder = requests_toolbelt.multipart.decoder.MultipartDecoder(
            raw_content, content_type, encoding = edq.util.dirent.DEFAULT_ENCODING)

        for multipart_section in decoder.parts:
            values = parse_content_dispositions(multipart_section.headers)

            name = values.get('name', None)
            if (name is None):
                raise ValueError("Could not find name for multipart section.")

            # Look for a "filename" field to indicate a multipart section is a file.
            # The file's desired name is still in "name", but an alternate name is in "filename".
            if ('filename' in values):
                filename = values.get('name', '')
                if (filename == ''):
                    raise ValueError("Unable to find filename for multipart section.")

                files[filename] = multipart_section.content
            else:
                # Normal Parameter
                data[name] = multipart_section.text

        return data, files

    raise ValueError(f"Unknown content type: '{content_type}'.")

def parse_content_dispositions(headers: email.message.EmailMessage) -> typing.Dict[str, typing.Any]:
    """ Parse a request's content dispositions from headers. """

    values = {}
    for (key, value) in headers.items():
        if (isinstance(key, bytes)):
            key = key.decode(edq.util.dirent.DEFAULT_ENCODING)

        if (isinstance(value, bytes)):
            value = value.decode(edq.util.dirent.DEFAULT_ENCODING)

        key = key.strip().lower()
        if (key != 'content-disposition'):
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

def parse_query_string(text: str,
        replace_single_lists: bool = True,
        ) -> typing.Dict[str, typing.Any]:
    """
    Parse a query string (like urllib.parse.parse_qs()), and normalize the result.
    If specified, lists with single values (as returned from urllib.parse.parse_qs()) will be replaced with the single value.
    """

    results = urllib.parse.parse_qs(text)
    for (key, value) in results.items():
        if (replace_single_lists and (len(value) == 1)):
            results[key] = value[0]  # type: ignore[assignment]

    return results
