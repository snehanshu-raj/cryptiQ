from __future__ import annotations

from pq_lock.hardware import MockLockHardware
from pq_lock.post_quantum.lock import PQController, PostQuantumLock


def main() -> None:
    print("=== Post-Quantum Lock Demo ===")

    hardware = MockLockHardware()
    lock = PostQuantumLock(kem_name="ML-KEM-512", hardware=hardware)
    controller = PQController(kem_name="ML-KEM-512")

    print("Lock created.")
    print("Generating unlock request with ML-KEM...")

    lock_public_key = lock.get_public_key()
    unlock_request = controller.build_unlock_request(lock_public_key)

    print("Controller sent encrypted unlock packet.")
    result = lock.process_unlock_request(unlock_request)

    print(f"Lock result: {result}")
    print(f"Lock open state: {lock.is_open}")
    print(f"Mock actuator locked state: {hardware.is_locked}")
    print(f"Mock actuator unlock count: {hardware.unlock_count}")


if __name__ == "__main__":
    main()
