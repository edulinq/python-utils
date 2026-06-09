import enum
import os
import typing

import edq.config.app
import edq.config.constants
import edq.config.load
import edq.config.testing
import edq.testing.unittest
import edq.util.crypto
import edq.util.json
import edq.util.serial

class _TestEnumStr(enum.Enum):
    """ A test enum that only has strings. """

    FIRST = 'a'
    SECOND = 'b'

class _TestApplicationConfig(edq.config.app.BaseApplicationConfig):
    """ A test application config. """

    serialization_omit_none = True

    def __init__(self,
            user: typing.Union[str, None] = None,
            token: typing.Union[edq.util.crypto.Secret, None] = None,
            number: typing.Union[int, None] = None,
            enum_value: typing.Union[_TestEnumStr, None] = None,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        self.user: typing.Union[str, None] = user
        self.token: typing.Union[edq.util.crypto.Secret, None] = token
        self.number: typing.Union[int, None] = number
        self.enum_value: typing.Union[_TestEnumStr, None] = enum_value

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, _TestApplicationConfig)):
            return False

        return (self.user, self.token, self.number) == (other.user, other.token, other.number)

class TestApplicationConfig(edq.testing.unittest.BaseTest):
    """ Test basic operations on configs. """

    def tearDown(self) -> None:
        edq.config.settings.set_application_config_class()
        os.environ.pop('EDQ__ENCRYPTION_KEY', None)

    def test_application_config_base(self) -> None:
        """
        Test loading config into an application config.
        """

        # [(application config, dict POD config), ...]
        test_cases: typing.List[typing.Tuple[
            edq.config.app.BaseApplicationConfig,
            typing.Dict[str, typing.Any],
        ]] = [
            # Base
            (
                _TestApplicationConfig(user = 'alice'),
                {
                    'user': 'alice',
                },
            ),

            # Numeric
            (
                _TestApplicationConfig(number = 4),
                {
                    'number': 4,
                },
            ),

            # Enum
            (
                _TestApplicationConfig(enum_value = _TestEnumStr.FIRST),
                {
                    'enum_value': 'a',
                },
            ),

            # Secret - No Encryption
            (
                _TestApplicationConfig(token = edq.util.crypto.Secret('secret')),
                {
                    'token': 'secret',
                },
            ),

            # Secret - Encryption
            (
                _TestApplicationConfig(
                    token = edq.util.crypto.Secret('secret', iv_b64 = 'UldcITh761FJcMRThJpkag==', salt_b64 = 'niOb2keWPoSwR1MlgWHayQ=='),
                ),
                {
                    'token': '__edq_secret__::AES256v1::UldcITh761FJcMRThJpkag==::niOb2keWPoSwR1MlgWHayQ==::sN3Tl4WCA6X+xszcnTO+9Q==',
                },
            ),
        ]

        # Use a fixed key.
        os.environ['EDQ__ENCRYPTION_KEY'] = 'key'
        serialization_context = edq.util.serial.SerializationContext(key = 'key')

        for (i, test_case) in enumerate(test_cases):
            expected_application_config, expected_dict_config = test_case

            with self.subTest(msg = f"Case {i}"):
                # Write the dict config to disk.
                temp_dir = edq.config.testing.create_test_dir(temp_dir_prefix = "edq-test-application-config-base-")
                config_path = os.path.join(temp_dir, 'config.json')
                edq.util.json.dump_path(expected_dict_config, config_path)

                edq.config.settings.set_application_config_class(_TestApplicationConfig)

                # Load the tiered config.
                # Note that they encryption key is passed via an environmental variable.
                tiered_config = edq.config.load.get_tiered_config(
                    cli_arguments = {edq.config.constants.GLOBAL_CONFIG_KEY: config_path},
                )

                # Ensure that the loaded application config matches the expected application config.
                self.assertEqual(expected_application_config, tiered_config.application_config)

                # Serialize the application config, and ensure it matches the dict config.
                new_dict_config = tiered_config.application_config.to_dict(context = serialization_context)
                self.assertJSONDictEqual(expected_dict_config, new_dict_config)

                # Deserialize the dict config into an application config, and ensure it matches the application config.
                new_application_config = _TestApplicationConfig.from_dict(new_dict_config, context = serialization_context)
                self.assertEqual(tiered_config.application_config, new_application_config)
