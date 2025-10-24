import argparse
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

    global_config_path = os.path.join(temp_dir, 'empty-dir')
    edq.util.dirent.mkdir(global_config_path)

    path_empty_config = os.path.join(temp_dir, 'empty-config')
    edq.util.dirent.mkdir(path_empty_config)
    edq.util.json.dump_path(
        {},
        os.path.join(path_empty_config, edq.core.config.DEFAULT_CONFIG_FILENAME),
    )

    path_non_empty_config = os.path.join(temp_dir, 'non-empty-config')
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
        Test that the 'set' command creates configuration files and writes the specified configuration correctly.
        """

        # [(set cli arguments, expected result, error substring), ...]
        test_cases = [
            # Invalid Option

            # Empty Key
            (
                {
                    "config_to_set": ["=user@test.edulinq.org"],
                },
                [],
                "Found an empty configuration option key associated with the value 'user@test.edulinq.org'.",
            ),

            # Missing '='
            (
                {
                    "config_to_set": ["useruser@test.edulinq.org"],
                },
                [],
                "Configuration options must be provided in the format `<key>=<value>` when passed via the CLI.",
            ),

            # Local Config

            # No Config
            (
                {
                    "config_to_set": ["user=user@test.edulinq.org"],
                },
                [
                    {
                        "path": edq.core.config.DEFAULT_CONFIG_FILENAME,
                        "data": {"user": "user@test.edulinq.org"},
                    },
                ],
                None,
            ),

            # Empty Config
            (
                {
                    "config_to_set": ["user=user@test.edulinq.org"],
                    "_config_params": {
                        edq.core.config.LOCAL_CONFIG_PATH_KEY: os.path.join("empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                    },
                },
                [
                    {
                        "path": os.path.join("empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                        "data": {"user": "user@test.edulinq.org"},
                    },
                ],
                None,
            ),

            # Multiple Configs
            (
                {
                    "config_to_set": ["user=user@test.edulinq.org", "pass=password123"],
                    "_config_params": {
                        edq.core.config.LOCAL_CONFIG_PATH_KEY: os.path.join("empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                    },
                },
                [
                    {
                        "path": os.path.join("empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                        "data": {
                            "user": "user@test.edulinq.org",
                            "pass": "password123",
                        },
                    },
                ],
                None,
            ),

            # Non Empty Config
            (
                {
                    "config_to_set": ["pass=password123"],
                    "_config_params": {
                        edq.core.config.LOCAL_CONFIG_PATH_KEY: os.path.join("non-empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                    },
                    "write_local": True,
                },
                [
                    {
                        "path": os.path.join("non-empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                        "data": {"user": "user@test.edulinq.org", "pass": "password123"},
                    },
                ],
                None,
            ),

            # Global Config

            # No Config
            (
                {
                    "config_to_set": ["user=user@test.edulinq.org"],
                    "write_global": True,
                    "_config_params": {
                        edq.core.config.GLOBAL_CONFIG_PATH_KEY: os.path.join('empty-dir', edq.core.config.DEFAULT_CONFIG_FILENAME)
                    }
                },
                [
                    {
                        "path": os.path.join('empty-dir', edq.core.config.DEFAULT_CONFIG_FILENAME),
                        "data": {"user": "user@test.edulinq.org"},
                    },
                ],
                None,
            ),

            # Empty Config
            (
                {
                    "config_to_set": ["user=user@test.edulinq.org"],
                    "write_global": True,
                    "_config_params": {
                        edq.core.config.GLOBAL_CONFIG_PATH_KEY: os.path.join("empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME)
                    }
                },
                [
                    {
                        "path": os.path.join("empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                        "data": {"user": "user@test.edulinq.org"},
                    },
                ],
                None,
            ),

            # Multiple Configs
            (
                {
                    "config_to_set": ["user=user@test.edulinq.org", "pass=password123"],
                    "write_global": True,
                    "_config_params": {
                        edq.core.config.GLOBAL_CONFIG_PATH_KEY: os.path.join("empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME)
                    }
                },
                [
                    {
                        "path": os.path.join("empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                        "data": {
                            "user": "user@test.edulinq.org",
                            "pass": "password123",
                        },
                    },
                ],
                None,
            ),

            # Non Empty Config
            (
                {
                    "config_to_set": ["pass=password123"],
                    "_config_params": {
                        edq.core.config.GLOBAL_CONFIG_PATH_KEY: os.path.join("non-empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                    },
                    "write_global": True,
                },
                [
                    {
                        "path": os.path.join("non-empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                        "data": {"user": "user@test.edulinq.org", "pass": "password123"},
                    },
                ],
                None,
            ),

            # File Config

            # Non Existent File
            (
                {
                    "config_to_set": ["user=user@test.edulinq.org"],
                    "write_file_path": os.path.join("non-existent", "path", edq.core.config.DEFAULT_CONFIG_FILENAME),
                },
                [
                    {
                        "path": os.path.join("non-existent", "path", edq.core.config.DEFAULT_CONFIG_FILENAME),
                        "data": {"user": "user@test.edulinq.org"},
                    },
                ],
                None,
            ),

            # Empty Config
            (
                {
                    "config_to_set": ["user=user@test.edulinq.org"],
                    "write_file_path": os.path.join("empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                },
                [
                    {
                        "path": os.path.join("empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                        "data": {"user": "user@test.edulinq.org"},
                    },
                ],
                None,
            ),

            # Multiple Configs
            (
                {
                    "config_to_set": ["user=user@test.edulinq.org", "pass=password123"],
                    "write_file_path": os.path.join("empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                },
                [
                    {
                        "path": os.path.join("empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                        "data": {
                            "user": "user@test.edulinq.org",
                            "pass": "password123",
                        },
                    },
                ],
                None,
            ),

            # Non Empty Config
            (
                {
                    "config_to_set": ["pass=password123"],
                    "write_file_path": os.path.join("non-empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                },
                [
                    {
                        "path": os.path.join("non-empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                        "data": {"user": "user@test.edulinq.org", "pass": "password123"},
                    },
                ],
                None,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            cli_arguments, expected_result, error_substring = test_case

            with self.subTest(msg = f"Case {i}"):
                temp_dir = create_test_dir(temp_dir_prefix = "edq-test-config-set-")

                config_params = cli_arguments.get("_config_params", {})
                filename = config_params.get(edq.core.config.FILENAME_KEY, edq.core.config.DEFAULT_CONFIG_FILENAME)

                set_args = argparse.Namespace(
                    write_local = cli_arguments.get("write_local", False),
                    write_global = cli_arguments.get("write_global", False),
                    write_file_path = cli_arguments.get("write_file_path", None),
                    config_to_set = cli_arguments.get("config_to_set"),
                    _config_params = {
                        edq.core.config.LOCAL_CONFIG_PATH_KEY: config_params.get(edq.core.config.LOCAL_CONFIG_PATH_KEY, None),
                        edq.core.config.GLOBAL_CONFIG_PATH_KEY: config_params.get(
                            edq.core.config.GLOBAL_CONFIG_PATH_KEY,
                            os.path.join(temp_dir, 'empty-dir', filename),
                        ),
                        edq.core.config.FILENAME_KEY: filename
                    }
                )

                previous_work_directory = os.getcwd()
                os.chdir(temp_dir)

                try:
                    edq.cli.config.set.run_cli(set_args)
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

                for file in expected_result:
                    write_file_path = file.get("path")
                    write_file_path = os.path.join(temp_dir, write_file_path)

                    if (not edq.util.dirent.exists(write_file_path)):
                        self.fail(f"Expected file does not exist at path: {write_file_path}")

                    data_actual = edq.util.json.load_path(write_file_path)

                    self.assertJSONDictEqual(data_actual, file.get("data"))
