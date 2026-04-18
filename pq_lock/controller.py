from __future__ import annotations

from dataclasses import dataclass

import oqs
from pq_lock.crypto_utils import encrypt_command


@dataclass(frozen=True)
class UnlockRequest:
    """Wire-format payload sent from the controller to the lock."""

    kem_ciphertext: bytes
    nonce: bytes
    encrypted_command: bytes


class Controller:
    def __init__(self, kem_name: str = "ML-KEM-512") -> None:
        self.kem_name = kem_name

    def build_unlock_request(self, lock_public_key: bytes) -> UnlockRequest:
        """Build an encrypted unlock request for the target lock."""
        with oqs.KeyEncapsulation(self.kem_name) as kem:
            ciphertext_kem, shared_secret = kem.encap_secret(lock_public_key)

        nonce, ciphertext_cmd = encrypt_command(shared_secret, "UNLOCK")
        return UnlockRequest(
            kem_ciphertext=ciphertext_kem,
            nonce=nonce,
            encrypted_command=ciphertext_cmd,
        )
