import os
import typing

import edq.config.constants
import edq.config.settings
import edq.config.testing
import edq.config.util
import edq.testing.unittest
import edq.util.json

class TestConfigUtils(edq.testing.unittest.BaseTest):
    """ Test configuration utils. """

    def test_update_config_base(self) -> None:
        """
        Test that the given config is updated correctly and paths are created correctly.
        """

        # [(write config arguments, expected result, error substring), ...]
        test_cases: typing.List[typing.Tuple[
            typing.Dict[str, typing.Any],
            typing.Dict[str, typing.Any],
            typing.Union[str, None],
        ]] = [
            # Non-exisiting Path
            (
                {
                    'path': os.path.join('non-exisiting-path', edq.config.settings.get_config_filename()),
                    'config_to_write': {'user': 'user@test.edulinq.org'},
                },
                {
                    'path': os.path.join('non-exisiting-path', edq.config.settings.get_config_filename()),
                    'data': {'user': 'user@test.edulinq.org'},
                },
                None,
            ),

            # Directory Path
            (
                {
                    'path': os.path.join("dir-config", edq.config.settings.get_config_filename()),
                    'config_to_write': {'user': 'user@test.edulinq.org'},
                },
                {},
                "Cannot open JSON file, expected a file but got a directory",
            ),

            # Empty Config
            (
                {
                    'path': os.path.join('empty', edq.config.settings.get_config_filename()),
                    'config_to_write': {'user': 'user@test.edulinq.org'},
                },
                {
                    'path': os.path.join('empty', edq.config.settings.get_config_filename()),
                    'data': {'user': 'user@test.edulinq.org'},
                },
                None,
            ),

            # Non-empty Config
            (
                {
                    'path': os.path.join('simple', edq.config.settings.get_config_filename()),
                    'config_to_write': {'pass': 'password1234'},
                },
                {
                    'path': os.path.join('simple', edq.config.settings.get_config_filename()),
                    'data': {'user': 'user@test.edulinq.org', 'pass': 'password1234'},
                },
                None,
            ),

            # Non-empty Config (Overwrite)
            (
                {
                    'path': os.path.join('simple', edq.config.settings.get_config_filename()),
                    'config_to_write': {'user': 'admin@test.edulinq.org'},
                },
                {
                    'path': os.path.join('simple', edq.config.settings.get_config_filename()),
                    'data': {'user': 'admin@test.edulinq.org'},
                },
                None,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            kwargs, expected_result, error_substring = test_case

            with self.subTest(msg = f"Case {i}"):
                temp_dir = edq.config.testing.create_test_dir(temp_dir_prefix = "edq-test-update-config-")

                kwargs['path'] = os.path.join(temp_dir, kwargs['path'])

                previous_work_directory = os.getcwd()
                os.chdir(temp_dir)

                try:
                    edq.config.util.update_options_in_config_file(**kwargs)
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

                path = os.path.join(temp_dir, expected_result["path"])

                data_actual = edq.util.json.load_path(path)
                data_expected = expected_result['data']

                self.assertJSONDictEqual(data_actual, data_expected)

    def test_remove_config_option_base(self) -> None:
        """
        Test that the given config option(s) are removed correctly.
        """

        # [(write config arguments, expected result, error substring), ...]
        test_cases: typing.List[typing.Tuple[
            typing.Dict[str, typing.Any],
            typing.Dict[str, typing.Any],
            typing.Union[str, None],
        ]] = [
            # Non-exisiting Path
            (
                {
                    'path': os.path.join('non-exisiting-path', edq.config.settings.get_config_filename()),
                    'config_to_remove': ['user'],
                },
                {},
                "FileNotFoundError",
            ),

            # Remove No Options
            (
                {
                    'path': os.path.join('simple', edq.config.settings.get_config_filename()),
                    'config_to_remove': [],
                },
                {
                    'path': os.path.join('simple', edq.config.settings.get_config_filename()),
                    'data': {'user': 'user@test.edulinq.org'},
                },
                None,
            ),

            # Directory Path
            (
                {
                    'path': os.path.join("dir-config", edq.config.settings.get_config_filename()),
                    'config_to_remove': ['user'],
                },
                {},
                "Cannot open JSON file, expected a file but got a directory",
            ),

            # Empty Config
            (
                {
                    'path': os.path.join('empty', edq.config.settings.get_config_filename()),
                    'config_to_remove': ['user'],
                },
                {
                    'path': os.path.join('empty', edq.config.settings.get_config_filename()),
                    'data': {},
                },
                None,
            ),

            # Non-empty Config (Remove Single Option)
            (
                {
                    'path': os.path.join('multiple-options', edq.config.settings.get_config_filename()),
                    'config_to_remove': ['pass'],
                },
                {
                    'path': os.path.join('multiple-options', edq.config.settings.get_config_filename()),
                    'data': {'user': 'user@test.edulinq.org'},
                },
                None,
            ),

            # Non-empty Config (Remove Multiple Options)
            (
                {
                    'path': os.path.join('multiple-options', edq.config.settings.get_config_filename()),
                    'config_to_remove': ['pass', 'user'],
                },
                {
                    'path': os.path.join('multiple-options', edq.config.settings.get_config_filename()),
                    'data': {},
                },
                None,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            kwargs, expected_result, error_substring = test_case

            with self.subTest(msg = f"Case {i}"):
                temp_dir = edq.config.testing.create_test_dir(temp_dir_prefix = "edq-test-remove-config-")

                kwargs['path'] = os.path.join(temp_dir, str(kwargs['path']))

                previous_work_directory = os.getcwd()
                os.chdir(temp_dir)

                try:
                    edq.config.util.remove_options_in_config_file(kwargs['path'], kwargs['config_to_remove'])
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

                path = os.path.join(temp_dir, str(expected_result["path"]))

                data_actual = edq.util.json.load_path(path)
                data_expected = expected_result['data']

                self.assertJSONDictEqual(data_actual, data_expected)
