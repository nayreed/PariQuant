import json
from pathlib import Path

import pytest

from pariquant.context import ContextField, ContextRecord, Snapshot, payload_hash

jsonschema = pytest.importorskip("jsonschema")
SCHEMA = json.loads((Path(__file__).parents[1] / "schemas" / "context_record.schema.json").read_text())


def snap(updated, cal_id=None):
    return Snapshot(
        retrieval_time="2026-10-22T12:00:00Z",
        source_api="GetDevice",
        raw_payload_hash=payload_hash({"updated": updated}),
        raw_payload_location="runs/0001/pre.json",
        provider_updated_at=updated,
        calibration_or_characterization_id=cal_id,
    )


def record(*snapshots):
    return ContextRecord(
        provider="aws-braket",
        backend_id="Emerald",
        task_or_job_id="arn:aws:braket:...:quantum-task/x",
        execution_start="2026-10-22T12:01:00Z",
        execution_end="2026-10-22T12:02:00Z",
        snapshots=tuple(snapshots),
        fields=(
            ContextField("T1", "qubit", "observed", "near-run-current", value=40e-6, unit="s"),
            ContextField("cz_duration", "operation", "unavailable"),
            ContextField(
                "cz_error", "operation", "derived", "near-run-current", value=0.005,
                derivation="1 - cz_fidelity (v1)",
            ),
        ),
    )


def test_record_validates_against_schema():
    jsonschema.validate(record(snap("a"), snap("a")).to_dict(), SCHEMA)


def test_schema_rejects_imputed_unavailable_value_and_underived_derived_field():
    base = record(snap("a")).to_dict()
    bad = json.loads(json.dumps(base))
    bad["fields"][1]["value"] = 1.0
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, SCHEMA)
    bad = json.loads(json.dumps(base))
    del bad["fields"][2]["derivation"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, SCHEMA)


def test_field_rules_match_schema_rules():
    with pytest.raises(ValueError):
        ContextField("T1", "qubit", "unavailable", value=1.0)
    with pytest.raises(ValueError):
        ContextField("x", "qubit", "derived", "near-run-current", value=1.0)
    with pytest.raises(ValueError):
        ContextField("x", "qubit", "observed", value=1.0)  # provenance missing
    with pytest.raises(ValueError):
        ContextField("x", "qubit", "observed", "guessed", value=1.0)


def test_crossing_a_characterization_change():
    assert record(snap("a"), snap("a")).crosses_characterization_change() is False
    assert record(snap("a"), snap("b")).crosses_characterization_change() is True
    assert record(snap("a")).crosses_characterization_change() is None
    no_ids = Snapshot("t", "api", payload_hash("x"), "loc")
    assert record(no_ids, no_ids).crosses_characterization_change() is None


def test_payload_hash_is_canonical():
    assert payload_hash({"b": 1, "a": 2}) == payload_hash({"a": 2, "b": 1})
