"""Post-quantum lock demo modules."""

from pq_lock.post_quantum.crypto_utils import (
    AES_GCM_NONCE_SIZE,
    CommandAuthenticationError,
    decrypt_command,
    derive_aes_key,
    encrypt_command,
)
from pq_lock.post_quantum.lock import PQController, PQUnlockRequest, PostQuantumLock
from pq_lock.post_quantum.lock import (
    PQVerificationResult,
    TamperStrategy,
    tamper_unlock_request,
)

__all__ = [
    "AES_GCM_NONCE_SIZE",
    "CommandAuthenticationError",
    "PQController",
    "PQUnlockRequest",
    "PQVerificationResult",
    "PostQuantumLock",
    "TamperStrategy",
    "decrypt_command",
    "derive_aes_key",
    "encrypt_command",
    "tamper_unlock_request",
]
