import importlib
import importlib.util
import os
import typing
import uuid

import edq.util.dirent

_import_cache: typing.Dict[str, typing.Any] = {}
""" A cache to help avoid importing a module multiple times. """

def import_path(raw_path: str, cache: bool = True, module_name: typing.Union[str, None] = None) -> typing.Any:
    """
    Import a module from a file.
    If cache is false, then the module will not be fetched or stored in this module's cache.
    """

    path = os.path.abspath(raw_path)
    cache_key = f"PATH::{path}"

    # Check the cache before importing.
    if (cache):
        module = _import_cache.get(cache_key, None)
        if (module is not None):
            return module

    if (not edq.util.dirent.exists(path)):
        raise ValueError(f"Module path does not exist: '{raw_path}'.")

    if (not os.path.isfile(path)):
        raise ValueError(f"Module path is not a file: '{raw_path}'.")

    if (module_name is None):
        module_name = str(uuid.uuid4()).replace('-', '')

    spec = importlib.util.spec_from_file_location(module_name, path)
    if ((spec is None) or (spec.loader is None)):
        raise ValueError(f"Failed to load module specification for path: '{raw_path}'.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Store the module in the cache.
    if (cache):
        _import_cache[cache_key] = module

    return module

def import_name(module_name: str, cache: bool = True) -> typing.Any:
    """
    Import a module from a name.
    The module must already be in the system's path (sys.path).
    If cache is false, then the module will not be fetched or stored in this module's cache.
    """

    cache_key = f"NAME::{module_name}"

    # Check the cache before importing.
    if (cache):
        module = _import_cache.get(cache_key, None)
        if (module is not None):
            return module

    try:
        module = importlib.import_module(module_name)
    except ImportError as ex:
        raise ValueError(f"Unable to locate module '{module_name}'.") from ex

    # Store the module in the cache.
    if (cache):
        _import_cache[cache_key] = module

    return module
