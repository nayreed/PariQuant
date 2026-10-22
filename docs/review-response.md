# Response to the proposal review (S. Adhikari, 2 October 2026)

The seven comments of the annotated PDF (`PariQuant_subarna.pdf`) are tracked as issues #2–#8 under #1. The positions below are the ones set out in the issue comments of 9 October 2026 and in the summary to Subarna; they are **proposals for discussion**, and this change implements them in the proposal text and reference code. Nothing here claims completed hardware validation. Each row cites the passage of [`proposal/PariQuant.md`](proposal/PariQuant.md) that carries the change (marked ⟨R*n*⟩ in the text).

| Issue | Comment | Change in the proposal | Reference code / data |
|---|---|---|---|
| [#2](https://github.com/nayreed/PariQuant/issues/2) | "how will you collect noise information?" | New Sec. 4.4: noise is *provider-reported calibration and characterization context* with provenance, not a physical noise model; eight-step collection procedure; per-provider table; observed/derived/unavailable status and provenance kinds; no imputation. Sec. 5.2 adds the live exact-backend audit. Abstract and Sec. 4.2 reworded | `schemas/context_record.schema.json`, `pariquant/context.py`, `tests/test_context.py` |
| [#3](https://github.com/nayreed/PariQuant/issues/3) | "will you be creating these rules or are there some rule generation algorithms?" | Sec. 4.3: first version is researcher-defined, in a versioned rule table; pilot/held-out split; frozen version and hash; predeclared sensitivity (0.5×, 2×); interval-based three-way decision with explicit aggregation and multiplicity note; what a match does and does not mean. RQ3 mentions sensitivity | `rules/rule_table_v0.1.json` (draft, **no tolerances chosen**), `pariquant/decision.py`, `tests/test_decision.py` |
| [#4](https://github.com/nayreed/PariQuant/issues/4) | "what is wire ordering?" | The phrase is gone. Sec. 4.0 defines circuit-qubit order, physical layout, measurement mapping and bitstring convention; Sec. 4.1 gives the two-qubit example and requires asymmetric validation circuits | `pariquant/bitorder.py`, `tests/test_bitorder.py` |
| [#5](https://github.com/nayreed/PariQuant/issues/5) | "approximation error of what?" | Sec. 4.1: approximation error = deviation from the ideal reference computation introduced by an explicitly permitted approximate synthesis step, noiseless, after mapping normalisation; metric table (state infidelity, TVD, operator infidelity), tolerance and provenance fields; exact transformations preferred; floating-point residual kept separate | `pariquant/validation.py`, `tests/test_validation.py` (CNOT ↔ CZ and MS-style decompositions are exact up to phase; a 10⁻² rotation error gives sin²(θ/2)) |
| [#6](https://github.com/nayreed/PariQuant/issues/6) | "…it is something you specify yourself in the program with shots value" | "Measurement repetitions" replaced by *requested shots*, an experiment setting; four separately recorded quantities (requested, provider-reported executed, returned, retained) plus repeated jobs (Sec. 4.0, 4.2, 5.3) | `pariquant/shots.py`, `tests/test_shots.py` |
| [#7](https://github.com/nayreed/PariQuant/issues/7) | "does that mean at minimum 12 physical qubits?" | Sec. 5.3: "at most 12 circuit qubits, including required ancillas", an upper bound, smaller workloads allowed; data qubits / width / occupied physical qubits recorded separately; "logical qubits" replaced by "circuit qubits"; feasibility checked per backend | rule `occupied_physical_qubits` |
| [#8](https://github.com/nayreed/PariQuant/issues/8) | "…different correlated or coherent noise behavior with statistical evidence or with certainty" | Sec. 5.3: noise known by construction in simulation (with the over-rotation vs. stochastic example); Sec. 5.4: hardware inference standard (repeat, interleave, prespecified analysis, mechanism claims only with dedicated characterization); limitations updated | `tests/test_validation.py::test_coherent_overrotation_…` |

Subarna's two suggestions in the e-mail are in the Month-1 work plan: use provider resource estimators (the IonQ one is reference [35]; note it estimates price from qubits, gates and shots) and create provider accounts to check for student credits.

## Open decisions for you (from the "Decisions to discuss" list in #1)

The text takes the position proposed in the issues. These remain **yours** (or the supervisors') to confirm, and the text should change if the answer differs:

1. **Essential descriptors.** The draft rule table marks occupied physical qubits, native two-qubit operations, scheduled duration and requested shots as *required* and the rest as *supplementary*. This is a placeholder proposal.
2. **Validation scope (#5).** The text defaults to full-operation (unitary) validation for the ≤12-circuit-qubit Phase-1 circuits and uses fixed-input/distribution checks where ancillas, mixed outputs or mid-circuit measurements rule that out. Say if you want fixed-input workloads only.
3. **Simulation-first scope (#8).** Mechanism-specific coherent/correlated-noise claims are confined to controlled simulation. Say if a hardware noise mechanism must be identified in the paper.
4. **Provider-reported context sufficient (#2).** Taken as sufficient for the initial hardware evaluation.
5. **Rule-based vs. learned rules (#3).** First version researcher-defined only.

## Not done (and why)

- The live exact-backend payload audit (#2), the tolerances (#3) and the interval/multiplicity design (#3) are still pending by design; the draft rule table refuses to produce a decision until it is frozen with tolerances.
- The proposal was only available as a PDF, so it has been transcribed into Markdown; the LaTeX/LNCS source was not in the repository. If you send the `.tex`, the changes can be ported to it.
- The issues were not edited or closed, and no comments were posted on them.
- The AQT "T1 is a literature value" statement in #2 could not be confirmed (see [`references.md`](references.md)) and is not asserted in the proposal.
