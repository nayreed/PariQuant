import numpy as np
import pytest

from pariquant.validation import (
    average_gate_infidelity_from_operator,
    operator_infidelity,
    state_infidelity,
    total_variation_distance,
    validate_translation,
)

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]])
Z = np.diag([1, -1]).astype(complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
CZ = np.diag([1, 1, 1, -1]).astype(complex)
# qubit order here: first Kronecker factor = control, second = target
CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)


def exp_pauli(p, theta):
    """exp(-i theta p / 2) for a Pauli-type involution p."""
    return np.cos(theta / 2) * np.eye(p.shape[0]) - 1j * np.sin(theta / 2) * p


def rx(t): return exp_pauli(X, t)
def ry(t): return exp_pauli(Y, t)
def rz(t): return exp_pauli(Z, t)
def rxx(t): return exp_pauli(np.kron(X, X), t)


def on_control(a): return np.kron(a, I2)
def on_target(a): return np.kron(I2, a)


def test_global_phase_is_ignored():
    psi = np.array([1, 1j, 0, 0]) / np.sqrt(2)
    assert state_infidelity(psi, np.exp(0.7j) * psi) < 1e-15
    assert operator_infidelity(CNOT, np.exp(1.3j) * CNOT) < 1e-15


def test_orthogonal_states_have_unit_infidelity():
    assert state_infidelity([1, 0], [0, 1]) == pytest.approx(1.0)


def test_cz_translation_of_cnot_is_exact():
    translated = on_target(H) @ CZ @ on_target(H)
    assert operator_infidelity(CNOT, translated) < 1e-14


def test_ms_style_translation_of_cnot_is_exact_up_to_phase():
    # Ry_c(pi/2); Rxx(pi/2); Rx_c(-pi/2) Rx_t(-pi/2); Ry_c(-pi/2)   (time order)
    sequence = [
        on_control(ry(np.pi / 2)),
        rxx(np.pi / 2),
        on_control(rx(-np.pi / 2)),
        on_target(rx(-np.pi / 2)),
        on_control(ry(-np.pi / 2)),
    ]
    u = np.eye(4, dtype=complex)
    for g in sequence:
        u = g @ u
    assert operator_infidelity(CNOT, u) < 1e-14


def test_small_rotation_error_gives_known_infidelity():
    # extra Rz(theta) on the control: 1 - |Tr|^2/d^2 = sin^2(theta/2)
    theta = 1e-2
    translated = on_control(rz(theta)) @ CNOT
    assert operator_infidelity(CNOT, translated) == pytest.approx(np.sin(theta / 2) ** 2, rel=1e-9)


def test_wrong_gate_order_or_swapped_qubits_is_detected():
    # control and target exchanged: swaps |01> and |11> instead of |10> and |11>
    cnot_reversed = np.eye(4, dtype=complex)
    cnot_reversed[[1, 3]] = cnot_reversed[[3, 1]]
    assert operator_infidelity(CNOT, cnot_reversed) > 0.5


def test_average_gate_infidelity_relation():
    eps = 0.04
    d = 4
    assert average_gate_infidelity_from_operator(eps, d) == pytest.approx(1 - (d * (1 - eps) + 1) / (d + 1))


def test_total_variation_distance():
    assert total_variation_distance({"0": 0.5, "1": 0.5}, {"0": 0.5, "1": 0.5}) == 0
    assert total_variation_distance({"0": 1.0}, {"1": 1.0}) == 1.0
    assert total_variation_distance({"0": 0.75, "1": 0.25}, {"0": 0.5, "1": 0.5}) == pytest.approx(0.25)


def test_shape_and_scope_checks():
    with pytest.raises(ValueError):
        state_infidelity([1, 0], [1, 0, 0, 0])
    with pytest.raises(ValueError):
        operator_infidelity(np.eye(2), np.eye(4))
    with pytest.raises(ValueError):
        validate_translation(0.0, 1e-9, scope="everything", metric="x")


def test_validation_record():
    rec = validate_translation(2e-15, 1e-9, scope="full_operation", metric="operator_infidelity")
    assert rec["passed"] and rec["scope"] == "full_operation"
    assert not validate_translation(1e-3, 1e-9, scope="fixed_input_state", metric="state_infidelity")["passed"]


def test_coherent_overrotation_accumulates_quadratically_unlike_matched_stochastic_error():
    theta = 1e-2
    r = operator_infidelity(I2, rz(theta))  # process infidelity of one over-rotation
    assert r == pytest.approx(np.sin(theta / 2) ** 2)
    for n in (1, 10, 100):
        coherent = operator_infidelity(I2, rz(n * theta))  # n repetitions of the same unitary
        stochastic = 1 - (1 - r) ** n  # n repetitions of a stochastic channel with the same r
        assert coherent == pytest.approx(np.sin(n * theta / 2) ** 2)
        if n == 100:
            assert coherent > 50 * stochastic  # ~ n^2 r vs ~ n r
        if n == 1:
            assert coherent == pytest.approx(stochastic)
