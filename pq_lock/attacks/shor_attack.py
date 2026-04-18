from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
import math

from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator

from pq_lock.classical.toy_rsa import RSAPrivateKey, RSAPublicKey, recover_private_key


@dataclass(frozen=True)
class ShorAttackResult:
    """Result of a toy factoring demo."""

    modulus: int
    factors: tuple[int, int]
    base: int
    true_order: int
    sampled_bitstring: str
    recovered_order: int
    used_order_fallback: bool

    def recover_private_key(self, public_key: RSAPublicKey) -> RSAPrivateKey:
        return recover_private_key(public_key, self.factors[0], self.factors[1])


def multiplicative_order(base: int, modulus: int) -> int:
    """Return the smallest r where base**r == 1 mod modulus."""
    if math.gcd(base, modulus) != 1:
        raise ValueError("Base and modulus must be coprime.")

    residue = 1
    for order in range(1, modulus + 1):
        residue = (residue * base) % modulus
        if residue == 1:
            return order

    raise ValueError("No multiplicative order found for the toy modulus.")


def _estimate_order_with_qpe(order: int, shots: int = 512) -> tuple[int, str]:
    """
    Use a phase-estimation-shaped circuit to recover a tiny order.

    This is intentionally pedagogical. For tiny toy RSA moduli we already know the
    exact order classically; the circuit only simulates the period-finding flavor
    of Shor's algorithm and then classical post-processing extracts the denominator.
    """
    counting_qubits = max(5, order.bit_length() + 2)
    phase = 1 / order

    circuit = QuantumCircuit(counting_qubits, counting_qubits)
    for qubit in range(counting_qubits):
        circuit.h(qubit)
        circuit.p(2 * math.pi * (2**qubit) * phase, qubit)

    circuit.append(QFT(counting_qubits, inverse=True, do_swaps=True), range(counting_qubits))
    circuit.measure(range(counting_qubits), range(counting_qubits))

    simulator = AerSimulator()
    compiled = transpile(circuit, simulator)
    counts = simulator.run(compiled, shots=shots).result().get_counts()
    measured = Counter(counts).most_common(1)[0][0]

    measured_phase = int(measured, 2) / (2**counting_qubits)
    recovered = Fraction(measured_phase).limit_denominator(order * 2).denominator
    return recovered, measured


def factor_toy_rsa_modulus(modulus: int) -> ShorAttackResult:
    """Factor a tiny RSA modulus with Shor-style classical post-processing."""
    for base in range(2, modulus):
        divisor = math.gcd(base, modulus)
        if 1 < divisor < modulus:
            other_factor = modulus // divisor
            return ShorAttackResult(
                modulus=modulus,
                factors=tuple(sorted((divisor, other_factor))),
                base=base,
                true_order=1,
                sampled_bitstring="classical-gcd",
                recovered_order=1,
                used_order_fallback=True,
            )

        try:
            true_order = multiplicative_order(base, modulus)
        except ValueError:
            continue

        if true_order % 2 != 0:
            continue

        midpoint = pow(base, true_order // 2, modulus)
        if midpoint in (1, modulus - 1):
            continue

        recovered_order, measured = _estimate_order_with_qpe(true_order)
        candidate_order = recovered_order if recovered_order % 2 == 0 else true_order
        used_order_fallback = candidate_order != recovered_order

        midpoint = pow(base, candidate_order // 2, modulus)
        factor_a = math.gcd(midpoint - 1, modulus)
        factor_b = math.gcd(midpoint + 1, modulus)

        if 1 < factor_a < modulus and 1 < factor_b < modulus:
            return ShorAttackResult(
                modulus=modulus,
                factors=tuple(sorted((factor_a, factor_b))),
                base=base,
                true_order=true_order,
                sampled_bitstring=measured,
                recovered_order=recovered_order,
                used_order_fallback=used_order_fallback,
            )

    raise ValueError("Failed to factor the toy RSA modulus.")
