# Quantum Lock Comparison

A hackathon demo that compares a toy RSA lock with a post-quantum lock.

## Purpose
This project shows two very different stories:
1. A toy RSA lock works in normal conditions.
2. The same toy RSA lock can be broken once its tiny modulus is factored.
3. A post-quantum lock using ML-KEM + AES-GCM does not fit that same factoring-based attack story.

The RSA attack path is intentionally educational and toy-sized. It does not claim that current real-world RSA deployments are broken.
For the factoring demo, the default toy RSA modulus is the canonical tiny example `N = 15`, and the attack uses a real order-finding circuit specialized to that case.

## Project Layout
- `pq_lock/classical/` contains the toy RSA helpers and RSA lock.
- `pq_lock/attacks/` contains the educational Qiskit + Aer factoring demo.
- `pq_lock/post_quantum/` contains the ML-KEM + AES-GCM lock flow.
- `pq_lock/demos/` contains runnable comparison and PQ-only demos.
- `pq_lock/hardware.py` contains the physical lock abstraction, a mock actuator, and a servo placeholder.
- `tests/test_quantum_lock_comparison.py` covers the basic success and failure cases.

## Demo Flows
1. `toy RSA normal flow`: the legitimate controller signs an `UNLOCK` token and the toy RSA lock opens.
2. `toy RSA broken flow`: the factoring demo recovers the tiny RSA private key and forges a valid unlock token.
3. `post-quantum flow`: the controller encapsulates to the lock's ML-KEM public key, encrypts `UNLOCK` with AES-GCM, and the lock opens only if authentication succeeds.
4. `post-quantum attack attempt`: the backend first generates a valid PQ unlock packet, then deliberately tampers with it before delivery. ML-KEM decapsulation and AES-GCM verification still run, authentication fails, and the lock stays closed.

## Judge Demo Story
- In legacy RSA mode, the toy factoring demo recovers the tiny private key and can forge an unlock token.
- In post-quantum mode, the attacker only sends a fake or tampered unlock packet.
- The post-quantum packet fails authentication, the lock fails closed, and the physical or mock actuator remains locked.

## Hardware Prep
- `LockHardware` defines the actuator interface.
- `MockLockHardware` keeps the software demo runnable on a normal laptop.
- `ServoLockHardware` is a placeholder for future isolated GPIO integration.
- `PostQuantumLock` now accepts a hardware implementation and triggers `actuate_unlock()` only after successful ML-KEM decapsulation and AES-GCM authentication.

## Windows Note
`liboqs-python` depends on a local `liboqs` build. On Windows, if `oqs.dll` is installed under `C:\liboqs\bin`, the project will add that directory at runtime before importing `oqs`.

## Run
1. Create and activate a virtual environment, then install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. If you are on Windows and built `liboqs` manually, expose it to the shell:
   ```powershell
   $env:OQS_INSTALL_PATH = "C:\liboqs"
   $env:PATH = "C:\liboqs\bin;$env:PATH"
   ```
3. Run the comparison demo:
   ```bash
   python -m pq_lock.demos.demo_compare
   ```
4. Run the post-quantum-only demo:
   ```bash
   python -m pq_lock.demos.pq_demo
   ```
5. Run the judge backend and open the phone-friendly UI:
   ```bash
   python -m pq_lock.judge_backend
   ```
   Then open `pq_lock/judge_demo_ui.html` in a browser and use `Attack Post-Quantum Lock` to send a tampered packet through the backend API.
6. Run the tests:
   ```bash
   python -m unittest discover -s tests -v
   ```
