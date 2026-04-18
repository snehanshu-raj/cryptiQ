from __future__ import annotations

from pq_lock.attacks.shor_attack import factor_toy_rsa_modulus
from pq_lock.classical.rsa_lock import RSALock, build_unlock_token
from pq_lock.classical.toy_rsa import generate_toy_rsa_keypair
from pq_lock.hardware import MockLockHardware
from pq_lock.post_quantum.lock import PQController, PostQuantumLock


def main() -> None:
    print("=== Quantum Lock Comparison ===")
    print()
    print("This demo uses toy RSA only for education.")
    print("It does not claim that real-world RSA is currently broken.")
    print()

    rsa_public_key, rsa_private_key = generate_toy_rsa_keypair()
    rsa_lock = RSALock(rsa_public_key)
    legitimate_token = build_unlock_token("UNLOCK", rsa_private_key)

    print("[1] Normal toy RSA flow")
    print(f"Controller public modulus n = {rsa_public_key.n}")
    result = rsa_lock.process_token(legitimate_token)
    print(f"Trusted signed unlock token -> {result}")
    print()

    print("[2] Educational toy factoring attack")
    attack = factor_toy_rsa_modulus(rsa_public_key.n)
    compromised_private_key = attack.recover_private_key(rsa_public_key)
    forged_token = build_unlock_token("UNLOCK", compromised_private_key)
    compromised_lock = RSALock(rsa_public_key)
    forged_result = compromised_lock.process_token(forged_token)

    print(
        f"Simulator factored tiny n = {attack.modulus} into "
        f"{attack.factors[0]} x {attack.factors[1]} using base {attack.base}"
    )
    print(
        f"Sampled order bitstring = {attack.sampled_bitstring}, "
        f"recovered order = {attack.recovered_order}"
    )
    if attack.used_order_fallback:
        print("Pedagogical shortcut: exact tiny-N order was used when the sampled value was noisy.")
    print(f"Forged RSA unlock token -> {forged_result}")
    print()

    print("[3] Post-quantum lock flow")
    pq_hardware = MockLockHardware()
    pq_lock = PostQuantumLock(hardware=pq_hardware)
    pq_controller = PQController()
    pq_request = pq_controller.build_unlock_request(pq_lock.get_public_key())
    pq_result = pq_lock.process_unlock_request(pq_request)
    print(f"ML-KEM + AES-GCM unlock packet -> {pq_result}")
    print(f"Mock actuator unlock count -> {pq_hardware.unlock_count}")
    print("Same factoring story does not apply here because there is no RSA modulus to factor.")


if __name__ == "__main__":
    main()
