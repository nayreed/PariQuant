"""Circuit-qubit identity and bitstring conventions ("wire ordering").

Three records are kept apart (docs/proposal/PariQuant.md, Sec. 4.1):

1. circuit-qubit order: which abstract circuit qubit each index names;
2. physical layout: which hardware qubit realises each circuit qubit (recorded,
   never needed to read results, because results are indexed by classical bit);
3. measurement mapping and bitstring convention: which classical bit receives
   each measured circuit qubit, and how a returned string is ordered.

Everything is converted to one *common ordering*: a tuple whose entry ``k`` is the
measured value of the ``k``-th entry of ``measured_qubits`` (ascending circuit-qubit
index by default). The convention name is explicit, so a string is never read in an
implicit direction.
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable, Mapping, Sequence

# Direction in which a returned string lists classical bits.
RIGHTMOST_IS_BIT0 = "rightmost_is_bit0"  # Qiskit classical-register strings: c_{n-1} ... c_0
LEFTMOST_IS_BIT0 = "leftmost_is_bit0"  # c_0 ... c_{n-1}
CONVENTIONS = (RIGHTMOST_IS_BIT0, LEFTMOST_IS_BIT0)


def string_to_clbits(bitstring: str, convention: str) -> tuple[int, ...]:
    """Return ``(c_0, c_1, ...)`` for a returned string under ``convention``."""
    if convention not in CONVENTIONS:
        raise ValueError(f"unknown bitstring convention {convention!r}; expected one of {CONVENTIONS}")
    bits = tuple(int(ch) for ch in bitstring.replace(" ", ""))
    if any(b not in (0, 1) for b in bits):
        raise ValueError(f"not a bitstring: {bitstring!r}")
    return bits[::-1] if convention == RIGHTMOST_IS_BIT0 else bits


def normalize_bitstring(
    bitstring: str,
    convention: str,
    measure_map: Mapping[int, int],
    measured_qubits: Sequence[int] | None = None,
) -> tuple[int, ...]:
    """Convert one returned string to the common ordering.

    ``measure_map`` maps circuit qubit -> classical bit that received its
    measurement (``measure q[q] -> c[measure_map[q]]``). The result lists the
    measured value of each circuit qubit in ``measured_qubits`` order
    (ascending circuit-qubit index when omitted).
    """
    clbits = string_to_clbits(bitstring, convention)
    qubits = tuple(sorted(measure_map)) if measured_qubits is None else tuple(measured_qubits)
    try:
        return tuple(clbits[measure_map[q]] for q in qubits)
    except (KeyError, IndexError) as exc:
        raise ValueError(
            f"measure_map {dict(measure_map)} is inconsistent with a {len(clbits)}-bit string"
        ) from exc


def normalize_counts(
    counts: Mapping[str, int],
    convention: str,
    measure_map: Mapping[int, int],
    measured_qubits: Sequence[int] | None = None,
) -> Counter:
    """Convert a counts dictionary to the common ordering (tuple keys), merging
    strings that coincide after dropping unmeasured classical bits."""
    out: Counter = Counter()
    for bitstring, n in counts.items():
        out[normalize_bitstring(bitstring, convention, measure_map, measured_qubits)] += n
    return out


def common_ordering_distribution(
    counts: Mapping[str, int],
    convention: str,
    measure_map: Mapping[int, int],
    measured_qubits: Sequence[int] | None = None,
) -> dict[tuple[int, ...], float]:
    """Empirical probabilities in the common ordering."""
    norm = normalize_counts(counts, convention, measure_map, measured_qubits)
    total = sum(norm.values())
    if total == 0:
        raise ValueError("empty counts")
    return {k: v / total for k, v in norm.items()}


def basis_index_to_string(index: int, n_bits: int, convention: str = RIGHTMOST_IS_BIT0) -> str:
    """String for computational-basis state ``index`` when bit ``k`` is the value of
    qubit/clbit ``k`` (little-endian index, as in a Qiskit statevector)."""
    bits = [(index >> k) & 1 for k in range(n_bits)]  # bits[k] = value of bit k
    ordered = bits[::-1] if convention == RIGHTMOST_IS_BIT0 else bits
    return "".join(map(str, ordered))


def permute_qubits(state_or_unitary, perm: Iterable[int]):
    """Relabel qubits of a state vector or unitary (little-endian: qubit 0 is the
    least significant index bit). ``perm[k]`` is the *old* qubit that becomes new
    qubit ``k``. Used to express a translated circuit in the reference circuit-qubit
    order before comparing it."""
    import numpy as np

    perm = list(perm)
    n = len(perm)
    if sorted(perm) != list(range(n)):
        raise ValueError(f"{perm} is not a permutation of range({n})")
    arr = np.asarray(state_or_unitary)
    dim = 1 << n
    if arr.shape not in ((dim,), (dim, dim)):
        raise ValueError(f"shape {arr.shape} does not match {n} qubits")
    # Tensor axes are ordered most-significant qubit first: axis a <-> qubit n-1-a.
    axes_new = [n - 1 - old for old in reversed(perm)]
    if arr.ndim == 1:
        return arr.reshape((2,) * n).transpose(axes_new).reshape(dim)
    t = arr.reshape((2,) * (2 * n))
    full = axes_new + [n + a for a in axes_new]
    return t.transpose(full).reshape(dim, dim)
