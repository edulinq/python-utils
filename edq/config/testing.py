import os

import edq.config.constants
import edq.testing.cli
import edq.testing.unittest
import edq.util.dirent
import edq.util.json

def create_test_dir(temp_dir_prefix: str) -> str:
    """
    Create a temp dir and populate it with dirents for testing.

    This test data directory is laid out as:
    .
    ├── custom-name
    │   └── custom-edq-config.json
    ├── dir-config
    │   └── edq-config.json
    ├── empty
    │   └── edq-config.json
    ├── empty-dir
    ├── empty-key
    │   └── edq-config.json
    ├── global
    │   └── edq-config.json
    ├── malformed
    │   └── edq-config.json
    ├── multiple-options
    │   └── edq-config.json
    ├── nested
    │   ├── config.json
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
    edq.util.json.dump_path(
        {},
        os.path.join(empty_config_dir_path, edq.config.constants.DEFAULT_CONFIG_FILENAME),
    )

    multiple_option_config_dir_path = os.path.join(temp_dir, "multiple-options")
    edq.util.dirent.mkdir(multiple_option_config_dir_path)
    edq.util.json.dump_path(
        {"user": "user@test.edulinq.org", "pass": "password1234"},
        os.path.join(multiple_option_config_dir_path, edq.config.constants.DEFAULT_CONFIG_FILENAME),
    )

    empty_key_config_dir_path = os.path.join(temp_dir, "empty-key")
    edq.util.dirent.mkdir(empty_key_config_dir_path)
    edq.util.json.dump_path(
        {"": "user@test.edulinq.org"},
        os.path.join(empty_key_config_dir_path, edq.config.constants.DEFAULT_CONFIG_FILENAME),
    )

    custom_name_config_dir_path = os.path.join(temp_dir, "custom-name")
    edq.util.dirent.mkdir(custom_name_config_dir_path)
    edq.util.json.dump_path(
        {"user": "user@test.edulinq.org"},
        os.path.join(custom_name_config_dir_path, "custom-edq-config.json"),
    )

    edq.util.dirent.mkdir(os.path.join(temp_dir, "dir-config", "edq-config.json"))
    edq.util.dirent.mkdir(os.path.join(temp_dir, "empty-dir"))

    global_config_dir_path = os.path.join(temp_dir, "global")
    edq.util.dirent.mkdir(global_config_dir_path)
    edq.util.json.dump_path(
        {"user": "user@test.edulinq.org"},
        os.path.join(global_config_dir_path, edq.config.constants.DEFAULT_CONFIG_FILENAME),
    )

    old_name_config_dir_path = os.path.join(temp_dir, "old-name")
    edq.util.dirent.mkdir(os.path.join(old_name_config_dir_path, "nest1", "nest2"))
    edq.util.json.dump_path(
        {"user": "user@test.edulinq.org"},
        os.path.join(old_name_config_dir_path, "config.json"),
    )

    nested_dir_path = os.path.join(temp_dir, "nested")
    edq.util.dirent.mkdir(os.path.join(nested_dir_path, "nest1", "nest2a"))
    edq.util.dirent.mkdir(os.path.join(nested_dir_path, "nest1", "nest2b"))
    edq.util.json.dump_path(
        {"server": "http://test.edulinq.org"},
        os.path.join(nested_dir_path, edq.config.constants.DEFAULT_CONFIG_FILENAME),
    )
    edq.util.json.dump_path(
        {"user": "user@test.edulinq.org"},
        os.path.join(nested_dir_path, "config.json"),
    )
    edq.util.json.dump_path(
        {"user": "user@test.edulinq.org"},
        os.path.join(nested_dir_path, "nest1", "nest2b", edq.config.constants.DEFAULT_CONFIG_FILENAME),
    )
    edq.util.json.dump_path(
        {"user": "user@test.edulinq.org"},
        os.path.join(nested_dir_path, "nest1", "nest2b", "config.json"),
    )

    simple_config_dir_path = os.path.join(temp_dir, "simple")
    edq.util.dirent.mkdir(simple_config_dir_path)
    edq.util.dirent.write_file(
        os.path.join(simple_config_dir_path, edq.config.constants.DEFAULT_CONFIG_FILENAME),
        '{"user": "user@test.edulinq.org",}',
    )

    malformed_config_dir_path = os.path.join(temp_dir, "malformed")
    edq.util.dirent.mkdir(malformed_config_dir_path)
    edq.util.dirent.write_file(
        os.path.join(malformed_config_dir_path, edq.config.constants.DEFAULT_CONFIG_FILENAME),
        "{user: user@test.edulinq.org}",
    )

    return temp_dir

def create_cli_test_dir(
    test: edq.testing.unittest.BaseTest,
    test_info: edq.testing.cli.CLITestInfo,
    ) -> None:
    """
    Create a temp dir and populate it with dirents for CLI testing.
    .
    ├── multiple-options
    │   └── edq-config.json
    └── simple
        └── edq-config.json
    """

    simple_config_dir_path = os.path.join(test_info.temp_dir, "simple")
    edq.util.dirent.mkdir(simple_config_dir_path)
    edq.util.json.dump_path(
        {"user": "user@test.edulinq.org"},
        os.path.join(simple_config_dir_path, edq.config.constants.DEFAULT_CONFIG_FILENAME),
    )

    multiple_option_config_dir_path = os.path.join(test_info.temp_dir, "multiple-options")
    edq.util.dirent.mkdir(multiple_option_config_dir_path)
    edq.util.json.dump_path(
        {"user": "user@test.edulinq.org", "pass": "password1234"},
        os.path.join(multiple_option_config_dir_path, edq.config.constants.DEFAULT_CONFIG_FILENAME),
    )

def verify_cli_test_config_content(
    test: edq.testing.unittest.BaseTest,
    test_info: edq.testing.cli.CLITestInfo,
    ) -> None:
    """ Verify the contents of a config file created by a CLI test. """

    path = os.path.join(test_info.work_dir, *test_info.extra_options["path"].split('/'))

    data_actual = edq.util.json.load_path(path)
    data_expected = test_info.extra_options["data"]

    test.assertJSONDictEqual(data_actual, data_expected)
