from pathlib import Path

import pytest

from pariquant.decision import (
    DIFFERENT,
    INSUFFICIENT,
    MATCHED,
    Interval,
    Rule,
    RuleTable,
    classify_descriptor,
    combine,
)

TABLE_PATH = Path(__file__).parents[1] / "rules" / "rule_table_v0.1.json"


def test_three_way_classification():
    assert classify_descriptor(Interval(-1, 2), 3) == MATCHED
    assert classify_descriptor(Interval(4, 6), 3) == DIFFERENT
    assert classify_descriptor(Interval(2, 4), 3) == INSUFFICIENT  # crosses the boundary
    assert classify_descriptor(Interval(-1, 1), 0.5) == INSUFFICIENT  # failing to reject != equivalence
    assert classify_descriptor(None, 3) == INSUFFICIENT  # missing evidence


def test_asymmetric_equivalence_region():
    assert classify_descriptor(Interval(-0.4, 0.4), 0.5, 1.0) == MATCHED
    assert classify_descriptor(Interval(0.9, 1.1), 0.5, 1.0) == INSUFFICIENT
    assert classify_descriptor(Interval(-3, -2), 0.5, 1.0) == DIFFERENT
    assert classify_descriptor(Interval.exact(0), 0) == MATCHED
    assert classify_descriptor(Interval.exact(2), 0) == DIFFERENT


def test_combination():
    req = {"a", "b"}
    assert combine({"a": MATCHED, "b": MATCHED}, req) == MATCHED
    assert combine({"a": MATCHED, "b": INSUFFICIENT}, req) == INSUFFICIENT
    assert combine({"a": DIFFERENT, "b": INSUFFICIENT}, req) == DIFFERENT
    assert combine({"a": MATCHED}, req) == INSUFFICIENT  # missing required result
    assert combine({"a": MATCHED, "b": MATCHED, "ctx": DIFFERENT}, req) == MATCHED  # supplementary ignored


def make_table(status="frozen", tol=None):
    return RuleTable(
        version="t1",
        status=status,
        rules=(
            Rule("qubits", "d", "qubits", "required", "exact"),
            Rule("duration", "d", "s", "required", "numerical", tolerance=tol),
            Rule("context", "d", "-", "supplementary", "numerical", tolerance={"low": 1.0}),
        ),
    )


def test_table_refuses_to_decide_until_frozen_with_tolerances():
    diffs = {"qubits": Interval.exact(0), "duration": Interval(-1, 1)}
    with pytest.raises(RuntimeError):
        make_table(status="draft", tol={"low": 2}).decide(diffs)
    with pytest.raises(RuntimeError):
        make_table(tol=None).decide(diffs)
    out = make_table(tol={"low": 2}).decide(diffs)
    assert out["overall"] == MATCHED and out["per_descriptor"]["qubits"] == MATCHED


def test_exact_descriptor_difference_decides_overall():
    out = make_table(tol={"low": 2}).decide({"qubits": Interval.exact(3), "duration": Interval(-1, 1)})
    assert out["per_descriptor"]["qubits"] == DIFFERENT and out["overall"] == DIFFERENT


def test_sensitivity_uses_predeclared_multipliers_and_primary_is_unchanged():
    table = make_table(tol={"low": 2})
    diffs = {"qubits": Interval.exact(0), "duration": Interval(-1.5, 1.5)}
    sens = table.sensitivity(diffs)
    assert sens == {0.5: INSUFFICIENT, 1.0: MATCHED, 2.0: MATCHED}
    assert table.decide(diffs)["overall"] == sens[1.0]


def test_rule_hash_changes_with_content():
    assert make_table(tol={"low": 2}).canonical_hash() != make_table(tol={"low": 3}).canonical_hash()


def test_shipped_draft_table_is_not_evaluable_and_sets_no_tolerances():
    table = RuleTable.load(TABLE_PATH)
    assert table.status == "draft" and not table.ready_for_evaluation()
    assert "native_two_qubit_operations" in table.unset_required_tolerances()
    assert all(r.tolerance is None for r in table.rules)
    with pytest.raises(RuntimeError):
        table.decide({})
