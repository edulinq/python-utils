"""
This file standardizes how we write and read JSON.
Specifically, we try to be flexible when reading (using JSON5),
and strict when writing (using vanilla JSON).
"""

import json
import typing

import json5

import edq.util.dirent

def load(file_obj: typing.TextIO, strict: bool = False, **kwargs) -> typing.Dict[str, typing.Any]:
    """
    Load a file object/handler as JSON.
    If strict is set, then use standard Python JSON,
    otherwise use JSON5.
    """

    if (strict):
        return json.load(file_obj, **kwargs)

    return json5.load(file_obj, **kwargs)

def loads(text: str, strict: bool = False, **kwargs) -> typing.Dict[str, typing.Any]:
    """
    Load a string as JSON.
    If strict is set, then use standard Python JSON,
    otherwise use JSON5.
    """

    if (strict):
        return json.loads(text, **kwargs)

    return json5.loads(text, **kwargs)

def load_path(
        path: str,
        strict: bool = False,
        encoding: str = edq.util.dirent.DEFAULT_ENCODING,
        **kwargs) -> typing.Dict[str, typing.Any]:
    """
    Load a file path as JSON.
    If strict is set, then use standard Python JSON,
    otherwise use JSON5.
    """

    try:
        with open(path, 'r', encoding = encoding) as file:
            return load(file, strict = strict, **kwargs)
    except Exception as ex:
        raise ValueError(f"Failed to read JSON file '{path}'.") from ex

def dump(
        data: typing.Any,
        file_obj: typing.TextIO,
        sort_keys: bool = True,
        **kwargs) -> None:
    """ Dump an object as a JSON file object. """

    json.dump(data, file_obj, sort_keys = sort_keys, **kwargs)

def dumps(
        data: typing.Any,
        sort_keys: bool = True,
        **kwargs) -> str:
    """ Dump an object as a JSON string. """

    return json.dumps(data, sort_keys = sort_keys, **kwargs)

def dump_path(
        data: typing.Any,
        path: str,
        encoding: str = edq.util.dirent.DEFAULT_ENCODING,
        **kwargs) -> None:
    """ Dump an object as a JSON file. """

    with open(path, 'w', encoding = encoding) as file:
        dump(data, file, **kwargs)
