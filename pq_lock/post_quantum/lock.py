from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

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


TamperStrategy = Literal["ciphertext", "nonce", "kem_ciphertext"]


@dataclass(frozen=True)
class PQVerificationResult:
    """Structured verification outcome for UI, backend, and tests."""

    result: str
    lock_state: str
    reason: str
    event_log: tuple[str, ...]


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


def tamper_unlock_request(
    request: PQUnlockRequest,
    strategy: TamperStrategy = "ciphertext",
) -> PQUnlockRequest:
    """Return a copy of the request with one field deliberately corrupted."""
    if strategy == "ciphertext":
        tampered_ciphertext = request.encrypted_command[:-1] + bytes(
            [request.encrypted_command[-1] ^ 0x01]
        )
        return replace(request, encrypted_command=tampered_ciphertext)

    if strategy == "nonce":
        tampered_nonce = request.nonce[:-1] + bytes([request.nonce[-1] ^ 0x01])
        return replace(request, nonce=tampered_nonce)

    if strategy == "kem_ciphertext":
        tampered_kem = request.kem_ciphertext[:-1] + bytes(
            [request.kem_ciphertext[-1] ^ 0x01]
        )
        return replace(request, kem_ciphertext=tampered_kem)

    raise ValueError(f"Unsupported tamper strategy: {strategy}")


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

    def verify_unlock_request(self, request: PQUnlockRequest) -> PQVerificationResult:
        """Fail closed unless ML-KEM decapsulation and AES-GCM verification succeed."""
        event_log = [
            "Attempting ML-KEM decapsulation",
            "Attempting AES-GCM authentication",
        ]
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
            event_log.append("Authentication failed")
            event_log.append("Lock remains closed")
            return PQVerificationResult(
                result="DENIED",
                lock_state="LOCKED",
                reason="Authentication failed after packet tampering.",
                event_log=tuple(event_log),
            )

        if command == "UNLOCK":
            self.is_open = True
            self.hardware.actuate_unlock()
            event_log.append("Authenticated unlock command accepted")
            event_log.append("Lock opened")
            return PQVerificationResult(
                result="OPEN",
                lock_state="OPEN",
                reason="Authenticated unlock command accepted.",
                event_log=tuple(event_log),
            )

        self.is_open = False
        self.hardware.engage_lock()
        event_log.append("Command rejected")
        event_log.append("Lock remains closed")
        return PQVerificationResult(
            result="DENIED",
            lock_state="LOCKED",
            reason="Packet decrypted but did not contain a valid unlock command.",
            event_log=tuple(event_log),
        )

    def process_unlock_request(self, request: PQUnlockRequest) -> str:
        return self.verify_unlock_request(request).result
