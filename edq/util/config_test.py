import os

import edq.testing.unittest
import edq.util.config
import edq.util.dirent

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
CONFIGS_DIR = os.path.join(THIS_DIR, "testdata", "configs")

class TestConfig(edq.testing.unittest.BaseTest):
    """ Test basic operations on configs. """

    def test_base(self):
        """ Test that configs are loaded correctly from the file system with the correct tier. """

        # [(work directory, expected config, expected source, {skip keys , cli arguments, config global}), ...]
        test_cases = [
            (
                "custom-name",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": f"<local config file>::{os.path.join('TEMP_DIR', 'custom-name', 'new-edq-config.json')}"
                },
                {
                    "config_file_name": "new-edq-config.json"
                }
            ),
            (
                "simple",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": f"<local config file>::{os.path.join('TEMP_DIR', 'simple', 'edq-config.json')}"
                },
                {}
            ),
            (
                "old-name",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": f"<local config file>::{os.path.join('TEMP_DIR', 'old-name', 'config.json')}"
                },
                {}
            ),
            (
                os.path.join("nested", "nest1", "nest2a"),
                {
                    "server": "http://test.edulinq.org"
                },
                {
                    "server": f"<local config file>::{os.path.join('TEMP_DIR', 'nested', 'edq-config.json')}"
                },
                {}
            ),
            (
                os.path.join("nested", "nest1", "nest2b"),
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": f"<local config file>::{os.path.join('TEMP_DIR', 'nested', 'nest1', 'nest2b', 'edq-config.json')}"
                },
                {}
            ),
            (
                "empty-dir",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": f"<global config file>::{os.path.join('TEMP_DIR', 'global', 'edq-config.json')}"
                },
                {
                    "global_config_path": os.path.join("global", "edq-config.json")
                }
            ),
            (
                "empty-dir",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": "<cli argument>"
                },
                {
                    "cli_args": {
                        "user": "user@test.edulinq.org"
                    }
                }
            ),
            (
                "empty-dir",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": "<cli argument>"
                },
                {
                    "cli_args": {
                        "user": "user@test.edulinq.org",
                        "pass": "user"
                    },
                    "skip_keys": [
                        "pass"
                    ]
                }
            ),
            (
                "empty-dir",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": f"<cli config file>::{os.path.join('TEMP_DIR', 'simple', 'edq-config.json')}"
                },
                {
                    "cli_args": {
                        edq.util.config.CONFIG_PATHS_KEY: [
                            os.path.join("global", "edq-config.json"),
                            os.path.join("simple", "edq-config.json")
                        ]
                    }
                }
            ),
            (
                "empty-dir",
                {
                    "user": "user@test.edulinq.org",
                    "server": "http://test.edulinq.org"
                },
                {
                    "user": f"<cli config file>::{os.path.join('TEMP_DIR', 'simple', 'edq-config.json')}",
                    "server": f"<cli config file>::{os.path.join('TEMP_DIR', 'nested', 'edq-config.json')}"
                },
                {
                    "cli_args": {
                        edq.util.config.CONFIG_PATHS_KEY: [
                            os.path.join("nested", "edq-config.json"),
                            os.path.join("simple", "edq-config.json")
                        ]
                    }
                }
            ),
            (
                "simple",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": f"<local config file>::{os.path.join('TEMP_DIR', 'simple', 'edq-config.json')}"
                },
                {
                    "global_config_path": os.path.join("global", "edq-config.json")
                }
            ),
            (
                "empty-dir",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": f"<cli config file>::{os.path.join('TEMP_DIR', 'simple', 'edq-config.json')}"
                },
                {
                    "cli_args": {
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("simple", "edq-config.json")]
                    },
                    "global_config_path": os.path.join("global", "edq-config.json")
                }
            ),
            (
                "simple",
                {
                    "user": "user@test.edulinq.org"
                },
                {
                    "user": f"<cli config file>::{os.path.join('TEMP_DIR', 'old-name', 'config.json')}"
                },
                {
                    "cli_args": {
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("old-name", "config.json")]
                    },
                }
            ),
            (
                "simple",
                {
                    "user": "user@test.edulinq.org",
                    "pass": "user"
                },
                {
                    "user": f"<cli config file>::{os.path.join('TEMP_DIR', 'old-name', 'config.json')}",
                    "pass": "<cli argument>"
                },
                {
                    "cli_args": {
                        edq.util.config.CONFIG_PATHS_KEY: [os.path.join("old-name", "config.json")],
                        "pass": "user",
                        "server": "http://test.edulinq.org"
                    },
                    "skip_keys": [
                        "server",
                        edq.util.config.CONFIG_PATHS_KEY
                    ],
                    "global_config_path": os.path.join("global", "edq-config.json")
                }
            )
        ]

        for test_case in test_cases:
            (test_work_dir, expected_config, expected_source, extra_args) = test_case

            self._evaluate_test_config(
                test_work_dir, expected_config, expected_source, **extra_args
            )

    def _evaluate_test_config(
            self, test_work_dir, expected_config,
            expected_source, skip_keys = None,
            cli_args = None, global_config_path = None,
            config_file_name = None):
        """
        Prepares testing environment and normalizes cli config paths,
        global config path and expected source paths. Evaluates the given expected and
        source configs with actual get_tiered_config() output.
        """

        if (cli_args is None):
            cli_args = {}

        if (skip_keys is None):
            skip_keys = [edq.util.config.CONFIG_PATHS_KEY]

        if (config_file_name is None):
            config_file_name = edq.util.config.DEFAULT_CONFIG_FILENAME

        temp_dir = edq.util.dirent.get_temp_dir(prefix = 'edq-test-config-')

        global_config = os.path.join(temp_dir)
        if (global_config_path is not None):
            global_config = os.path.join(temp_dir, global_config_path)

        abs_config_paths = []
        config_paths = cli_args.get(edq.util.config.CONFIG_PATHS_KEY, None)
        if (config_paths is not None):
            for rel_config_path in config_paths:
                abs_config_paths.append(os.path.join(temp_dir, rel_config_path))
            cli_args[edq.util.config.CONFIG_PATHS_KEY] = abs_config_paths

        edq.util.dirent.copy_contents(CONFIGS_DIR, temp_dir)

        previous_work_directory = os.getcwd()
        initial_work_directory = os.path.join(temp_dir, test_work_dir)
        os.chdir(initial_work_directory)

        try:
            (actual_configs, actual_sources) = edq.util.config.get_tiered_config(
                cli_arguments = cli_args,
                global_config_path = global_config,
                local_config_root_cutoff = temp_dir,
                skip_keys = skip_keys,
                config_file_name = config_file_name
            )
        finally:
            os.chdir(previous_work_directory)

        for (key, value) in actual_sources.items():
            actual_sources[key] = value.replace(temp_dir, "TEMP_DIR")

        self.assertDictEqual(expected_config, actual_configs)
        self.assertDictEqual(expected_source, actual_sources)
