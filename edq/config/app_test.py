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

class TestApplicationConfig(edq.testing.unittest.BaseTest):
    """ Test basic operations on configs. """

    def test_application_config_base(self) -> None:
        """
        Test loading config into an application config.
        """

        class _TestApplicationConfig(edq.config.app.BaseApplicationConfig):
            serialization_omit_none = True

            def __init__(self,
                    user: typing.Union[str, None] = None,
                    token: typing.Union[edq.util.crypto.Secret, None] = None,
                    number: typing.Union[int, None] = None,
                    **kwargs: typing.Any) -> None:
                super().__init__(**kwargs)

                self.user: typing.Union[str, None] = user
                self.token: typing.Union[edq.util.crypto.Secret, None] = token
                self.number: typing.Union[int, None] = number

            def __eq__(self, other: object) -> bool:
                if (not isinstance(other, _TestApplicationConfig)):
                    return False

                return (self.user, self.token, self.number) == (other.user, other.token, other.number)

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
        serialization_context = edq.util.serial.SerializationContext(key = 'key')

        for (i, test_case) in enumerate(test_cases):
            expected_application_config, expected_dict_config = test_case

            with self.subTest(msg = f"Case {i}"):
                # Write the dict config to disk.
                temp_dir = edq.config.testing.create_test_dir(temp_dir_prefix = "edq-test-application-config-base-")
                config_path = os.path.join(temp_dir, 'config.json')
                edq.util.json.dump_path(expected_dict_config, config_path)

                # Load the tiered config.
                tiered_config = edq.config.load.get_tiered_config(
                    cli_arguments = {edq.config.constants.GLOBAL_CONFIG_KEY: config_path},
                    config_class = _TestApplicationConfig,
                    serialization_context = serialization_context,
                )

                # Ensure that the loaded application config matches the expected application config.
                self.assertEqual(expected_application_config, tiered_config.application_config)

                # Serialize the application config, and ensure it matches the dict config.
                new_dict_config = tiered_config.application_config.to_dict(context = serialization_context)
                self.assertJSONDictEqual(expected_dict_config, new_dict_config)

                # Deserialize the dict config into an application config, and ensure it matches the application config.
                new_application_config = _TestApplicationConfig.from_dict(new_dict_config, context = serialization_context)
                self.assertEqual(tiered_config.application_config, new_application_config)
