from __future__ import annotations

from dataclasses import dataclass

from pq_lock._oqs import configure_oqs_dll_search_path
from pq_lock.hardware import LockHardware, MockLockHardware

configure_oqs_dll_search_path()

import oqs

from pq_lock.post_quantum.crypto_utils import (
    CommandAuthenticationError,
    decrypt_command,
    encrypt_command,
)


@dataclass(frozen=True)
class PQUnlockRequest:
    """Wire-format payload sent from the controller to the lock."""

    kem_ciphertext: bytes
    nonce: bytes
    encrypted_command: bytes


class PQController:
    def __init__(self, kem_name: str = "ML-KEM-512") -> None:
        self.kem_name = kem_name

    def build_unlock_request(self, lock_public_key: bytes) -> PQUnlockRequest:
        """Build an encrypted unlock request for the target lock."""
        with oqs.KeyEncapsulation(self.kem_name) as kem:
            ciphertext_kem, shared_secret = kem.encap_secret(lock_public_key)

        nonce, ciphertext_cmd = encrypt_command(shared_secret, "UNLOCK")
        return PQUnlockRequest(
            kem_ciphertext=ciphertext_kem,
            nonce=nonce,
            encrypted_command=ciphertext_cmd,
        )


class PostQuantumLock:
    def __init__(
        self,
        kem_name: str = "ML-KEM-512",
        hardware: LockHardware | None = None,
    ) -> None:
        self.kem_name = kem_name
        self.kem = oqs.KeyEncapsulation(self.kem_name)
        self.public_key = self.kem.generate_keypair()
        self.hardware = hardware or MockLockHardware()
        self.is_open = False
        self.hardware.engage_lock()

    def get_public_key(self) -> bytes:
        return self.public_key

    def process_unlock_request(self, request: PQUnlockRequest) -> str:
        """Fail closed unless ML-KEM decapsulation and AES-GCM verification succeed."""
        try:
            shared_secret = self.kem.decap_secret(request.kem_ciphertext)
            command = decrypt_command(
                shared_secret,
                request.nonce,
                request.encrypted_command,
            )
        except (ValueError, RuntimeError, CommandAuthenticationError):
            self.is_open = False
            self.hardware.engage_lock()
            return "DENIED"

        if command == "UNLOCK":
            self.is_open = True
            self.hardware.actuate_unlock()
            return "OPEN"

        self.is_open = False
        self.hardware.engage_lock()
        return "DENIED"
