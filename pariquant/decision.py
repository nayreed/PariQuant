"""Frozen rule tables and the three-way resource-comparison decision.

Per descriptor, for a difference ``d`` between two implementations with uncertainty
interval ``[lo, hi]`` and an equivalence region ``[-tol_low, tol_high]`` (0 inside it):

- ``matched``       interval lies wholly inside the region (equivalence shown, as in a
                    two one-sided tests procedure at the interval's level);
- ``different``     interval lies wholly outside the region (mismatch shown);
- ``insufficient``  interval crosses a boundary, or required evidence is missing.

Failure to detect a difference is never read as equivalence. Exact quantities (counts)
use a degenerate interval ``lo == hi`` and need no invented sampling uncertainty.

Overall (required descriptors only; per-descriptor results are always preserved):
any ``different`` -> ``different``; else all ``matched`` -> ``matched``; else
``insufficient``. A ``matched`` verdict is an intersection-union test, so each
descriptor is tested at level alpha without multiplicity correction; a ``different``
verdict from any one of k descriptors is a union of rejections and the interval used
for it should be corrected (e.g. Bonferroni, alpha/k). The interval construction,
confidence level and repeated-run design are fixed in the Month-3 pre-specification.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional

MATCHED, DIFFERENT, INSUFFICIENT = "matched", "different", "insufficient"


@dataclass(frozen=True)
class Interval:
    lo: float
    hi: float

    def __post_init__(self) -> None:
        if self.lo > self.hi:
            raise ValueError(f"empty interval [{self.lo}, {self.hi}]")

    @classmethod
    def exact(cls, value: float) -> "Interval":
        return cls(value, value)


def classify_descriptor(
    difference: Optional[Interval], tol_low: float, tol_high: Optional[float] = None
) -> str:
    """Classify one descriptor. ``difference=None`` means the evidence is missing."""
    if tol_high is None:
        tol_high = tol_low
    if tol_low < 0 or tol_high < 0:
        raise ValueError("tolerances must be non-negative")
    if difference is None:
        return INSUFFICIENT
    lo_bound, hi_bound = -tol_low, tol_high
    if difference.lo >= lo_bound and difference.hi <= hi_bound:
        return MATCHED
    if difference.hi < lo_bound or difference.lo > hi_bound:
        return DIFFERENT
    return INSUFFICIENT


def _classify_exact(difference: Optional[Interval]) -> str:
    """Exact quantities (counts): equal, unequal, or not determined."""
    if difference is None or difference.lo != difference.hi:
        return INSUFFICIENT
    return MATCHED if difference.lo == 0 else DIFFERENT


def combine(results: Mapping[str, str], required: set[str]) -> str:
    """Overall decision from per-descriptor results (required descriptors only)."""
    missing = required - set(results)
    if missing:
        # a required descriptor with no result is missing evidence
        results = {**results, **{name: INSUFFICIENT for name in missing}}
    required_results = [results[name] for name in required]
    if not required_results:
        raise ValueError("no required descriptors")
    if DIFFERENT in required_results:
        return DIFFERENT
    if all(r == MATCHED for r in required_results):
        return MATCHED
    return INSUFFICIENT


@dataclass(frozen=True)
class Rule:
    name: str
    definition: str
    unit: str
    role: str  # "required" or "supplementary"
    comparison: str  # "exact" or "numerical"
    tolerance: Optional[dict] = None  # {"low": x, "high": y} on the compared scale; None until set from pilot
    applicability: str = ""

    @property
    def required(self) -> bool:
        return self.role == "required"


@dataclass(frozen=True)
class RuleTable:
    version: str
    status: str  # "draft" until frozen
    rules: tuple[Rule, ...]
    sensitivity_multipliers: tuple[float, ...] = (0.5, 1.0, 2.0)

    @classmethod
    def load(cls, path: str | Path) -> "RuleTable":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        rules = tuple(Rule(**r) for r in data["rules"])
        return cls(
            version=data["version"],
            status=data["status"],
            rules=rules,
            sensitivity_multipliers=tuple(data.get("sensitivity_multipliers", (0.5, 1.0, 2.0))),
        )

    def canonical_hash(self) -> str:
        """Hash of the substantive content; identifies the frozen rule version."""
        body = {
            "version": self.version,
            "rules": [r.__dict__ for r in self.rules],
            "sensitivity_multipliers": list(self.sensitivity_multipliers),
        }
        return hashlib.sha256(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()

    def unset_required_tolerances(self) -> list[str]:
        return [
            r.name
            for r in self.rules
            if r.required and r.comparison == "numerical" and r.tolerance is None
        ]

    def ready_for_evaluation(self) -> bool:
        return self.status == "frozen" and not self.unset_required_tolerances()

    def decide(self, differences: Mapping[str, Optional[Interval]], tolerance_scale: float = 1.0) -> dict:
        """Apply the table to per-descriptor difference intervals.

        Refuses to run unless the table is frozen and every required numerical
        tolerance is set, so tolerances cannot be chosen after seeing held-out values.
        ``tolerance_scale`` supports the predeclared sensitivity analysis only.
        """
        if not self.ready_for_evaluation():
            raise RuntimeError(
                f"rule table {self.version} is not ready for evaluation: status={self.status!r}, "
                f"unset required tolerances={self.unset_required_tolerances()}"
            )
        results: dict[str, str] = {}
        for rule in self.rules:
            diff = differences.get(rule.name)
            if rule.comparison == "exact":
                results[rule.name] = _classify_exact(diff)
            else:
                tol = rule.tolerance or {}
                low = tol.get("low", 0.0) * tolerance_scale
                high = tol.get("high", tol.get("low", 0.0)) * tolerance_scale
                results[rule.name] = classify_descriptor(diff, low, high)
        required = {r.name for r in self.rules if r.required}
        return {
            "rule_version": self.version,
            "rule_hash": self.canonical_hash(),
            "tolerance_scale": tolerance_scale,
            "per_descriptor": results,
            "overall": combine(results, required),
        }

    def sensitivity(self, differences: Mapping[str, Optional[Interval]]) -> dict[float, str]:
        """Overall verdict under each predeclared tolerance multiplier. The primary
        result is the multiplier-1.0 entry and is never redefined afterwards."""
        return {m: self.decide(differences, m)["overall"] for m in self.sensitivity_multipliers}
