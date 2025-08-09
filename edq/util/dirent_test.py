import os
import unittest

import edq.util.dirent

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
TEST_BASE_DIR = os.path.join(THIS_DIR, 'testdata', 'dirent-operations')
"""
This test data directory is laid out as:
.
├── a.txt
├── dir_1
│   ├── b.txt
│   └── dir_2
│       └── c.txt
├── dir_empty
├── file_empty
├── symlinklink_a.txt -> a.txt
├── symlinklink_dir_1 -> dir_1
└── symlinklink_dir_empty -> dir_empty

Where non-empty files are filled with their filename (without the extension).
dir_empty will not exist in the repository (since it is an empty directory),
but it will be created by _prep_temp_dir().
"""

DIRENT_TYPE_DIR = 'dir'
DIRENT_TYPE_FILE = 'file'

class TestDirentOperations(unittest.TestCase):
    """ Test basic operations on dirents. """

    def test_dirent_base(self):
        """ Test that the base temp directory is properly setup. """

        temp_dir = self._prep_temp_dir()

        expected_paths = [
            ('a.txt', DIRENT_TYPE_FILE),
            ('dir_1', DIRENT_TYPE_DIR),
            (os.path.join('dir_1', 'b.txt'), DIRENT_TYPE_FILE),
            (os.path.join('dir_1', 'dir_2'), DIRENT_TYPE_DIR),
            (os.path.join('dir_1', 'dir_2', 'c.txt'), DIRENT_TYPE_FILE),
            ('dir_empty', DIRENT_TYPE_DIR),
            ('file_empty', DIRENT_TYPE_FILE),
            ('symlinklink_a.txt', DIRENT_TYPE_FILE, True),
            ('symlinklink_dir_1', DIRENT_TYPE_DIR, True),
            ('symlinklink_dir_empty', DIRENT_TYPE_DIR, True),
        ]

        self._check_existing_paths(temp_dir, expected_paths)

    def test_dirent_operations_remove(self):
        """ Test removing dirents. """

        temp_dir = self._prep_temp_dir()

        # Remove these paths in this order.
        remove_relpaths = [
            # Symlink - File
            'symlinklink_a.txt',

            # Symlink - Dir
            'symlinklink_dir_1',

            # File in Directory
            os.path.join('dir_1', 'dir_2', 'c.txt'),

            # File
            'a.txt',

            # Empty File
            'file_empty'

            # Directory
            'dir_1',

            # Empty Directory
            'dir_empty'

            # Non-Existent
            'ZZZ'
        ]

        expected_paths = [
            (os.path.join('dir_1', 'dir_2'), DIRENT_TYPE_DIR),
            ('file_empty', DIRENT_TYPE_FILE),
            # Windows has some symlink issues, so we will not check for this file.
            # ('symlinklink_dir_empty', DIRENT_TYPE_DIR, True),
        ]

        for relpath in remove_relpaths:
            path = os.path.join(temp_dir, relpath)
            edq.util.dirent.remove(path)

        self._check_nonexisting_paths(temp_dir, remove_relpaths)
        self._check_existing_paths(temp_dir, expected_paths)

    def _prep_temp_dir(self):
        temp_dir = edq.util.dirent.get_temp_dir(prefix = 'edq_test_dirent_')
        edq.util.dirent.mkdir(os.path.join(temp_dir, 'dir_empty'))
        edq.util.dirent.copy_contents(TEST_BASE_DIR, temp_dir)
        return temp_dir

    def _check_existing_paths(self, base_dir, raw_paths):
        """
        Ensure that specific paths exists, and fail the test if they do not.
        All paths should be relative to the base dir.
        Paths can be:
         - A string.
         - A two-item tuple (path, dirent type).
         - A three-item tuple (path, dirent type, is link?).
        Missing components are not defaulted, they are just not checked.
        """

        for raw_path in raw_paths:
            relpath = ''
            dirent_type = None
            is_link = None

            if (isinstance(raw_path, str)):
                relpath = raw_path
            elif (isinstance(raw_path, tuple)):
                if (len(raw_path) not in [2, 3]):
                    raise ValueError(f"Expected exactly two or three items for path check, found {len(raw_path)} items: '{raw_path}'.")

                relpath = raw_path[0]
                dirent_type = raw_path[1]

                if (len(raw_path) == 3):
                    is_link = raw_path[2]
            else:
                raise ValueError(f"Could not parse expected path ({type(raw_path)}): '{raw_path}'.")

            path = os.path.join(base_dir, relpath)

            # Check the path exists.
            if (not edq.util.dirent.exists(path)):
                self.fail(f"Expected path does not exist: '{relpath}'.")

            # Check the link status.
            if (is_link is not None):
                if (is_link != os.path.islink(path)):
                    self.fail(f"Expected path does not have a matching link status. Expected {is_link}, but is {not is_link}: '{relpath}'.")

            # Check the type of the dirent.
            if (dirent_type is not None):
                if (dirent_type == DIRENT_TYPE_DIR):
                    if (not os.path.isdir(path)):
                        self.fail(f"Expected path to be a directory, but it is not: '{relpath}'.")
                elif (dirent_type == DIRENT_TYPE_FILE):
                    if (not os.path.isfile(path)):
                        self.fail(f"Expected path to be a file, but it is not: '{relpath}'.")
                else:
                    raise ValueError(f"Unknown dirent type '{dirent_type}' for path: '{relpath}'.")

    def _check_nonexisting_paths(self, base_dir, raw_paths):
        """
        Ensure that specific paths do not exists, and fail the test if they do exist.
        All paths should be relative to the base dir.
        Unlike _check_existing_paths(), paths should only be strings.
        """

        for relpath in raw_paths:
            path = os.path.join(base_dir, relpath)

            if (edq.util.dirent.exists(path)):
                self.fail(f"Path exists when it should not: '{relpath}'.")
