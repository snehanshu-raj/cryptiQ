"""Educational classical cryptography demo modules."""

from pq_lock.classical.rsa_lock import RSALock, RSAUnlockToken, build_unlock_token
from pq_lock.classical.toy_rsa import (
    RSAPrivateKey,
    RSAPublicKey,
    decrypt_int,
    encrypt_int,
    generate_toy_rsa_keypair,
    recover_private_key,
    sign_message,
    verify_signature,
)

__all__ = [
    "RSALock",
    "RSAUnlockToken",
    "RSAPrivateKey",
    "RSAPublicKey",
    "build_unlock_token",
    "decrypt_int",
    "encrypt_int",
    "generate_toy_rsa_keypair",
    "recover_private_key",
    "sign_message",
    "verify_signature",
]
