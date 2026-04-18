from __future__ import annotations

import oqs
from pq_lock.controller import UnlockRequest
from pq_lock.crypto_utils import CommandAuthenticationError, decrypt_command


class QuantumResistantLock:
    def __init__(self, kem_name: str = "ML-KEM-512") -> None:
        self.kem_name = kem_name
        self.kem = oqs.KeyEncapsulation(self.kem_name)
        self.public_key = self.kem.generate_keypair()
        self.is_open = False

    def get_public_key(self) -> bytes:
        return self.public_key

    def process_unlock_request(self, request: UnlockRequest) -> str:
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
            return "DENIED"

        if command == "UNLOCK":
            self.is_open = True
            return "OPEN"

        self.is_open = False
        return "DENIED"
