import argparse
import os

import edq.testing.unittest
import edq.cli.config.set
import edq.core.config
import edq.util.dirent
import edq.util.json

GLOBAL_DIR: str  = 'global'
LOCAL_DIR: str = 'local'

def create_test_dir(temp_dir_prefix: str) -> str:
    """ 
    Create a temp dir and populate it with dirents for testing.

    This test data directory is laid out as:

    .
    ├── empty-config
    │   └── edq-config.json
    ├── global
    └── non-empty-config
        └── edq-config.json
    """

    temp_dir = edq.util.dirent.get_temp_dir(prefix = temp_dir_prefix, rm = False)

    global_config_path = os.path.join(temp_dir, GLOBAL_DIR)
    edq.util.dirent.mkdir(global_config_path)

    path_empty_config = os.path.join(temp_dir, "empty-config")
    edq.util.dirent.mkdir(path_empty_config)
    edq.util.json.dump_path(
        {},
        os.path.join(path_empty_config, edq.core.config.DEFAULT_CONFIG_FILENAME),
    )

    path_non_empty_config = os.path.join(temp_dir, "non-empty-config")
    edq.util.dirent.mkdir(path_non_empty_config)
    edq.util.json.dump_path(
        {"user": "user@test.edulinq.org"},
        os.path.join(path_non_empty_config, edq.core.config.DEFAULT_CONFIG_FILENAME),
    )

    return temp_dir

class TestSetConfig(edq.testing.unittest.BaseTest):
    """ Test basic functionality of set config. """

    def test_set_base(self):
        """
        Test that the set command creates configuration files and writes the specified configuration correctly.
        """

        # [(set cli arguments, expected result, error substring), ...]
        test_cases = [
            (
                {
                    "config_to_set": ["user=user@test.edulinq.org"],
                },
                (
                    {
                        "path": os.path.join("TEMP_DIR", edq.core.config.DEFAULT_CONFIG_FILENAME),
                        "data": {"user": "user@test.edulinq.org"},
                    },
                ),
                None,
            )

        ]

        for test_case in test_cases:
            temp_dir = create_test_dir(temp_dir_prefix = "edq-test-config-set-")

            cli_arguments, expected_result, error_substring = test_case

            set_args = argparse.Namespace(
                write_to_local = cli_arguments.get("write_to_local", False),
                write_to_global = cli_arguments.get("write_to_global", False),
                file_to_write = cli_arguments.get("file_to_write", None),
                config_to_set = cli_arguments.get("config_to_set"),
                _config_params = {
                    edq.core.config.LOCAL_CONFIG_PATH_KEY: cli_arguments.get(edq.core.config.LOCAL_CONFIG_PATH_KEY, None),
                    edq.core.config.FILENAME_KEY: cli_arguments.get(edq.core.config.FILENAME_KEY, edq.core.config.DEFAULT_CONFIG_FILENAME),
                    edq.core.config.GLOBAL_CONFIG_PATH_KEY: cli_arguments.get(
                        edq.core.config.GLOBAL_CONFIG_PATH_KEY,
                        os.path.join(temp_dir, GLOBAL_DIR)
                    )
                }
            )

            error_substring = None

            previous_work_directory = os.getcwd()
            os.chdir(temp_dir)

            try:
                edq.cli.config.set.run_cli(set_args)
            except Exception as ex:
                error_string = self.format_error_string(ex)

                if (error_substring is None):
                    self.fail(f"Unexpected error: '{error_string}'.")

                self.assertIn(error_substring, error_string, 'Error is not as expected.')

            finally:
                os.chdir(previous_work_directory)

            if (error_substring is not None):
                self.fail(f"Did not get expected error: '{error_substring}'.")

            for file in expected_result:
                file_path = file.get("path")
                file_path = file_path.replace('TEMP_DIR', temp_dir)

                if (not edq.util.dirent.exists(file_path)):
                    self.fail("Expected file doesn't exist.")

                data_actual = edq.util.json.load_path(file_path)

                self.assertJSONDictEqual(data_actual, file.get("data"))
