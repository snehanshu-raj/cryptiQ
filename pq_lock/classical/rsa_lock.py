from __future__ import annotations

from dataclasses import dataclass

from pq_lock.classical.toy_rsa import RSAPrivateKey, RSAPublicKey, sign_message, verify_signature


@dataclass(frozen=True)
class RSAUnlockToken:
    """A tiny signed token accepted by the toy RSA lock."""

    message: str
    signature: int


def build_unlock_token(message: str, private_key: RSAPrivateKey) -> RSAUnlockToken:
    """Create a signed unlock token."""
    return RSAUnlockToken(message=message, signature=sign_message(message, private_key))


class RSALock:
    """Educational lock that trusts a toy RSA signature on the unlock token."""

    def __init__(self, controller_public_key: RSAPublicKey) -> None:
        self.controller_public_key = controller_public_key
        self.is_open = False

    def process_token(self, token: RSAUnlockToken) -> str:
        if token.message != "UNLOCK":
            self.is_open = False
            return "DENIED"

        if verify_signature(token.message, token.signature, self.controller_public_key):
            self.is_open = True
            return "OPEN"

        self.is_open = False
        return "DENIED"
