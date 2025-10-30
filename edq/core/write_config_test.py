import os

import edq.cli.config.set
import edq.core.config
import edq.testing.unittest
import edq.util.dirent
import edq.util.json

def create_test_dir(temp_dir_prefix: str) -> str:
    """
    Create a temp dir and populate it with dirents for testing.

    This test data directory is laid out as:
    .
    ├── empty-config
    │   └── edq-config.json
    ├── empty-dir
    └── non-empty-config
        └── edq-config.json
    """

    temp_dir = edq.util.dirent.get_temp_dir(prefix = temp_dir_prefix)

    edq.util.dirent.mkdir(os.path.join(temp_dir, 'empty-dir'))

    empty_config_path = os.path.join(temp_dir, 'empty-config')
    edq.util.dirent.mkdir(empty_config_path)
    edq.util.json.dump_path(
        {},
        os.path.join(empty_config_path, edq.core.config.DEFAULT_CONFIG_FILENAME),
    )

    non_empty_config_path = os.path.join(temp_dir, 'non-empty-config')
    edq.util.dirent.mkdir(non_empty_config_path)
    edq.util.json.dump_path(
        {'user': 'user@test.edulinq.org'},
        os.path.join(non_empty_config_path, edq.core.config.DEFAULT_CONFIG_FILENAME),
    )

    return temp_dir

class TestWriteConfig(edq.testing.unittest.BaseTest):
    """ Test basic functionality of write config. """

    def test_write_config_base(self):
        """
        Test that the given config is written correctly and required paths are created.
        """

        # [(write config arguments, expected result, error substring), ...]
        test_cases = [
            # Non-exisitng Config
            (
                {
                    'file_path': os.path.join('empty-dir', edq.core.config.DEFAULT_CONFIG_FILENAME),
                    'config_to_write': {'user': 'user@test.edulinq.org'},
                },
                {
                    'path': os.path.join('empty-dir', edq.core.config.DEFAULT_CONFIG_FILENAME),
                    'data': {'user': 'user@test.edulinq.org'},
                },
                None,
            ),

            # Non-exisiting Path
            (
                {
                    'file_path': os.path.join('non-exisiting-path', edq.core.config.DEFAULT_CONFIG_FILENAME),
                    'config_to_write': {'user': 'user@test.edulinq.org'},
                },
                {
                    'path': os.path.join('non-exisiting-path', edq.core.config.DEFAULT_CONFIG_FILENAME),
                    'data': {'user': 'user@test.edulinq.org'},
                },
                None,
            ),

            # Exisiting Directory Config
            (
                {
                    'file_path': 'empty-dir',
                    'config_to_write': {'user': 'user@test.edulinq.org'},
                },
                {},
                "Cannot open JSON file, expected a file but got a directory",
            ),

            # Empty Config
            (
                {
                    'file_path': os.path.join('empty-config', edq.core.config.DEFAULT_CONFIG_FILENAME),
                    'config_to_write': {'user': 'user@test.edulinq.org'},
                },
                {
                    'path': os.path.join('empty-config', edq.core.config.DEFAULT_CONFIG_FILENAME),
                    'data': {'user': 'user@test.edulinq.org'},
                },
                None,
            ),

            # Non-empty Config
            (
                {
                    'file_path': os.path.join('non-empty-config', edq.core.config.DEFAULT_CONFIG_FILENAME),
                    'config_to_write': {'pass': 'password1234'},
                },
                {
                    'path': os.path.join('non-empty-config', edq.core.config.DEFAULT_CONFIG_FILENAME),
                    'data': {'user': 'user@test.edulinq.org', 'pass': 'password1234'},
                },
                None,
            ),

            # Config Overwrite
            (
                {
                    'file_path': os.path.join('non-empty-config', edq.core.config.DEFAULT_CONFIG_FILENAME),
                    'config_to_write': {'user': 'admin@test.edulinq.org'},
                },
                {
                    'path': os.path.join('non-empty-config', edq.core.config.DEFAULT_CONFIG_FILENAME),
                    'data': {'user': 'admin@test.edulinq.org'},
                },
                None,
            ),

        ]

        for (i, test_case) in enumerate(test_cases):
            arguments, expected_result, error_substring = test_case

            with self.subTest(msg = f"Case {i}"):
                temp_dir = create_test_dir(temp_dir_prefix = "edq-test-config-set-")

                arguments['file_path'] = os.path.join(temp_dir, arguments['file_path'])

                previous_work_directory = os.getcwd()
                os.chdir(temp_dir)

                try:
                    edq.core.config.write_config_to_file(**arguments)
                except Exception as ex:
                    error_string = self.format_error_string(ex)

                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{error_string}'.")

                    self.assertIn(error_substring, error_string, 'Error is not as expected.')

                    continue
                finally:
                    os.chdir(previous_work_directory)

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")


                write_file_path = expected_result["path"]
                write_file_path = os.path.join(temp_dir, write_file_path)

                if (not edq.util.dirent.exists(write_file_path)):
                    self.fail(f"Expected file does not exist at path: {write_file_path}")

                data_actual = edq.util.json.load_path(write_file_path)
                data_expected = expected_result.get('data')

                self.assertJSONDictEqual(data_actual, data_expected)
