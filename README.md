# PariQuant

PariQuant asks under what stated conditions the resources used to implement the **same workload** on different quantum processors (superconducting and trapped-ion) can be meaningfully compared. It does not assume a universal conversion between native gates; it builds an auditable accounting record for each compiled implementation and compares records with pre-specified rules and tolerances. A resource match is conditional on the named descriptors, tolerances and evidence standard; it does not imply equal output quality or identical noise.

Initial targets (2 × 2 design): IBM Berlin and IQM Emerald (superconducting); AQT IBEX-Q1 and IonQ Forte-1 (trapped ion).

## Contents

| Path | What it is |
|---|---|
| [`docs/proposal/PariQuant.md`](docs/proposal/PariQuant.md) | The research proposal (revised after the review of 2 Oct 2026) |
| [`docs/review-response.md`](docs/review-response.md) | Each review comment → what changed, plus open decisions |
| [`docs/references.md`](docs/references.md) | Checked references and links, and which papers are still missing |
| [`pariquant/`](pariquant) | Reference implementation of the definitions in the proposal |
| [`schemas/context_record.schema.json`](schemas/context_record.schema.json) | Execution-context record (provider-reported calibration context with provenance) |
| [`rules/rule_table_v0.1.json`](rules/rule_table_v0.1.json) | Draft, versioned comparison-rule table (no tolerances chosen yet) |
| [`tests/`](tests) | Tests, including known-output bit-order circuits and exact/approximate gate translations |

## Modules

- `bitorder`: circuit-qubit identity, measurement mapping and bitstring conventions ("wire ordering")
- `validation`: noiseless translation-validation metrics (state / operator infidelity, TVD)
- `shots`: requested vs. executed vs. returned vs. retained samples
- `context`: provider-reported calibration context with evidence status and provenance
- `decision`: frozen rule tables and the matched / different / insufficient-evidence decision

## Development

```bash
pip install -e '.[dev]'
pytest
```

The code depends only on NumPy (`jsonschema` is used by one test). It contains no provider credentials and makes no network calls.

## License

Apache-2.0, see [`LICENSE`](LICENSE).
