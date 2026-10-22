"""Wire-ordering checks with asymmetric known-output circuits.

A tiny exact simulator for X gates is enough: qubit k is bit k of the basis index
(little-endian), so Qiskit writes the string with qubit n-1 leftmost.
"""

import numpy as np
import pytest

from pariquant.bitorder import (
    LEFTMOST_IS_BIT0,
    RIGHTMOST_IS_BIT0,
    basis_index_to_string,
    normalize_bitstring,
    normalize_counts,
    permute_qubits,
    string_to_clbits,
)


def x_circuit_result(x_on, n=2):
    return sum(1 << q for q in x_on)  # basis index after X on the listed qubits


def test_issue4_example_q0_flipped_displays_01_in_qiskit():
    idx = x_circuit_result([0])
    assert basis_index_to_string(idx, 2, RIGHTMOST_IS_BIT0) == "01"
    assert basis_index_to_string(idx, 2, LEFTMOST_IS_BIT0) == "10"


@pytest.mark.parametrize("x_on", [[0], [1], [0, 1], []])
@pytest.mark.parametrize("convention", [RIGHTMOST_IS_BIT0, LEFTMOST_IS_BIT0])
def test_identity_measurement_maps_back_to_circuit_qubits(x_on, convention):
    s = basis_index_to_string(x_circuit_result(x_on), 2, convention)
    out = normalize_bitstring(s, convention, {0: 0, 1: 1})
    assert out == tuple(int(q in x_on) for q in range(2))


def test_asymmetric_circuits_are_distinguished_but_symmetric_one_is_not():
    only_q0 = basis_index_to_string(x_circuit_result([0]), 2, RIGHTMOST_IS_BIT0)
    only_q1 = basis_index_to_string(x_circuit_result([1]), 2, RIGHTMOST_IS_BIT0)
    assert only_q0 != only_q1
    # Reading the right strings in the wrong direction swaps the two answers ...
    assert normalize_bitstring(only_q0, LEFTMOST_IS_BIT0, {0: 0, 1: 1}) == (0, 1)
    # ... whereas 00 / 11 cannot expose a reversal.
    for s in ("00", "11"):
        assert normalize_bitstring(s, LEFTMOST_IS_BIT0, {0: 0, 1: 1}) == normalize_bitstring(
            s, RIGHTMOST_IS_BIT0, {0: 0, 1: 1}
        )


def test_nontrivial_measurement_mapping():
    # measure q0 -> c1 and q1 -> c0, X applied on q0 only: c1 = 1, c0 = 0
    measure_map = {0: 1, 1: 0}
    qiskit_string = "10"  # c1 c0
    assert normalize_bitstring(qiskit_string, RIGHTMOST_IS_BIT0, measure_map) == (1, 0)
    # same physical result under the opposite string convention
    assert normalize_bitstring("01", LEFTMOST_IS_BIT0, measure_map) == (1, 0)


def test_partial_measurement_and_counts_merge():
    # three clbits, only q2 -> c0 measured: other clbits ignored, strings merge
    counts = {"001": 10, "101": 5, "000": 7}
    out = normalize_counts(counts, RIGHTMOST_IS_BIT0, {2: 0})
    assert out == {(1,): 15, (0,): 7}


def test_bad_inputs():
    with pytest.raises(ValueError):
        string_to_clbits("01", "sideways")
    with pytest.raises(ValueError):
        string_to_clbits("0a", RIGHTMOST_IS_BIT0)
    with pytest.raises(ValueError):
        normalize_bitstring("01", RIGHTMOST_IS_BIT0, {0: 5})


def test_permute_qubits_state_matches_relabelled_x():
    n = 3
    ket = lambda idx: np.eye(2**n)[idx].astype(complex)
    # X on old qubit 0 -> |001>; relabel old qubit 0 as new qubit 2
    perm = [1, 2, 0]  # new qubit k <- old qubit perm[k]  (new 0<-old 1, new 1<-old 2, new 2<-old 0)
    out = permute_qubits(ket(0b001), perm)
    assert np.allclose(out, ket(0b100))
    out = permute_qubits(ket(0b010), perm)  # old qubit 1 -> new qubit 0
    assert np.allclose(out, ket(0b001))


def test_permute_qubits_unitary_swap():
    # CNOT(control 0, target 1) relabelled by swapping qubits equals CNOT(control 1, target 0)
    cnot01 = np.eye(4, dtype=complex)
    cnot01[[1, 3]] = cnot01[[3, 1]]  # control = qubit 0 (LSB): swaps |01> and |11>
    cnot10 = np.eye(4, dtype=complex)
    cnot10[[2, 3]] = cnot10[[3, 2]]  # control = qubit 1: swaps |10> and |11>
    assert np.allclose(permute_qubits(cnot01, [1, 0]), cnot10)


def test_permute_rejects_non_permutation():
    with pytest.raises(ValueError):
        permute_qubits(np.eye(4), [0, 0])
