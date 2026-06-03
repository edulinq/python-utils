import typing

import edq.testing.unittest
import edq.util.crypto
import edq.util.encoding

class CryptoTest(edq.testing.unittest.BaseTest):
    """ Test cryptographic functions. """

    def test_aes256_base(self) -> None:
        """ Test base encryption and decryptin with AES256. """

        # [(key, iv, salt, cleartext, error substring), ...]
        test_cases: typing.List[typing.Tuple[
                str,
                typing.Union[str, None],
                typing.Union[str, None],
                str,
                typing.Union[str, None],
        ]] = [
            # Base
            (
                'key',
                edq.util.encoding.to_base64('iv'),
                edq.util.encoding.to_base64('salt'),
                'abc123',
                None,
            ),
            (
                'key2',
                edq.util.encoding.to_base64('iv'),
                edq.util.encoding.to_base64('salt'),
                'abc123',
                None,
            ),

            # Optional Field Generation
            (
                'key',
                None,
                edq.util.encoding.to_base64('salt'),
                'abc123',
                None,
            ),
            (
                'key',
                edq.util.encoding.to_base64('iv'),
                None,
                'abc123',
                None,
            ),
            (
                'key',
                None,
                None,
                'abc123',
                None,
            ),

            # Empty
            (
                '',
                '',
                '',
                '',
                None,
            ),
            (
                'key',
                edq.util.encoding.to_base64('iv'),
                edq.util.encoding.to_base64('salt'),
                '',
                None,
            ),
            (
                'key',
                '',
                '',
                '',
                None,
            ),
            (
                '',
                edq.util.encoding.to_base64('iv'),
                '',
                '',
                None,
            ),
            (
                '',
                '',
                edq.util.encoding.to_base64('salt'),
                '',
                None,
            ),
            (
                '',
                '',
                '',
                'abc',
                None,
            ),
        ]

        # Ensure that no duplicate ciphertexts are found.
        seen_ciphertexts: typing.Set[str] = set()

        for (i, test_case) in enumerate(test_cases):
            (key, iv, salt, cleartext, error_substring) = test_case

            with self.subTest(msg = f"Case {i} ('{cleartext}'):"):
                try:
                    ciphertext, actual_iv, actual_salt = edq.util.crypto.aes256_encrypt(key, cleartext, iv_b64 = iv, salt_b64 = salt)
                    actual = edq.util.crypto.aes256_decrypt(key, actual_iv, actual_salt, ciphertext)
                except Exception as ex:
                    error_string = self.format_error_string(ex)
                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{error_string}'.")

                    self.assertIn(error_substring, error_string, 'Error is not as expected.')

                    continue

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")

                self.assertEqual(cleartext, actual)

                if (iv is not None):
                    self.assertEqual(iv, actual_iv)

                if (salt is not None):
                    self.assertEqual(salt, actual_salt)

                self.assertNotIn(ciphertext, seen_ciphertexts, 'Found duplicate ciphertext.')
                seen_ciphertexts.add(ciphertext)
