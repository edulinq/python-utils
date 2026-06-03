import hashlib
import os
import typing

import cryptography.hazmat.primitives
import cryptography.hazmat.primitives.ciphers
import cryptography.hazmat.primitives.padding

import edq.util.constants
import edq.util.encoding

SCRYPT_DEFAULT_ITERATIONS: int = 2**11
"""
The default iterations to use with scrypt.
2^11 or 2^14 are generally recommended for interactive tools.
"""

SCRYPT_DEFAULT_BLOCK_SIZE: int = 8
""" The default block size factor to use with scrypt. """

SCRYPT_PARALLELIZATION: int = 1
""" The parallelization (or lack thereof) to use in scrypt. """

SALT_LENGTH_BYTES: int = 16
""" The length for generated salts. """

IV_LENGTH_BYTES: int = 16
""" The length for generated IVs (before key derivation). """

AES_BLOCK_SIZE_BYTES: int = 16
""" AES always uses 128-bit blocks. """

def aes256_encrypt(
        key: str,
        cleartext: str,
        iv_b64: typing.Union[str, None] = None,
        salt_b64: typing.Union[str, None] = None,
        encoding: str = edq.util.constants.DEFAULT_ENCODING,
        ) -> typing.Tuple[str, str, str]:
    """
    Perform AES256-CBC encryption.
    Returns the base64 encoding of the ciphertext, iv, and salt.
    If the IV and/or salt are passed in, the same values will be passed back.
    """

    # Resolve optional fields.

    if (salt_b64 is None):
        salt_bytes = os.urandom(SALT_LENGTH_BYTES)
    else:
        salt_bytes = edq.util.encoding.from_base64(salt_b64, encoding = encoding)

    if (iv_b64 is None):
        iv_bytes = os.urandom(IV_LENGTH_BYTES)
    else:
        iv_bytes = edq.util.encoding.from_base64(iv_b64, encoding = encoding)

    # Derive fixed-sized keys from the key (32 bytes) and IV (16 bytes).
    aes_key = _derive_aes_key(key.encode(encoding), salt_bytes, 32)
    aes_iv = _derive_aes_key(iv_bytes, salt_bytes, AES_BLOCK_SIZE_BYTES)

    # Convert the cleartext to bytes and pad for a 256 block size.
    cleartext_bytes = cleartext.encode(encoding)
    padder = cryptography.hazmat.primitives.padding.PKCS7(8 * AES_BLOCK_SIZE_BYTES).padder()
    cleartext_bytes_padded = padder.update(cleartext_bytes) + padder.finalize()

    # Encrypt the data.
    cipher = cryptography.hazmat.primitives.ciphers.Cipher(
        cryptography.hazmat.primitives.ciphers.algorithms.AES(aes_key),
        cryptography.hazmat.primitives.ciphers.modes.CBC(aes_iv),
    )
    encryptor = cipher.encryptor()
    ciphertext_bytes = encryptor.update(cleartext_bytes_padded) + encryptor.finalize()

    # Encode the results in base64.
    ciphertext_b64 = edq.util.encoding.to_base64(ciphertext_bytes)
    iv_b64 = edq.util.encoding.to_base64(iv_bytes)
    salt_b64 = edq.util.encoding.to_base64(salt_bytes)

    return (ciphertext_b64, iv_b64, salt_b64)

def aes256_decrypt(
        key: str,
        iv_b64: str,
        salt_b64: str,
        ciphertext_b64: str,
        encoding: str = edq.util.constants.DEFAULT_ENCODING,
        ) -> str:
    """
    Perform AES256-CBC decryption.
    """

    # Get the input data as bytes.
    iv_bytes = edq.util.encoding.from_base64(iv_b64, encoding = encoding)
    salt_bytes = edq.util.encoding.from_base64(salt_b64, encoding = encoding)
    ciphertext_bytes = edq.util.encoding.from_base64(ciphertext_b64, encoding = encoding)

    # Derive fixed-sized keys from the key (32 bytes) and IV (16 bytes).
    aes_key = _derive_aes_key(key.encode(encoding), salt_bytes, 32)
    aes_iv = _derive_aes_key(iv_bytes, salt_bytes, AES_BLOCK_SIZE_BYTES)

    # Decrypt the data.
    cipher = cryptography.hazmat.primitives.ciphers.Cipher(
        cryptography.hazmat.primitives.ciphers.algorithms.AES(aes_key),
        cryptography.hazmat.primitives.ciphers.modes.CBC(aes_iv),
    )
    decryptor = cipher.decryptor()
    cleartext_bytes_padded = decryptor.update(ciphertext_bytes) + decryptor.finalize()

    # Unpad and decode the data.
    unpadder = cryptography.hazmat.primitives.padding.PKCS7(8 * AES_BLOCK_SIZE_BYTES).unpadder()
    cleartext_bytes = unpadder.update(cleartext_bytes_padded) + unpadder.finalize()
    cleartext = cleartext_bytes.decode(encoding)

    return cleartext

def _derive_aes_key(
        key_bytes: bytes,
        salt: bytes,
        derived_key_length: int,
        iterations: int = SCRYPT_DEFAULT_ITERATIONS,
        block_size: int = SCRYPT_DEFAULT_BLOCK_SIZE,
        ) -> bytes:
    """ Derive a key for use in AES256 from a cleartext key and salt. """

    return hashlib.scrypt(
        key_bytes,
        salt = salt,
        n = iterations,
        r = block_size,
        p = SCRYPT_PARALLELIZATION,
        dklen = derived_key_length,
    )
