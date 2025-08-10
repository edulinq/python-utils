"""
Operations relating to directory entries (dirents).

These operations are designed for clarity and compatibility, not performance.

Only directories, files, and links will be handled.
Other types of dirents may result in an error being raised.

In general, all recursive operations do not follow symlinks by default and instead treat the link as a file.
"""

import atexit
import os
import shutil
import tempfile
import uuid

DEAULT_ENCODING: str = 'utf-8'
""" The default encoding that will be used when reading and writing. """

def exists(path: str) -> bool:
    """
    Check if a path exists.
    This will transparently call os.path.lexists(),
    which will include broken links.
    """

    return os.path.lexists(path)

def get_temp_path(prefix: str = '', suffix: str = '', rm: bool = True) -> str:
    """
    Get a path to a valid (but not currently existing) temp dirent.
    If rm is True, then the dirent will be attempted to be deleted on exit
    (no error will occur if the path is not there).
    """

    path = None
    while ((path is None) or exists(path)):
        path = os.path.join(tempfile.gettempdir(), prefix + str(uuid.uuid4()) + suffix)

    if (rm):
        atexit.register(remove, path)

    return path

def get_temp_dir(prefix: str = '', suffix: str = '', rm: bool = True) -> str:
    """
    Get a temp directory.
    The directory will exist when returned.
    """

    path = get_temp_path(prefix = prefix, suffix = suffix, rm = rm)
    mkdir(path)
    return path

def mkdir(path: str) -> None:
    """
    Make a directory (including any required parent directories).
    Does not complain if the directory (or parents) already exist.
    """

    os.makedirs(path, exist_ok = True)

def remove(path: str) -> None:
    """
    Remove the given path.
    The path can be of any type (dir, file, link),
    and does not need to exist.
    """

    if (not exists(path)):
        return

    if (os.path.isfile(path) or os.path.islink(path)):
        os.remove(path)
    elif (os.path.isdir(path)):
        shutil.rmtree(path)
    else:
        raise ValueError(f"Unknown type of dirent: '{path}'.")

def same_dirent(a: str, b: str):
    """
    Check if two paths represent the same dirent.
    If either (or both) paths do not exist, false will be returned.
    If either paths are links, they are resolved before checking
    (so a link and the target file are considered the "same").
    """

    return (exists(a) and exists(b) and os.path.samefile(a, b))

def move(raw_source: str, raw_dest: str, no_clobber: bool = False) -> None:
    """
    Move the source dirent to the given destination.
    Any existing destination will be removed before moving.
    """

    source = os.path.abspath(raw_source)
    dest = os.path.abspath(raw_dest)

    if (not exists(source)):
        raise ValueError(f"No such file or directory: '{raw_source}'.")

    # If dest is a dir, then resolve the path.
    if (os.path.isdir(dest)):
        dest = os.path.abspath(os.path.join(dest, os.path.basename(source)))

    # Skip if this is self.
    if (same_dirent(source, dest)):
        return

    # Check for clobber.
    if (exists(dest)):
        if (no_clobber):
            raise ValueError(f"Destination of move already exists: '{raw_dest}'.")

        remove(dest)

    # Create any required parents.
    os.makedirs(os.path.dirname(dest), exist_ok = True)

    shutil.move(source, dest)

def copy(raw_source: str, raw_dest: str, no_clobber: bool = False) -> None:
    """
    Copy a dirent or directory to a destination.

    The destination will be overwritten if it exists (and no_clober is false).
    For copying the contents of a directory INTO another directory, use copy_contents().

    No copy is made if the source and dest refer to the same dirent.
    """

    source = os.path.abspath(raw_source)
    dest = os.path.abspath(raw_dest)

    if (same_dirent(source, dest)):
        return

    if (not exists(source)):
        raise ValueError(f"Source of copy does not exist: '{raw_source}'.")

    if (exists(dest)):
        if (no_clobber):
            raise ValueError(f"Destination of copy already exists: '{raw_dest}'.")

        remove(dest)

    mkdir(os.path.dirname(dest))

    if (os.path.isfile(source)):
        shutil.copy2(source, dest, follow_symlinks = False)
    elif (os.path.islink(source)):
        # shutil.copy2() can generally handle links, but Windows is inconsistent (between 3.11 and 3.12) on link handling.
        link_target = os.readlink(source)
        os.symlink(link_target, dest)
    elif (os.path.isdir(source)):
        mkdir(dest)

        for child in sorted(os.listdir(source)):
            copy(os.path.join(raw_source, child), os.path.join(raw_dest, child))
    else:
        raise ValueError(f"Source of copy is not a dir, fie, or link: '{raw_source}'.")

def copy_contents(raw_source: str, raw_dest: str, no_clobber: bool = False) -> None:
    """
    Copy a file or the contents of a directory (excluding the top-level directory itself) into a destination.
    If the destination exists, it must be a directory.

    The source and destination should not be the same file.

    For a file, this is equivalent to `mkdir -p dest && cp source dest`
    For a dir, this is equivalent to `mkdir -p dest && cp -r source/* dest`
    """

    source = os.path.abspath(raw_source)
    dest = os.path.abspath(raw_dest)

    if (same_dirent(source, dest)):
        raise ValueError(f"Source and destination of contents copy cannot be the same: '{raw_source}'.")

    if (exists(dest) and (not os.path.isdir(dest))):
        raise ValueError(f"Destination of contents copy exists and is not a dir: '{raw_dest}'.")

    mkdir(dest)

    if (os.path.isfile(source) or os.path.islink(source)):
        copy(source, os.path.join(dest, os.path.basename(source)), no_clobber = no_clobber)
    elif (os.path.isdir(source)):
        for child in sorted(os.listdir(source)):
            copy(os.path.join(raw_source, child), os.path.join(raw_dest, child), no_clobber = no_clobber)
    else:
        raise ValueError(f"Source of contents copy is not a dir, fie, or link: '{raw_source}'.")

def read_file(path: str, strip: bool = True, encoding: str = DEAULT_ENCODING) -> str:
    """ Read the contents of a file. """

    with open(path, 'r', encoding = encoding) as file:
        contents = file.read()

    if (strip):
        contents = contents.strip()

    return contents

def write_file(path: str, contents: str, strip: bool = True, newline: bool = True, encoding: str = DEAULT_ENCODING) -> None:
    """
    Write the contents of a file.
    Any existing file will be truncated.
    """

    if (contents is None):
        contents = ''

    if (strip):
        contents = contents.strip()

    if (newline):
        contents += "\n"

    with open(path, 'w', encoding = encoding) as file:
        file.write(contents)
