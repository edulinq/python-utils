import argparse
import os
import typing

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

def replace_placeholders_str(unresolved_object: str, placeholder: str, replacement: str) -> str:
    """
    In-place replacement of a placeholder in a string with a given replacement.
    If the input is not a string, no changes are made and the original object is returned.
    """

    if(isinstance(unresolved_object, str)):
        unresolved_object = unresolved_object.replace(placeholder, replacement)

    return unresolved_object

def replace_placeholders_dict(unresolved_object: dict, placeholder: str, replacement: str) -> dict:
    """ Performs an in-place, recursive replacement of placeholder with replacement across all levels of a nested dictionary. """

    if(not isinstance(unresolved_object, dict)):
        raise TypeError(f"Expected unresolved object to be dict, got {type(unresolved_object).__name__}")

    for element in unresolved_object:
        if (isinstance(unresolved_object[element], dict)):
            unresolved_object[element] = replace_placeholders_dict(unresolved_object[element], placeholder = placeholder, replacement = replacement)
        if (isinstance(unresolved_object[element], str)):
            unresolved_object[element] = replace_placeholders_str(unresolved_object[element], placeholder = placeholder, replacement = replacement)

    return unresolved_object

def replace_tempdir_placeholder(
        cli_args: typing.Dict[str, typing.Union[str, typing.List, bool]],
        expected_result: typing.List,
        temp_dir_path: str,
    ) -> typing.Tuple[typing.Dict[str, typing.Union[str, typing.List]], typing.List[typing.Dict[str, typing.Union[str, typing.Dict[str, str]]]]]:
    """ Replaces all occurrences of 'TEMP_DIR' in CLI arguments and expected results with the actual temporary directory path. """


    resolved_expected_result = []
    for file in expected_result:
        set_to_file_path = file.get("path")
        data = file.get("data")
        set_to_file_path = replace_placeholders_str(set_to_file_path, 'TEMP_DIR', temp_dir_path)
        resolved_expected_result.append({
            "path": set_to_file_path,
            "data": data
        })

    resolved_cli_args = replace_placeholders_dict(cli_args, 'TEMP_DIR', temp_dir_path)
    return resolved_cli_args, resolved_expected_result

class TestSetConfig(edq.testing.unittest.BaseTest):
    """ Test basic functionality of set config. """

    def test_set_base(self):
        """
        Test that the 'set' command creates configuration files and writes the specified configuration correctly.
        'TEMP_DIR' gets replaced with actual temp dir path when testing.
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
                        "path": os.path.join('TEMP_DIR', edq.core.config.DEFAULT_CONFIG_FILENAME),
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
                        edq.core.config.LOCAL_CONFIG_PATH_KEY: os.path.join("TEMP_DIR", "empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                    },
                },
                [
                    {
                        "path": os.path.join("TEMP_DIR", "empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                        "data": {"user": "user@test.edulinq.org"},
                    },
                ],
                None,
            ),

            # Non Empty Config
            (
                {
                    "config_to_set": ["pass=password123"],
                    "_config_params": {
                        edq.core.config.LOCAL_CONFIG_PATH_KEY: os.path.join("TEMP_DIR", "non-empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
                    },
                },
                [
                    {
                        "path": os.path.join("TEMP_DIR", "non-empty-config", edq.core.config.DEFAULT_CONFIG_FILENAME),
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
                    "set_is_global": True,
                },
                [
                    {
                        "path": os.path.join("TEMP_DIR", GLOBAL_DIR, edq.core.config.DEFAULT_CONFIG_FILENAME),
                        "data": {"user": "user@test.edulinq.org"},
                    },
                ],
                None,
            ),

            # File Config

            # Non Existent File
            (
                {
                    "config_to_set": ["user=user@test.edulinq.org"],
                    "set_to_file_path": os.path.join("TEMP_DIR", "non-existent", "path", edq.core.config.DEFAULT_CONFIG_FILENAME),
                },
                [
                    {
                        "path": os.path.join("TEMP_DIR", "non-existent", "path", edq.core.config.DEFAULT_CONFIG_FILENAME),
                        "data": {"user": "user@test.edulinq.org"},
                    },
                ],
                None,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            cli_arguments, expected_result, error_substring = test_case

            with self.subTest(msg = f"Case {i}"):
                temp_dir = create_test_dir(temp_dir_prefix = "edq-test-config-set-")

                (cli_arguments, expected_result) =  replace_tempdir_placeholder(cli_arguments, expected_result, temp_dir)

                config_params = cli_arguments.get("_config_params", {})
                filename = config_params.get(edq.core.config.FILENAME_KEY, edq.core.config.DEFAULT_CONFIG_FILENAME)

                set_args = argparse.Namespace(
                    set_is_local = cli_arguments.get("set_is_local", False),
                    set_is_global = cli_arguments.get("set_is_global", False),
                    set_to_file_path = cli_arguments.get("set_to_file_path", None),
                    config_to_set = cli_arguments.get("config_to_set"),
                    _config_params = {
                        edq.core.config.LOCAL_CONFIG_PATH_KEY: config_params.get(edq.core.config.LOCAL_CONFIG_PATH_KEY, None),
                        edq.core.config.GLOBAL_CONFIG_PATH_KEY: config_params.get(
                            edq.core.config.GLOBAL_CONFIG_PATH_KEY,
                            os.path.join(temp_dir, GLOBAL_DIR, filename),
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
                    set_to_file_path = file.get("path")

                    if (not edq.util.dirent.exists(set_to_file_path)):
                        self.fail(f"Expected file does not exist at path: {set_to_file_path}")

                    data_actual = edq.util.json.load_path(set_to_file_path)

                    self.assertJSONDictEqual(data_actual, file.get("data"))
