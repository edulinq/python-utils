import os

import edq.testing.unittest
import edq.util.config
import edq.util.dirent

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
CONFIGS_DIR = os.path.join(THIS_DIR, "testdata", "configs")

class TestConfig(edq.testing.unittest.BaseTest):
    """ Test basic operations on configs. """

    def test_get_tiered_config_base(self):
        """ Test that configs are loaded correctly from the file system with the correct tier. """

        # [(work directory, expected config, expected source, extra arguments), ...]
        test_cases = [
            (
                # Global Config: Custom global config path.
                "empty-dir",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = "<global config file>",
                        path = os.path.join("TEMP_DIR", "global", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    )
                },
                {
                    "global_config_path": os.path.join("TEMP_DIR", "global", edq.util.config.DEFAULT_CONFIG_FILENAME ),
                    "local_config_root_cutoff": "TEMP_DIR"
                }
            ),
            (
                # Local Config: Custom config file in current directory.
                "custom-name",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = "<local config file>",
                        path = os.path.join("TEMP_DIR", "custom-name", "new-edq-config.json" )
                    )
                },
                {
                    "config_file_name": "new-edq-config.json",
                    "local_config_root_cutoff": "TEMP_DIR"
                }
            ),
            (
                # Local Config: Default config file in current directory.
                "simple",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = "<local config file>",
                        path = os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    )
                },
                {
                    "local_config_root_cutoff": "TEMP_DIR"
                }
            ),
            (
                # Local Config: Legacy config file in current directory.
                "old-name",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = "<local config file>",
                        path = os.path.join("TEMP_DIR", "old-name", "config.json")
                    )
                },
                {
                    "legacy_config_file_name": "config.json",
                    "local_config_root_cutoff": "TEMP_DIR"
                }
            ),
            (
                # Local Config: Default config file in an ancestor directory.
                os.path.join("nested", "nest1", "nest2a"),
                {
                    "server": "http://test.edulinq.org"
                },
                {
                    "server": edq.util.config.ConfigSource(
                        label = "<local config file>",
                        path = os.path.join("TEMP_DIR", "nested", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    )
                },
                {
                    "local_config_root_cutoff": "TEMP_DIR"
                }
            ),
            (
                # Local Config: All variations.
                os.path.join("nested", "nest1", "nest2b"),
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = "<local config file>",
                        path = os.path.join("TEMP_DIR", "nested", "nest1", "nest2b", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    )
                },
                {   "legacy_config_file_name": "config.json",
                    "local_config_root_cutoff": "TEMP_DIR"
                }
            ),
            (
                # CLI Provided Config: Distinct keys.
                "empty-dir",
                {
                    "user": "user@test.edulinq.org",
                    "server": "http://test.edulinq.org"
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = "<cli config file>",
                        path = os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    ),
                    "server": edq.util.config.ConfigSource(
                        label = "<cli config file>",
                        path = os.path.join("TEMP_DIR", "nested", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    )
                },
                {
                    "cli_arguments": {
                        edq.util.config.CONFIG_PATHS_KEY: [
                            os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME),
                            os.path.join("TEMP_DIR", "nested", edq.util.config.DEFAULT_CONFIG_FILENAME)
                        ]
                    },
                    "local_config_root_cutoff": "TEMP_DIR"
                }
            ),
            (
                # CLI Provided Config: Overriding keys.
                "empty-dir",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = "<cli config file>",
                        path = os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    )
                },
                {
                    "cli_arguments": {
                        edq.util.config.CONFIG_PATHS_KEY: [
                            os.path.join("TEMP_DIR", "custom-name", "new-edq-config.json"),
                            os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME)
                        ]
                    },
                    "local_config_root_cutoff": "TEMP_DIR"
                }
            ),
            (
                # CLI Bare Options: CLI arguments only (direct key: value).
                "empty-dir",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": edq.util.config.ConfigSource(label = "<cli argument>")
                },
                {
                    "cli_arguments": {
                        "user": "user@test.edulinq.org"
                    },
                    "local_config_root_cutoff": "TEMP_DIR"
                }
            ),
            (
                # CLI Bare Options: Skip keys functionally.
                "empty-dir",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": edq.util.config.ConfigSource(label = "<cli argument>")
                },
                {
                    "cli_arguments": {
                        "user": "user@test.edulinq.org",
                        "pass": "user"
                    },
                    "skip_keys": [
                        "pass"
                    ],
                    "local_config_root_cutoff": "TEMP_DIR"
                }
            ),
            (
                # Combination: Local Config + Global Config
                "simple",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = "<local config file>",
                        path = os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME)
                    )
                },
                {
                    "global_config_path": os.path.join("global", edq.util.config.DEFAULT_CONFIG_FILENAME),
                    "local_config_root_cutoff": "TEMP_DIR"
                }
            ),
            (
                # Combination: CLI Provided Config + Local Config
                "simple",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = "<cli config file>",
                        path = os.path.join("TEMP_DIR", "old-name", "config.json")
                    )
                },
                {
                    "cli_arguments": {
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("TEMP_DIR", "old-name", "config.json")]
                    },
                    "local_config_root_cutoff": "TEMP_DIR"
                }
            ),
            (
                # Combination: CLI Bare Options + CLI Provided Config
                "empty-dir",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": edq.util.config.ConfigSource(label = "<cli argument>")
                },
                {
                    "cli_arguments": {
                        "user": "user@test.edulinq.org",
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("TEMP_DIR", "simple", edq.util.config.DEFAULT_CONFIG_FILENAME)]
                    },
                    "local_config_root_cutoff": "TEMP_DIR"
                }
            ),
            (
                # Combination: CLI Bare Options + CLI Provided Config + Local Config + Global Config
                os.path.join("nested", "nest1", "nest2b"),
                {
                    "user": "user@test.edulinq.org",
                    "pass": "user"
                },
                {
                    "user": edq.util.config.ConfigSource(
                        label = "<cli config file>",
                        path = os.path.join("TEMP_DIR", "old-name", "config.json")
                    ),
                    "pass": edq.util.config.ConfigSource(label = "<cli argument>")
                },
                {
                    "cli_arguments": {
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("TEMP_DIR", "old-name", "config.json")],
                        "pass": "user",
                        "server": "http://test.edulinq.org"
                    },
                    "skip_keys": [
                        "server",
                        edq.util.config.CONFIG_PATHS_KEY
                    ],
                    "global_config_path": os.path.join("TEMP_DIR", "global", edq.util.config.DEFAULT_CONFIG_FILENAME),
                    "local_config_root_cutoff": "TEMP_DIR"
                }
            )
        ]

        for (i, test_case) in enumerate(test_cases):
            (test_work_dir, expected_config, expected_source, extra_args) = test_case

            with self.subTest(msg = f"Case {i} ('{test_work_dir}'):"):
                temp_dir = edq.util.dirent.get_temp_dir(prefix = "edq-test-config-")

                _replace_placeholders_dict(extra_args, "TEMP_DIR", temp_dir)

                cli_arguments = extra_args.get("cli_arguments", None)
                if (cli_arguments is not None):
                    config_paths = cli_arguments.get(edq.util.config.CONFIG_PATHS_KEY, None)
                    if (config_paths is not None):
                        _replace_placeholders_list(config_paths, "TEMP_DIR", temp_dir)

                edq.util.dirent.copy_contents(CONFIGS_DIR, temp_dir)

                previous_work_directory = os.getcwd()
                initial_work_directory = os.path.join(temp_dir, test_work_dir)
                os.chdir(initial_work_directory)

                try:
                    (actual_configs, actual_sources) = edq.util.config.get_tiered_config(**extra_args)
                finally:
                    os.chdir(previous_work_directory)

                for (key, value) in actual_sources.items():
                    if value.path is not None:
                        value.path = value.path.replace(temp_dir, "TEMP_DIR")
                        actual_sources[key] = value

                self.assertJSONDictEqual(expected_config, actual_configs)
                self.assertJSONDictEqual(expected_source, actual_sources)

def _replace_placeholders_dict(data, old, new):
    for (key, value) in data.items():
        if (isinstance(value, str)):
            if (old in value):
                data[key] = value.replace(old, new)

def _replace_placeholders_list(data, old, new):
    for (i, path) in enumerate(data):
        data[i] = path.replace(old, new)
