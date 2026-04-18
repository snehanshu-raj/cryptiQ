from __future__ import annotations

import hashlib
import os
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

AES_GCM_NONCE_SIZE = 12


class CommandAuthenticationError(Exception):
    """Raised when an encrypted command cannot be authenticated."""


def derive_aes_key(shared_secret: bytes) -> bytes:
    """Derive a 256-bit AES key from the ML-KEM shared secret."""
    return hashlib.sha256(shared_secret).digest()


def encrypt_command(shared_secret: bytes, command: str) -> tuple[bytes, bytes]:
    """Encrypt and authenticate a UTF-8 command with AES-GCM."""
    key = derive_aes_key(shared_secret)
    aesgcm = AESGCM(key)
    nonce = os.urandom(AES_GCM_NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, command.encode("utf-8"), None)
    return nonce, ciphertext


def decrypt_command(shared_secret: bytes, nonce: bytes, ciphertext: bytes) -> str:
    """Decrypt and verify a command, raising on authentication failure."""
    key = derive_aes_key(shared_secret)
    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except InvalidTag as exc:
        raise CommandAuthenticationError("AES-GCM authentication failed.") from exc

    return plaintext.decode("utf-8")
