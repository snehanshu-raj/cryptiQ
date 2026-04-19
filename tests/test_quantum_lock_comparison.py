from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

import pq_lock.judge_backend as judge_backend
from pq_lock.attacks.shor_attack import factor_toy_rsa_modulus
from pq_lock.classical.rsa_lock import RSALock, build_unlock_token
from pq_lock.classical.toy_rsa import generate_toy_rsa_keypair
from pq_lock.hardware import MockLockHardware
from pq_lock.post_quantum.lock import (
    PQController,
    PostQuantumLock,
    tamper_unlock_request,
)


class QuantumLockComparisonTests(unittest.TestCase):
    def setUp(self) -> None:
        judge_backend.pq_demo_hardware.engage_lock()
        judge_backend.pq_demo_hardware.unlock_count = 0
        judge_backend.pq_demo_lock.is_open = False

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
        tampered_request = tamper_unlock_request(request, strategy="ciphertext")

        result = lock.process_unlock_request(tampered_request)

        self.assertEqual(result, "DENIED")
        self.assertFalse(lock.is_open)
        self.assertTrue(hardware.is_locked)
        self.assertEqual(hardware.unlock_count, 0)

    def test_pq_nonce_tampering_fails_closed(self) -> None:
        hardware = MockLockHardware()
        lock = PostQuantumLock(hardware=hardware)
        controller = PQController()
        request = controller.build_unlock_request(lock.get_public_key())
        tampered_request = tamper_unlock_request(request, strategy="nonce")

        result = lock.process_unlock_request(tampered_request)

        self.assertEqual(result, "DENIED")
        self.assertFalse(lock.is_open)
        self.assertTrue(hardware.is_locked)
        self.assertEqual(hardware.unlock_count, 0)

    def test_pq_kem_tampering_fails_closed(self) -> None:
        hardware = MockLockHardware()
        lock = PostQuantumLock(hardware=hardware)
        controller = PQController()
        request = controller.build_unlock_request(lock.get_public_key())
        tampered_request = tamper_unlock_request(request, strategy="kem_ciphertext")

        result = lock.process_unlock_request(tampered_request)

        self.assertEqual(result, "DENIED")
        self.assertFalse(lock.is_open)
        self.assertTrue(hardware.is_locked)
        self.assertEqual(hardware.unlock_count, 0)

    def test_pq_attack_route_returns_denied_and_keeps_lock_closed(self) -> None:
        client = TestClient(judge_backend.app)

        response = client.post("/attack/pq", json={"strategy": "ciphertext"})
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["mode"], "pq")
        self.assertEqual(payload["action"], "attack")
        self.assertEqual(payload["result"], "DENIED")
        self.assertEqual(payload["lock_state"], "LOCKED")
        self.assertIn("Authentication failed", payload["reason"])
        self.assertTrue(payload["hardware"]["is_locked"])
        self.assertEqual(payload["hardware"]["unlock_count"], 0)
        self.assertIn("Generated valid PQ unlock packet", payload["event_log"])
        self.assertIn("Lock remains closed", payload["event_log"])


if __name__ == "__main__":
    unittest.main()
