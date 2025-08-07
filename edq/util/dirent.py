import atexit
import os
import shutil
import tempfile
import uuid

DEAULT_ENCODING: str = 'utf-8'
""" The default encoding that will be used when reading and writing. """

def get_temp_path(prefix: str = '', suffix: str = '', rm: bool = True) -> str:
    """
    Get a path to a valid (but not currently existing) temp dirent.
    If rm is True, then the dirent will be attempted to be deleted on exit
    (no error will occur if the path is not there).
    """

    path = None
    while ((path is None) or os.path.exists(path)):
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

    if (not os.path.exists(path)):
        return

    if (os.path.isfile(path) or os.path.islink(path)):
        os.remove(path)
    elif (os.path.isdir(path)):
        shutil.rmtree(path)
    else:
        raise ValueError(f"Unknown type of dirent: '{path}'.")

def move(source: str, dest: str) -> None:
    """
    Move the source dirent to the given destination.
    Any existing destination will be removed before moving.
    """

    # If dest is a dir, then resolve the path.
    if (os.path.isdir(dest)):
        dest = os.path.abspath(os.path.join(dest, os.path.basename(source)))

    # Skip if this is self.
    if (os.path.exists(dest) and os.path.samefile(source, dest)):
        return

    # Create any required parents.
    os.makedirs(os.path.dirname(dest), exist_ok = True)

    # Remove any existing dest.
    if (os.path.exists(dest)):
        remove(dest)

    shutil.move(source, dest)

def copy(source: str, dest: str, dirs_exist_ok: bool = False) -> None:
    """
    Copy a file or directory into dest.
    If source is a file, then dest can be a file or dir.
    If source is a dir, it is copied as a subdirectory of dest.
    If dirs_exist_ok is true, an existing destination directory is allowed.
    """

    if (os.path.isfile(source) or os.path.islink(source)):
        os.makedirs(os.path.dirname(dest), exist_ok = True)

        try:
            shutil.copy2(source, dest, follow_symlinks = False)
        except shutil.SameFileError:
            return
    else:
        if (os.path.isdir(dest)):
            dest = os.path.join(dest, os.path.basename(source))

        shutil.copytree(source, dest, dirs_exist_ok = dirs_exist_ok, symlinks = True)

def copy_contents(source: str, dest: str) -> None:
    """
    Copy a file or the contents of a directory (excluding the top-level directory) into dest.
    For a file: `cp source dest/`
    For a dir: `cp -r source/* dest/`
    """

    source = os.path.abspath(source)

    if (os.path.isfile(source)):
        copy(source, dest)
        return

    for dirent in os.listdir(source):
        source_path = os.path.join(source, dirent)
        dest_path = os.path.join(dest, dirent)

        if (os.path.isfile(source_path) or os.path.islink(source_path)):
            copy(source_path, dest_path)
        else:
            shutil.copytree(source_path, dest_path, symlinks = True)

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
