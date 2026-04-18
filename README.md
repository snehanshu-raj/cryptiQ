# Post-Quantum Lock

A hackathon-ready software prototype of a lock secured with post-quantum cryptography.

## Goal
Build a software-first prototype where:
1. A controller requests unlock access
2. The lock exposes a post-quantum public key
3. The controller uses ML-KEM to establish a shared secret
4. The controller encrypts an "UNLOCK" command with AES-GCM
5. The lock decrypts and validates the command
6. If valid, the lock opens

## Project Layout
- lock.py simulates the lock
- controller.py simulates the controller
- crypto_utils.py handles AES-GCM key derivation and encryption helpers
- demo.py runs the flow end-to-end
- tests/ contains basic unit tests

## How It Works
1. The lock generates an ML-KEM public/private keypair.
2. The controller encapsulates to the lock's public key to derive a shared secret.
3. The controller derives an AES-256 key from that shared secret with SHA-256.
4. The controller encrypts the string `UNLOCK` with AES-GCM.
5. The lock decapsulates, derives the same AES key, and decrypts the command.
6. The lock returns `OPEN` only if decryption and authentication succeed.

Any decapsulation or AES-GCM authentication failure is treated as tampering and the lock fails closed.

## Run
1. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the demo:
   ```bash
   python demo.py
   ```
3. Run the tests:
   ```bash
   python -m unittest discover -s tests -v
   ```
