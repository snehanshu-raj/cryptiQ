from __future__ import annotations

from pq_lock.controller import Controller
from pq_lock.lock import QuantumResistantLock


def main() -> None:
    print("=== Post-Quantum Lock Demo ===")

    lock = QuantumResistantLock(kem_name="ML-KEM-512")
    controller = Controller(kem_name="ML-KEM-512")

    print("Lock created.")
    print("Generating unlock request with ML-KEM...")

    lock_public_key = lock.get_public_key()
    unlock_request = controller.build_unlock_request(lock_public_key)

    print("Controller sent encrypted unlock packet.")
    result = lock.process_unlock_request(unlock_request)

    print(f"Lock result: {result}")
    print(f"Lock open state: {lock.is_open}")


if __name__ == "__main__":
    main()
