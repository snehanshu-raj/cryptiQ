from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
import math

from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator

from pq_lock.classical.toy_rsa import RSAPrivateKey, RSAPublicKey, recover_private_key

SUPPORTED_SHOR_MODULUS = 15
SUPPORTED_BASES = {2, 7, 8, 11, 13}


@dataclass(frozen=True)
class ShorAttackResult:
    """Result of a tiny Shor order-finding demo."""

    modulus: int
    factors: tuple[int, int]
    base: int
    sampled_bitstring: str
    sampled_phase: str
    recovered_order: int
    counting_qubits: int
    shots: int

    def recover_private_key(self, public_key: RSAPublicKey) -> RSAPrivateKey:
        return recover_private_key(public_key, self.factors[0], self.factors[1])


def _controlled_amod_15(base: int, power: int) -> QuantumCircuit:
    """
    Return the controlled modular multiplication gate for N = 15.

    This is the standard tiny Shor demo approach: the modular multiplication
    unitaries are specialized to the known N = 15 case instead of being built
    from a scalable arithmetic circuit.
    """
    if base not in SUPPORTED_BASES:
        raise ValueError(f"Base {base} is not supported for the N=15 circuit.")

    circuit = QuantumCircuit(4)
    for _ in range(power):
        if base in {2, 13}:
            circuit.swap(2, 3)
            circuit.swap(1, 2)
            circuit.swap(0, 1)
        elif base in {7, 8}:
            circuit.swap(0, 1)
            circuit.swap(1, 2)
            circuit.swap(2, 3)
        elif base in {4, 11}:
            circuit.swap(1, 3)
            circuit.swap(0, 2)

        if base in {7, 11, 13}:
            for qubit in range(4):
                circuit.x(qubit)

    gate = circuit.to_gate()
    gate.name = f"{base}^{power} mod 15"
    return gate.control()


def build_shor_order_finding_circuit(
    modulus: int = SUPPORTED_SHOR_MODULUS,
    base: int = 2,
    counting_qubits: int = 8,
) -> QuantumCircuit:
    """Construct the tiny order-finding circuit used to factor N = 15."""
    if modulus != SUPPORTED_SHOR_MODULUS:
        raise ValueError("This demo circuit is intentionally specialized to N = 15.")
    if math.gcd(base, modulus) != 1:
        raise ValueError("Base and modulus must be coprime.")

    total_qubits = counting_qubits + 4
    circuit = QuantumCircuit(total_qubits, counting_qubits)

    for qubit in range(counting_qubits):
        circuit.h(qubit)

    # Initialize the work register to |1>.
    circuit.x(counting_qubits)

    for qubit in range(counting_qubits):
        power = 2**qubit
        circuit.append(
            _controlled_amod_15(base, power),
            [qubit, *range(counting_qubits, total_qubits)],
        )

    circuit.append(
        QFT(counting_qubits, inverse=True, do_swaps=True),
        range(counting_qubits),
    )
    circuit.measure(range(counting_qubits), range(counting_qubits))
    return circuit


def _factors_from_order(modulus: int, base: int, order: int) -> tuple[int, int] | None:
    if order <= 0 or order % 2 != 0:
        return None

    midpoint = pow(base, order // 2, modulus)
    if midpoint in (1, modulus - 1):
        return None

    factor_a = math.gcd(midpoint - 1, modulus)
    factor_b = math.gcd(midpoint + 1, modulus)
    if 1 < factor_a < modulus and 1 < factor_b < modulus:
        return tuple(sorted((factor_a, factor_b)))
    return None


def _extract_order_from_bitstring(bitstring: str) -> int:
    numerator = int(bitstring, 2)
    denominator = 2 ** len(bitstring)
    phase = Fraction(numerator, denominator)
    return phase.limit_denominator(SUPPORTED_SHOR_MODULUS).denominator


def factor_toy_rsa_modulus(
    modulus: int,
    base: int = 2,
    counting_qubits: int = 8,
    shots: int = 2048,
) -> ShorAttackResult:
    """Factor the canonical tiny RSA modulus N = 15 using a real order-finding circuit."""
    if modulus != SUPPORTED_SHOR_MODULUS:
        raise ValueError("This Shor demo is intentionally implemented only for N = 15.")

    circuit = build_shor_order_finding_circuit(
        modulus=modulus,
        base=base,
        counting_qubits=counting_qubits,
    )
    simulator = AerSimulator()
    compiled = transpile(circuit, simulator)
    counts = simulator.run(compiled, shots=shots).result().get_counts()

    for bitstring, _ in Counter(counts).most_common():
        recovered_order = _extract_order_from_bitstring(bitstring)
        factors = _factors_from_order(modulus, base, recovered_order)
        if factors is None:
            continue

        numerator = int(bitstring, 2)
        sampled_phase = f"{numerator}/{2 ** len(bitstring)}"
        return ShorAttackResult(
            modulus=modulus,
            factors=factors,
            base=base,
            sampled_bitstring=bitstring,
            sampled_phase=sampled_phase,
            recovered_order=recovered_order,
            counting_qubits=counting_qubits,
            shots=shots,
        )

    raise ValueError("Failed to recover non-trivial factors from the order-finding circuit.")
