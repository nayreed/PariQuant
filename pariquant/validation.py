"""Noiseless translation-validation metrics.

"Approximation error" in PariQuant means the deviation introduced by an explicitly
permitted approximate translation or synthesis step, measured between *noiseless*
objects computed from the reference circuit and the translated circuit, after layout
and measurement mappings are normalised (see ``bitorder``). It is not hardware noise
and not finite-shot sampling uncertainty.

Target (declared before evaluation) selects the metric:

- fixed-input output state ........ ``state_infidelity``
- output distribution ............. ``total_variation_distance``
- full operation (unitary) ........ ``operator_infidelity``

``numerical_residual`` scale deviations (~1e-12) are recorded separately and are
not evidence of approximate synthesis.
"""

from __future__ import annotations

import numpy as np

_EPS = 1e-12


def _unit(psi) -> np.ndarray:
    v = np.asarray(psi, dtype=complex).reshape(-1)
    norm = np.linalg.norm(v)
    if norm < _EPS:
        raise ValueError("zero vector")
    return v / norm


def state_infidelity(psi_ref, psi_translated) -> float:
    """epsilon_state = 1 - |<psi_ref | psi_translated>|^2 (global-phase invariant)."""
    a, b = _unit(psi_ref), _unit(psi_translated)
    if a.shape != b.shape:
        raise ValueError(f"dimension mismatch: {a.shape} vs {b.shape}")
    return float(max(0.0, 1.0 - abs(np.vdot(a, b)) ** 2))


def operator_infidelity(u_ref, u_translated) -> float:
    """epsilon_op = 1 - |Tr(U_ref^dagger U_translated)|^2 / d^2 (global-phase invariant).

    This is one minus the process (entanglement) fidelity of the two unitaries.
    Average gate fidelity is F_avg = (d * (1 - epsilon_op) + 1) / (d + 1).
    It is zero iff the unitaries agree up to global phase.
    """
    u = np.asarray(u_ref, dtype=complex)
    v = np.asarray(u_translated, dtype=complex)
    if u.shape != v.shape or u.ndim != 2 or u.shape[0] != u.shape[1]:
        raise ValueError(f"need equal square matrices, got {u.shape} and {v.shape}")
    d = u.shape[0]
    return float(max(0.0, 1.0 - abs(np.trace(u.conj().T @ v)) ** 2 / d**2))


def average_gate_infidelity_from_operator(eps_op: float, d: int) -> float:
    """1 - F_avg for a unitary difference with process infidelity ``eps_op``."""
    return float(eps_op * d / (d + 1))


def total_variation_distance(p, q) -> float:
    """TVD between two probability distributions given as dicts over the same
    (common-ordering) outcome keys; missing keys count as probability 0."""
    keys = set(p) | set(q)
    return 0.5 * float(sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys))


def validate_translation(metric_value: float, tolerance: float, *, scope: str, metric: str) -> dict:
    """Provenance record for one validation: metric, tolerance, deviation, scope, verdict."""
    if scope not in {"fixed_input_state", "output_distribution", "full_operation"}:
        raise ValueError(f"unknown validation scope {scope!r}")
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    return {
        "scope": scope,
        "metric": metric,
        "tolerance": tolerance,
        "observed_deviation": metric_value,
        "passed": bool(metric_value <= tolerance),
    }
