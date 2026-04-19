from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math

TOY_PRIME_PAIRS: tuple[tuple[int, int], ...] = (
    (3, 5),
    (11, 13),
    (17, 19),
    (23, 29),
)


@dataclass(frozen=True)
class RSAPublicKey:
    n: int
    e: int


@dataclass(frozen=True)
class RSAPrivateKey:
    n: int
    d: int
    p: int
    q: int


def _pick_prime_pair() -> tuple[int, int]:
    return TOY_PRIME_PAIRS[0]


def _select_public_exponent(phi: int) -> int:
    for candidate in (17, 7, 5, 3):
        if math.gcd(candidate, phi) == 1:
            return candidate
    raise ValueError("Could not find a toy public exponent.")


def generate_toy_rsa_keypair(
    primes: tuple[int, int] | None = None,
) -> tuple[RSAPublicKey, RSAPrivateKey]:
    """Generate a tiny educational RSA keypair, defaulting to the Shor demo modulus 15."""
    p, q = primes or _pick_prime_pair()
    if p == q:
        raise ValueError("Toy RSA requires distinct primes.")

    n = p * q
    phi = (p - 1) * (q - 1)
    e = _select_public_exponent(phi)
    d = pow(e, -1, phi)
    return RSAPublicKey(n=n, e=e), RSAPrivateKey(n=n, d=d, p=p, q=q)


def encrypt_int(message: int, public_key: RSAPublicKey) -> int:
    """Encrypt a small integer with textbook RSA."""
    if not 0 <= message < public_key.n:
        raise ValueError("Toy RSA message integer must be in [0, n).")
    return pow(message, public_key.e, public_key.n)


def decrypt_int(ciphertext: int, private_key: RSAPrivateKey) -> int:
    """Decrypt a small integer with textbook RSA."""
    return pow(ciphertext, private_key.d, private_key.n)


def _message_digest(message: str, modulus: int) -> int:
    digest = hashlib.sha256(message.encode("utf-8")).digest()
    return int.from_bytes(digest, "big") % modulus


def sign_message(message: str, private_key: RSAPrivateKey) -> int:
    """Create a tiny raw RSA signature for a demo message."""
    digest = _message_digest(message, private_key.n)
    return pow(digest, private_key.d, private_key.n)


def verify_signature(message: str, signature: int, public_key: RSAPublicKey) -> bool:
    """Verify a tiny raw RSA signature for a demo message."""
    expected_digest = _message_digest(message, public_key.n)
    recovered_digest = pow(signature, public_key.e, public_key.n)
    return recovered_digest == expected_digest


def recover_private_key(
    public_key: RSAPublicKey,
    p: int,
    q: int,
) -> RSAPrivateKey:
    """Recover the toy private key once the tiny modulus has been factored."""
    if p * q != public_key.n:
        raise ValueError("Factors do not match the public modulus.")

    phi = (p - 1) * (q - 1)
    d = pow(public_key.e, -1, phi)
    return RSAPrivateKey(n=public_key.n, d=d, p=p, q=q)
