from __future__ import annotations

import unittest
from dataclasses import replace

from pq_lock.attacks.shor_attack import factor_toy_rsa_modulus
from pq_lock.classical.rsa_lock import RSALock, build_unlock_token
from pq_lock.classical.toy_rsa import generate_toy_rsa_keypair
from pq_lock.hardware import MockLockHardware
from pq_lock.post_quantum.lock import PQController, PostQuantumLock


class QuantumLockComparisonTests(unittest.TestCase):
    def test_rsa_normal_flow(self) -> None:
        public_key, private_key = generate_toy_rsa_keypair()
        lock = RSALock(public_key)
        token = build_unlock_token("UNLOCK", private_key)

        result = lock.process_token(token)

        self.assertEqual(result, "OPEN")
        self.assertTrue(lock.is_open)

    def test_rsa_broken_flow(self) -> None:
        public_key, _ = generate_toy_rsa_keypair()
        attack = factor_toy_rsa_modulus(public_key.n)
        forged_private_key = attack.recover_private_key(public_key)
        lock = RSALock(public_key)
        forged_token = build_unlock_token("UNLOCK", forged_private_key)

        result = lock.process_token(forged_token)

        self.assertEqual(result, "OPEN")
        self.assertTrue(lock.is_open)

    def test_pq_lock_success(self) -> None:
        hardware = MockLockHardware()
        lock = PostQuantumLock(hardware=hardware)
        controller = PQController()
        request = controller.build_unlock_request(lock.get_public_key())

        result = lock.process_unlock_request(request)

        self.assertEqual(result, "OPEN")
        self.assertTrue(lock.is_open)
        self.assertFalse(hardware.is_locked)
        self.assertEqual(hardware.unlock_count, 1)

    def test_pq_ciphertext_tampering_fails_closed(self) -> None:
        hardware = MockLockHardware()
        lock = PostQuantumLock(hardware=hardware)
        controller = PQController()
        request = controller.build_unlock_request(lock.get_public_key())
        tampered_request = replace(
            request,
            encrypted_command=request.encrypted_command[:-1]
            + bytes([request.encrypted_command[-1] ^ 0x01]),
        )

        result = lock.process_unlock_request(tampered_request)

        self.assertEqual(result, "DENIED")
        self.assertFalse(lock.is_open)
        self.assertTrue(hardware.is_locked)
        self.assertEqual(hardware.unlock_count, 0)


if __name__ == "__main__":
    unittest.main()
