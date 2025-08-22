import os

import edq.testing.unittest
import edq.util.config
import edq.util.dirent
import edq.util.json

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
CONFIGS_DIR = os.path.join(THIS_DIR, "testdata", "configs")

def creat_test_dir(temp_dir_prefix: str) -> str:
    """
    Creat a temp dir and populate it with dirents for testing.

    This test data directory is laid out as:
    .
    ├── custom-name
    |   └── custom-edq-config.json
    ├── dir-config
    │   └── edq-config.json
    ├── empty
    │   └── edq-config.json
    ├── empty-dir
    ├── global
    │   └── edq-config.json
    ├── malformatted
    │   └── edq-config.json
    ├── nested
    │   ├── edq-config.json
    │   └── nest1
    │       ├── nest2a
    │       └── nest2b
    │           ├── config.json
    │           └── edq-config.json
    ├── old-name
    │   ├── config.json
    │   └── nest1
    │       └── nest2
    └── simple
        └── edq-config.json
    """

    temp_dir = edq.util.dirent.get_temp_dir(prefix = temp_dir_prefix)

    empty_config_dir_path = os.path.join(temp_dir, "empty")
    edq.util.dirent.mkdir(empty_config_dir_path)
    edq.util.json.dump_path({}, os.path.join(empty_config_dir_path,  edq.util.config.DEFAULT_CONFIG_FILENAME))

    custome_name_config_dir_path = os.path.join(temp_dir, "custom-name")
    edq.util.dirent.mkdir(custome_name_config_dir_path)
    edq.util.json.dump_path({"user": "user@test.edulinq.org"}, os.path.join(custome_name_config_dir_path, "custom-edq-config.json"))

    edq.util.dirent.mkdir(os.path.join(temp_dir, "dir-config", "edq-config.json"))
    edq.util.dirent.mkdir(os.path.join(temp_dir, "empty-dir"))

    global_config_dir_path = os.path.join(temp_dir, "global")
    edq.util.dirent.mkdir(global_config_dir_path)
    edq.util.json.dump_path({"user": "user@test.edulinq.org"}, os.path.join(global_config_dir_path, edq.util.config.DEFAULT_CONFIG_FILENAME))

    old_name_config_dir_path = os.path.join(temp_dir, "old-name")
    edq.util.dirent.mkdir(os.path.join(old_name_config_dir_path, "nest1", "nest2"))
    edq.util.json.dump_path({"user": "user@test.edulinq.org"}, os.path.join(old_name_config_dir_path, "config.json"))

    nested_dir_path = os.path.join(temp_dir, "nested")
    edq.util.dirent.mkdir(os.path.join(nested_dir_path, "nest1", "nest2a"))
    edq.util.dirent.mkdir(os.path.join(nested_dir_path, "nest1", "nest2b"))

    edq.util.json.dump_path({"server": "http://test.edulinq.org"}, os.path.join(nested_dir_path, edq.util.config.DEFAULT_CONFIG_FILENAME))
    edq.util.json.dump_path({"user": "user@test.edulinq.org"}, os.path.join(nested_dir_path, "nest1", "nest2b","config.json"))
    edq.util.json.dump_path(
        {"user": "user@test.edulinq.org"},
        os.path.join(nested_dir_path, "nest1", "nest2b", edq.util.config.DEFAULT_CONFIG_FILENAME)
    )

    # Malformatted JSONs
    simple_config_dir_path = os.path.join(temp_dir, "simple")
    edq.util.dirent.mkdir(simple_config_dir_path)
    edq.util.dirent.write_file(
        os.path.join(simple_config_dir_path, edq.util.config.DEFAULT_CONFIG_FILENAME),
        '{\n"user": "user@test.edulinq.org",\n}'
    )

    malformatted_config_dir_path = os.path.join(temp_dir, "malformatted")
    edq.util.dirent.mkdir(malformatted_config_dir_path)
    edq.util.dirent.write_file(
        os.path.join(malformatted_config_dir_path, edq.util.config.DEFAULT_CONFIG_FILENAME),
        "{\nuser: user@test.edulinq.org\n}"
    )

    return temp_dir

class TestConfig(edq.testing.unittest.BaseTest):
    """ Test basic operations on configs. """

    def test_get_tiered_config_base(self):
        """
        Test that configuration files are loaded correctly from the file system with the expected tier.
        The placeholder 'TEMP_DIR' is overwritten during testing with the actual path to the directory.
        """

        # [(work directory, expected config, expected source, extra arguments, error substring), ...]
        test_cases = [
            # No Config
            (
                "empty-dir",
                {},
                {},
                {},
                None
            ),

            # Global Config

            # Custom Global Config Path
            (
                "empty-dir",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = edq.util.config.CONFIG_SOURCE_GLOBAL,
                        path = os.path.join("TEMP_DIR", "global", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    ),
                },
                {
                    "global_config_path": os.path.join("TEMP_DIR", "global", edq.util.config.DEFAULT_CONFIG_FILENAME),
                },
                None
            ),

            # Empty Config JSON
            (
                "empty-dir",
                {},
                {},
                {
                    "global_config_path": os.path.join("TEMP_DIR", "empty", edq.util.config.DEFAULT_CONFIG_FILENAME),
                },
                None
            ),

            # Directory Config JSON
            (
                "empty-dir",
                {},
                {},
                {
                    "global_config_path": os.path.join("TEMP_DIR", "dir-config", edq.util.config.DEFAULT_CONFIG_FILENAME),
                },
                None
            ),

            # Non-Existent Config JSON
            (
                "empty-dir",
                {},
                {},
                {
                    "global_config_path": os.path.join("TEMP_DIR", "empty-dir", "non-existent-config.json"),
                },
                None
            ),

            # Malformatted Config JSON
            (
                "empty-dir",
                {},
                {},
                {
                    "global_config_path": os.path.join("TEMP_DIR", "malformatted", edq.util.config.DEFAULT_CONFIG_FILENAME),
                },
                "Failed to read JSON file"
            ),

            # Local Config

            # Default config file in current directory.
            (
                "simple",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = edq.util.config.CONFIG_SOURCE_LOCAL,
                        path = os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    ),
                },
                {},
                None
            ),

            # Custom config file in current directory.
            (
                "custom-name",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = edq.util.config.CONFIG_SOURCE_LOCAL,
                        path = os.path.join("TEMP_DIR", "custom-name", "custom-edq-config.json")
                    ),
                },
                {
                    "config_file_name": "custom-edq-config.json",
                },
                None
            ),

            # Legacy config file in current directory.
            (
                "old-name",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = edq.util.config.CONFIG_SOURCE_LOCAL,
                        path = os.path.join("TEMP_DIR", "old-name", "config.json")
                    ),
                },
                {
                    "legacy_config_file_name": "config.json",
                },
                None
            ),

            # Default config file in an ancestor directory.
            (
                os.path.join("nested", "nest1", "nest2a"),
                {
                    "server": "http://test.edulinq.org",
                },
                {
                    "server": edq.util.config.ConfigSource(
                        label = edq.util.config.CONFIG_SOURCE_LOCAL,
                        path = os.path.join("TEMP_DIR", "nested", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    ),
                },
                {},
                None
            ),

            # Legacy config file in an ancestor directory.
            (
                os.path.join("old-name", "nest1", "nest2"),
                {},
                {},
                {
                    "legacy_config_file_name": "config.json",
                },
                None
            ),

            # Empty Config JSON
            (
                "empty",
                {},
                {},
                {},
                None
            ),

            # Directory Config JSON
            (
                "dir-config",
                {},
                {},
                {},
                None
            ),

            # Malformatted Config JSON
            (
                "malformatted",
                {},
                {},
                {},
                "Failed to read JSON file"
            ),

            # All 3 local config locations present at the same time.
            (
                os.path.join("nested", "nest1", "nest2b"),
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = edq.util.config.CONFIG_SOURCE_LOCAL,
                        path = os.path.join("TEMP_DIR", "nested", "nest1", "nest2b", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    )
                },
                {
                    "legacy_config_file_name": "config.json",
                },
                None
            ),

            # CLI Provided Config

            # Distinct Keys
            (
                "empty-dir",
                {
                    "user": "user@test.edulinq.org",
                    "server": "http://test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = edq.util.config.CONFIG_SOURCE_CLI,
                        path = os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    ),
                    "server": edq.util.config.ConfigSource(
                        label = edq.util.config.CONFIG_SOURCE_CLI,
                        path = os.path.join("TEMP_DIR", "nested", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    ),
                },
                {
                    "cli_arguments": {
                        edq.util.config.CONFIG_PATHS_KEY: [
                            os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME),
                            os.path.join("TEMP_DIR", "nested", edq.util.config.DEFAULT_CONFIG_FILENAME)
                        ],
                    },
                },
                None
            ),

            # Overwriting Keys
            (
                "empty-dir",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = edq.util.config.CONFIG_SOURCE_CLI,
                        path = os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    ),
                },
                {
                    "cli_arguments": {
                        edq.util.config.CONFIG_PATHS_KEY: [
                            os.path.join("TEMP_DIR", "custom-name", "custom-edq-config.json"),
                            os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME)
                        ],
                    },
                },
                None
            ),

            # Empty Config JSON
            (
                "empty-dir",
                {},
                {},
                {
                    "cli_arguments": {
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("TEMP_DIR", "empty", edq.util.config.DEFAULT_CONFIG_FILENAME)],
                    },
                },
                None
            ),

            # Directory Config JSON
            (
                "empty-dir",
                {},
                {},
                {
                    "cli_arguments": {
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("TEMP_DIR", "dir-config", edq.util.config.DEFAULT_CONFIG_FILENAME)],
                    },
                },
                "IsADirectoryError"
            ),

            # Non-Existent Config JSON
            (
                "empty-dir",
                {},
                {},
                {
                    "cli_arguments": {
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("TEMP_DIR", "empty-dir", "non-existent-config.json")],
                    },
                },
                "FileNotFoundError"
            ),

            # Malformatted Config JSON
            (
                "empty-dir",
                {},
                {},
                {
                    "cli_arguments": {
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("TEMP_DIR", "malformatted", edq.util.config.DEFAULT_CONFIG_FILENAME)],
                    },
                },
                "Failed to read JSON file"
            ),

            # CLI Bare Options:

            # CLI arguments only (direct key: value).
            (
                "empty-dir",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(label = edq.util.config.CONFIG_SOURCE_CLI_BARE),
                },
                {
                    "cli_arguments": {
                        "user": "user@test.edulinq.org"
                    },
                },
                None
            ),

            # Skip keys functionally.
            (
                "empty-dir",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(label = edq.util.config.CONFIG_SOURCE_CLI_BARE),
                },
                {
                    "cli_arguments": {
                        "user": "user@test.edulinq.org",
                        "pass": "user"
                    },
                    "skip_keys": [
                        "pass"
                    ],
                },
                None
            ),

            # Combinations

            # Global Config + Local Config
            (
                "simple",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = edq.util.config.CONFIG_SOURCE_LOCAL,
                        path = os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    ),
                },
                {
                    "global_config_path": os.path.join("TEMP_DIR", "global", edq.util.config.DEFAULT_CONFIG_FILENAME),
                },
                None
            ),

            # Global Config + CLI Provided Config
            (
                "empty-dir",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = edq.util.config.CONFIG_SOURCE_CLI,
                        path = os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    ),
                },
                {
                    "cli_arguments": {
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME)]
                    },
                    "global_config_path": os.path.join("TEMP_DIR", "global", edq.util.config.DEFAULT_CONFIG_FILENAME),
                },
                None
            ),

            # Global + CLI Bare Options
            (
                "empty-dir",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(label = edq.util.config.CONFIG_SOURCE_CLI_BARE),
                },
                {
                    "cli_arguments": {
                        "user": "user@test.edulinq.org",
                    },
                    "global_config_path": os.path.join("TEMP_DIR", "global", edq.util.config.DEFAULT_CONFIG_FILENAME),

                },
                None
            ),

            # Local Config + CLI Provided Config
            (
                "simple",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = edq.util.config.CONFIG_SOURCE_CLI,
                        path = os.path.join("TEMP_DIR", "custom-name", "custom-edq-config.json")
                    ),
                },
                {
                    "cli_arguments": {
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("TEMP_DIR", "custom-name", "custom-edq-config.json")]
                    },
                },
                None
            ),

            # Local Config + CLI Bare Options
            (
                "simple",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(label = edq.util.config.CONFIG_SOURCE_CLI_BARE),
                },
                {
                    "cli_arguments": {
                        "user": "user@test.edulinq.org"
                    },
                },
                None
            ),

            #  CLI Provided Config + CLI Bare Options
            (
                "empty-dir",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(label = edq.util.config.CONFIG_SOURCE_CLI_BARE),
                },
                {
                    "cli_arguments": {
                        "user": "user@test.edulinq.org",
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME)]
                    },
                },
                None
            ),

            # Global Config + CLI Provided Config + CLI Bare Options

            (
                "empty-dir",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(label = edq.util.config.CONFIG_SOURCE_CLI_BARE),
                },
                {
                    "cli_arguments": {
                         "user": "user@test.edulinq.org",
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME)]
                    },
                    "global_config_path": os.path.join("TEMP_DIR", "global", edq.util.config.DEFAULT_CONFIG_FILENAME),
                },
                None
            ),

            # Global Config + Local Config + CLI Bare Options
            (
                "simple",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(label = edq.util.config.CONFIG_SOURCE_CLI_BARE),
                },
                {
                    "cli_arguments": {
                        "user": "user@test.edulinq.org",
                    },
                    "global_config_path": os.path.join("TEMP_DIR", "global", edq.util.config.DEFAULT_CONFIG_FILENAME),
                },
                None
            ),

            # Global Config + Local Config + CLI Provided Config
            (
                "simple",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = edq.util.config.CONFIG_SOURCE_CLI,
                        path = os.path.join("TEMP_DIR", "custom-name", "custom-edq-config.json")
                    ),
                },
                {
                    "cli_arguments": {
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("TEMP_DIR", "custom-name", "custom-edq-config.json")],
                    },
                    "global_config_path": os.path.join("TEMP_DIR", "global", edq.util.config.DEFAULT_CONFIG_FILENAME),
                },
                None
            ),

            # Local Config + CLI Provided Config + CLI Bare Options
            (
                "simple",
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.util.config.ConfigSource(label = edq.util.config.CONFIG_SOURCE_CLI_BARE),
                },
                {
                    "cli_arguments": {
                        "user": "user@test.edulinq.org",
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("TEMP_DIR", "custom-name", "custom-edq-config.json")],
                    },
                },
                None
            ),

            # Global Config + Local Config + CLI Provided Config + CLI Bare Options
            (
                "simple",
                {
                    "user": "user@test.edulinq.org",
                    "pass": "user",
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = edq.util.config.CONFIG_SOURCE_CLI,
                        path = os.path.join("TEMP_DIR", "custom-name", "custom-edq-config.json")
                    ),
                    "pass": edq.util.config.ConfigSource(label = edq.util.config.CONFIG_SOURCE_CLI_BARE),
                },
                {
                    "cli_arguments": {
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("TEMP_DIR", "custom-name", "custom-edq-config.json")],
                        "pass": "user",
                        "server": "http://test.edulinq.org",
                    },
                    "skip_keys": [
                        "server",
                        edq.util.config.CONFIG_PATHS_KEY,
                    ],
                    "global_config_path": os.path.join("TEMP_DIR", "global", edq.util.config.DEFAULT_CONFIG_FILENAME),
                },
                None
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            (test_work_dir, expected_config, expected_source, extra_args, error_substring) = test_case

            with self.subTest(msg = f"Case {i} ('{test_work_dir}'):"):
                temp_dir = creat_test_dir(temp_dir_prefix = "edq-test-config-get-tiered-config-")

                cli_arguments = extra_args.get("cli_arguments", None)
                if (cli_arguments is not None):
                    config_paths = cli_arguments.get(edq.util.config.CONFIG_PATHS_KEY, None)
                    if (config_paths is not None):
                        _replace_placeholders_list(config_paths, "TEMP_DIR", temp_dir)

                cutoff = extra_args.get("local_config_root_cutoff", None)
                if (cutoff is None):
                    extra_args["local_config_root_cutoff"] = "TEMP_DIR"

                global_config = extra_args.get("global_config_path", None)
                if (global_config is None):
                    extra_args["global_config_path"] = os.path.join("TEMP_DIR", "empty", edq.util.config.CONFIG_PATHS_KEY)

                _replace_placeholders_dict(extra_args, "TEMP_DIR", temp_dir)

                previous_work_directory = os.getcwd()
                initial_work_directory = os.path.join(temp_dir, test_work_dir)
                os.chdir(initial_work_directory)

                try:
                    (actual_config, actual_sources) = edq.util.config.get_tiered_config(**extra_args)
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

                for (key, value) in actual_sources.items():
                    if (value.path is not None):
                        value.path = value.path.replace(temp_dir, "TEMP_DIR")
                        actual_sources[key] = value

                self.assertJSONDictEqual(expected_config, actual_config)
                self.assertJSONDictEqual(expected_source, actual_sources)

def _replace_placeholders_dict(data_dict, old, new):
    for (key, value) in data_dict.items():
        if (isinstance(value, str)):
            if (old in value):
                data_dict[key] = value.replace(old, new)

def _replace_placeholders_list(data_list, old, new):
    for (i, path) in enumerate(data_list):
        data_list[i] = path.replace(old, new)
