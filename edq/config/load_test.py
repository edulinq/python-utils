import os
import typing

import edq.config.constants
import edq.config.load
import edq.config.testing
import edq.testing.unittest

class TestLoadConfig(edq.testing.unittest.BaseTest):
    """ Test basic operations of loading configs. """

    def test_get_tiered_config_base(self) -> None:
        """
        Test that configuration files are loaded correctly from the file system with the expected tier.
        """

        temp_dir = edq.config.testing.create_test_dir(temp_dir_prefix = "edq-test-config-get-tiered-config-")

        # [(work directory, config filenames, extra arguments, expected config, expected sources, expected config options, error substring), ...]
        test_cases: typing.List[typing.Tuple[
            str,
            typing.Dict[str, typing.Any],
            typing.Dict[str, typing.Any],
            typing.Dict[str, typing.Any],
            typing.Dict[str, typing.Any],
            typing.Dict[str, typing.Any],
            typing.Union[str, None],
        ]] = [
            # No Config
            (
                "empty-dir",
                {},
                {},
                {},
                {},
                {},
                None,
            ),

            # Global Config

            # Custom Global Config Path
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_GLOBAL,
                        path = os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    ),
                },
                {
                      edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            # Empty Config JSON
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "empty", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    },
                },
                {},
                {},
                {
                    edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "empty", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            # Empty Key Config JSON
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "empty-key", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    },
                },
                {},
                {},
                {},
                "Found an empty configuration option key associated with the value 'user@test.edulinq.org'.",
            ),

            # Directory Config JSON
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "dir-config", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    },
                },
                {},
                {},
                {
                    edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "dir-config", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                "IsADirectoryError",
            ),

            # Non-Existent Config JSON
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "empty-dir", "non-existent-config.json"),
                    },
                },
                {},
                {},
                {
                    edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "empty-dir", "non-existent-config.json"),
                },
                None,
            ),

            # Malformed Config JSON
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "malformed", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    },
                },
                {},
                {},
                {},
                "Failed to read JSON file",
            ),

            # Ignore Config Option
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(
                            temp_dir, "multiple-options", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                        edq.config.constants.IGNORE_CONFIG_OPTIONS_KEY: [
                            "pass",
                        ],
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_GLOBAL,
                        path = os.path.join(temp_dir, "multiple-options", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    ),
                },
                {

                    edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "multiple-options", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            # Ignore Non-Existing Config Option
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                        edq.config.constants.IGNORE_CONFIG_OPTIONS_KEY: [
                            "non-existing-option",
                        ],
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_GLOBAL,
                        path = os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    ),
                },
                {
                    edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            # Local Config

            # Default config file in current directory.
            (
                "simple",
                {},
                {},
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_LOCAL,
                        path = os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    ),
                },
                {
                    'local_config_path': os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            # Custom config file in current directory.
            (
                "custom-name",
                {
                    'config_filename': "custom-edq-config.json",
                },
                {},
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_LOCAL,
                        path = os.path.join(temp_dir, "custom-name", "custom-edq-config.json"),
                    ),
                },
                {
                    'config_filename': "custom-edq-config.json",
                    'local_config_path': os.path.join(temp_dir, "custom-name","custom-edq-config.json"),
                },
                None,
            ),

            # Legacy config file in current directory.
            (
                "old-name",
                {
                    "legacy_config_filename": "config.json",
                },
                {},
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_LOCAL,
                        path = os.path.join(temp_dir, "old-name", "config.json"),
                    ),
                },
                {
                    'local_config_path': os.path.join(temp_dir, "old-name", "config.json"),
                },
                None,
            ),

            # Default config file in an ancestor directory.
            (
                os.path.join("nested", "nest1", "nest2a"),
                {},
                {},
                {
                    "server": "http://test.edulinq.org",
                },
                {
                    "server": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_LOCAL,
                        path = os.path.join(temp_dir, "nested", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    ),
                },
                {
                    'local_config_path': os.path.join(temp_dir, "nested", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            # Legacy config file in an ancestor directory.
            (
                os.path.join("old-name", "nest1", "nest2"),
                {
                    "legacy_config_filename": "config.json",
                },
                {},
                {},
                {},
                {},
                None,
            ),

            # Empty Config JSON
            (
                "empty",
                {},
                {},
                {},
                {},
                {
                    'local_config_path': os.path.join(temp_dir, "empty", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            # Empty Key Config JSON
            (
                "empty-key",
                {},
                {},
                {},
                {},
                {},
                "Found an empty configuration option key associated with the value 'user@test.edulinq.org'.",
            ),

            # Directory Config JSON
            (
                "dir-config",
                {},
                {},
                {},
                {},
                {},
                "IsADirectoryError",
            ),

            # Malformed Config JSON
            (
                "malformed",
                {},
                {},
                {},
                {},
                {},
                "Failed to read JSON file",
            ),

            # Ignore Config Option
            (
                "multiple-options",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.IGNORE_CONFIG_OPTIONS_KEY: [
                            "pass",
                        ],
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_LOCAL,
                        path = os.path.join(temp_dir, "multiple-options", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    ),
                },
                {
                    'local_config_path': os.path.join(temp_dir, "multiple-options", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            # Ignore Non-Existing Config Option
            (
                "simple",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.IGNORE_CONFIG_OPTIONS_KEY: [
                            "non-existing-option",
                        ],
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_LOCAL,
                        path = os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    ),
                },
                {
                    'local_config_path': os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),


            # All 3 local config locations present at the same time.
            (
                os.path.join("nested", "nest1", "nest2b"),
                {
                    "legacy_config_filename": "config.json",
                },
                {},
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_LOCAL,
                        path = os.path.join(temp_dir, "nested", "nest1", "nest2b", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    ),
                },
                {
                    'local_config_path': os.path.join(
                        temp_dir, "nested", "nest1", "nest2b",
                        edq.config.constants.DEFAULT_CONFIG_FILENAME,
                    ),
                },
                None,
            ),

            # CLI Provided Config

            # Distinct Keys
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_PATHS_KEY: [
                            os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                            os.path.join(temp_dir, "nested", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                        ],
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                    "server": "http://test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_CLI_FILE,
                        path = os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    ),
                    "server": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_CLI_FILE,
                        path = os.path.join(temp_dir, "nested", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    ),
                },
                {},
                None,
            ),

            # Overwriting Keys
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_PATHS_KEY: [
                            os.path.join(temp_dir, "custom-name", "custom-edq-config.json"),
                            os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                        ],
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_CLI_FILE,
                        path = os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    ),
                },
                {},
                None,
            ),

            # Empty Config JSON
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_PATHS_KEY: [
                            os.path.join(temp_dir, "empty", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                        ],
                    },
                },
                {},
                {},
                {},
                None,
            ),

            # Empty Key Config JSON
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_PATHS_KEY: [
                            os.path.join(temp_dir, "empty-key", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                        ],
                    },
                },
                {},
                {},
                {},
                "Found an empty configuration option key associated with the value 'user@test.edulinq.org'.",
            ),

            # Directory Config JSON
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_PATHS_KEY: [
                            os.path.join(temp_dir, "dir-config", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                        ],
                    },
                },
                {},
                {},
                {},
                "IsADirectoryError",
            ),

            # Non-Existent Config JSON
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_PATHS_KEY: [
                            os.path.join(temp_dir, "empty-dir", "non-existent-config.json"),
                        ],
                    },
                },
                {},
                {},
                {},
                "FileNotFoundError",
            ),

            # Malformed Config JSON
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_PATHS_KEY: [
                            os.path.join(temp_dir, "malformed", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                        ],
                    },
                },
                {},
                {},
                {},
                "Failed to read JSON file",
            ),

            # Ignore Config Option
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_PATHS_KEY: [
                            os.path.join(temp_dir, "multiple-options", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                        ],
                        edq.config.constants.IGNORE_CONFIG_OPTIONS_KEY: [
                            "pass",
                        ],
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_CLI_FILE,
                        path = os.path.join(temp_dir, "multiple-options", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    ),
                },
                {},
                None,
            ),

            # Ignore Non-Existing Config Option
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_PATHS_KEY: [
                            os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                        ],
                        edq.config.constants.IGNORE_CONFIG_OPTIONS_KEY: [
                            "non-existing-option",
                        ],
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_CLI_FILE,
                        path = os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    ),
                },
                {},
                None,
            ),


            # CLI Options:

            # CLI arguments only (direct key: value).
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_OPTIONS_KEY: [
                            "user=user@test.edulinq.org",
                        ],
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(label = edq.config.constants.CONFIG_SOURCE_CLI),
                },
                {},
                None,
            ),

            # Empty Config Key
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_OPTIONS_KEY: [
                            "=user@test.edulinq.org",
                        ],
                    },
                },
                {},
                {},
                {},
                "Found an empty configuration option key associated with the value 'user@test.edulinq.org'.",
            ),

            # Empty Config Value
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_OPTIONS_KEY: [
                            "user=",
                        ],
                    },
                },
                {
                    "user": "",
                },
                {
                    "user": edq.config.load.ConfigSource(label = edq.config.constants.CONFIG_SOURCE_CLI),
                },
                {},
                None,
            ),

            # Separator In Config Value
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_OPTIONS_KEY: [
                            "pass=password=1234",
                        ],
                    },
                },
                {
                    "pass": "password=1234",
                },
                {
                    "pass": edq.config.load.ConfigSource(label = edq.config.constants.CONFIG_SOURCE_CLI),
                },
                {},
                None,
            ),

            # Invalid Config Option Format
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_OPTIONS_KEY: [
                            "useruser@test.edulinq.org",
                        ],
                    },
                },
                {},
                {},
                {},
                "Invalid configuration option string 'useruser@test.edulinq.org'.",
            ),

            # Ignore Config Option
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_OPTIONS_KEY: [
                            "user=user@test.edulinq.org",
                            "pass=password1234",
                        ],
                        edq.config.constants.IGNORE_CONFIG_OPTIONS_KEY: [
                            "pass",
                        ],
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(label = edq.config.constants.CONFIG_SOURCE_CLI),
                },
                {},
                None,
            ),

            # Ignore Non-Existing Config Option
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_OPTIONS_KEY: [
                            "user=user@test.edulinq.org",
                        ],
                        edq.config.constants.IGNORE_CONFIG_OPTIONS_KEY: [
                            "non-existing-option",
                        ],
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(label = edq.config.constants.CONFIG_SOURCE_CLI),
                },
                {},
                None,
            ),

            # Combinations

            # Global Config + Local Config
            (
                "simple",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_LOCAL,
                        path = os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    ),
                },
                {
                    edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    'local_config_path': os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            # Global Config + CLI Provided Config
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_PATHS_KEY: [
                            os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                        ],
                        edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_CLI_FILE,
                        path = os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    ),
                },
                {
                    edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            # Global + CLI Bare Options
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_OPTIONS_KEY: [
                            "user=user@test.edulinq.org",
                        ],
                        edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(label = edq.config.constants.CONFIG_SOURCE_CLI),
                },
                {
                    edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            # Local Config + CLI Provided Config
            (
                "simple",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_PATHS_KEY: [
                            os.path.join(temp_dir, "custom-name", "custom-edq-config.json"),
                        ],
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_CLI_FILE,
                        path = os.path.join(temp_dir, "custom-name", "custom-edq-config.json"),
                    ),
                },
                {
                    'local_config_path': os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            # Local Config + CLI Bare Options
            (
                "simple",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_OPTIONS_KEY: [
                            "user=user@test.edulinq.org",
                        ],
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(label = edq.config.constants.CONFIG_SOURCE_CLI),
                },
                {
                    'local_config_path': os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            #  CLI Provided Config + CLI Bare Options
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_OPTIONS_KEY: [
                            "user=user@test.edulinq.org",
                        ],
                        edq.config.constants.CONFIG_PATHS_KEY: [
                            os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                        ],
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(label = edq.config.constants.CONFIG_SOURCE_CLI),
                },
                {},
                None,
            ),

            # Global Config + CLI Provided Config + CLI Bare Options
            (
                "empty-dir",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_OPTIONS_KEY: [
                            "user=user@test.edulinq.org",
                        ],
                        edq.config.constants.CONFIG_PATHS_KEY: [
                            os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                        ],
                        edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(label = edq.config.constants.CONFIG_SOURCE_CLI),
                },
                {
                    edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            # Global Config + Local Config + CLI Bare Options
            (
                "simple",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_OPTIONS_KEY: [
                            "user=user@test.edulinq.org",
                        ],
                        edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(label = edq.config.constants.CONFIG_SOURCE_CLI),
                },
                {
                    edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    'local_config_path': os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            # Global Config + Local Config + CLI Provided Config
            (
                "simple",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_PATHS_KEY: [
                            os.path.join(temp_dir, "custom-name", "custom-edq-config.json"),
                        ],
                        edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_CLI_FILE,
                        path = os.path.join(temp_dir, "custom-name", "custom-edq-config.json"),
                    ),
                },
                {
                    edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    'local_config_path': os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            # Local Config + CLI Provided Config + CLI Bare Options
            (
                "simple",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_OPTIONS_KEY: [
                            "user=user@test.edulinq.org",
                        ],
                        edq.config.constants.CONFIG_PATHS_KEY: [
                            os.path.join(temp_dir, "custom-name", "custom-edq-config.json"),
                        ],
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                },
                {
                    "user": edq.config.load.ConfigSource(label = edq.config.constants.CONFIG_SOURCE_CLI),
                },
                {
                    'local_config_path': os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),

            # Global Config + Local Config + CLI Provided Config + CLI Bare Options
            (
                "simple",
                {},
                {
                    "cli_arguments": {
                        edq.config.constants.CONFIG_PATHS_KEY: [
                            os.path.join(temp_dir, "custom-name", "custom-edq-config.json"),
                        ],
                        edq.config.constants.CONFIG_OPTIONS_KEY: [
                            "pass=password1234",
                        ],
                        edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    },
                },
                {
                    "user": "user@test.edulinq.org",
                    "pass": "password1234",
                },
                {
                    "user": edq.config.load.ConfigSource(
                        label = edq.config.constants.CONFIG_SOURCE_CLI_FILE,
                        path = os.path.join(temp_dir, "custom-name", "custom-edq-config.json"),
                    ),
                    "pass": edq.config.load.ConfigSource(label = edq.config.constants.CONFIG_SOURCE_CLI),
                },
                {
                    edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "global", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                    'local_config_path': os.path.join(temp_dir, "simple", edq.config.constants.DEFAULT_CONFIG_FILENAME),
                },
                None,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            (test_work_dir, config_filenames, extra_args, expected_config, expected_sources,  expected_config_options, error_substring) = test_case

            with self.subTest(msg = f"Case {i} ('{test_work_dir}'):"):
                edq.config.load.set_config_filename(edq.config.constants.DEFAULT_CONFIG_FILENAME)
                edq.config.load.set_legacy_config_filename(None)

                config_filename = config_filenames.get('config_filename', edq.config.constants.DEFAULT_CONFIG_FILENAME)
                edq.config.load.set_config_filename(config_filename)

                legacy_config_filename = config_filenames.get("legacy_config_filename", None)
                edq.config.load.set_legacy_config_filename(legacy_config_filename)

                cli_args = extra_args.get("cli_arguments", None)
                if cli_args is None:
                    extra_args["cli_arguments"] = {
                        edq.config.constants.GLOBAL_CONFIG_KEY: os.path.join(temp_dir, "empty", config_filename),
                    }
                else:
                    cli_global_config_path = cli_args.get(edq.config.constants.GLOBAL_CONFIG_KEY, None)
                    if cli_global_config_path is None:
                        extra_args["cli_arguments"][edq.config.constants.GLOBAL_CONFIG_KEY] = os.path.join(
                            temp_dir, "empty", config_filename,
                        )

                cutoff = extra_args.get("local_config_root_cutoff", None)
                if (cutoff is None):
                    extra_args["local_config_root_cutoff"] = temp_dir

                global_file_used = expected_config_options.get(edq.config.constants.GLOBAL_CONFIG_KEY, None)
                if (global_file_used is None):
                    expected_config_options[edq.config.constants.GLOBAL_CONFIG_KEY] =  os.path.join(
                        temp_dir, "empty", config_filename,
                    )

                local_file_used = expected_config_options.get('local_config_path', None)
                if (local_file_used is None):
                    expected_config_options['local_config_path'] = os.path.join(
                        temp_dir, test_work_dir, config_filename,
                    )

                file_name_used = expected_config_options.get('config_filename', None)
                if (file_name_used is None):
                    expected_config_options['config_filename'] = config_filename

                expected_config_info = edq.config.load.TieredConfigInfo(
                    raw_config = expected_config,
                    sources = expected_sources,
                    **expected_config_options,
                )

                previous_work_directory = os.getcwd()
                initial_work_directory = os.path.join(temp_dir, test_work_dir)
                os.chdir(initial_work_directory)

                try:
                    actual_config_info = edq.config.load.get_tiered_config(**extra_args)
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

                self.assertJSONDictEqual(actual_config_info, expected_config_info)
                self.assertJSONDictEqual(actual_config_info.application_config._extra, expected_config)
