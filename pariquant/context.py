"""Provider-reported calibration and characterization context.

This is *execution context*, not a model of the full physical noise channel. Every field
carries its provenance and an evidence status; missing values stay unavailable and are
never imputed. See docs/proposal/PariQuant.md Sec. 4.4 and schemas/context_record.schema.json.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

EVIDENCE_STATUS = ("observed", "derived", "unavailable")
PROVENANCE_KIND = (
    "job-linked",
    "calibration-set-linked",
    "near-run-current",
    "static-provider",
    "researcher-measured",
)
SCOPES = ("device", "qubit", "qubit-pair", "operation")


def payload_hash(raw: bytes | str | dict) -> str:
    """SHA-256 of a raw provider payload (dicts are hashed in canonical JSON form)."""
    if isinstance(raw, dict):
        raw = json.dumps(raw, sort_keys=True, separators=(",", ":"))
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class ContextField:
    name: str
    scope: str
    evidence_status: str
    provenance_kind: Optional[str] = None
    value: Any = None
    unit: Optional[str] = None
    uncertainty: Optional[float] = None
    characterization_method: Optional[str] = None
    derivation: Optional[str] = None  # equation/model + version; only for derived fields
    source_note: Optional[str] = None

    def __post_init__(self) -> None:
        if self.evidence_status not in EVIDENCE_STATUS:
            raise ValueError(f"evidence_status must be one of {EVIDENCE_STATUS}")
        if self.scope not in SCOPES:
            raise ValueError(f"scope must be one of {SCOPES}")
        if self.provenance_kind is not None and self.provenance_kind not in PROVENANCE_KIND:
            raise ValueError(f"provenance_kind must be one of {PROVENANCE_KIND}")
        if self.evidence_status == "unavailable":
            if self.value is not None:
                raise ValueError("an unavailable field must not carry a value (no imputation)")
        else:
            if self.value is None:
                raise ValueError(f"a {self.evidence_status} field needs a value")
            if self.provenance_kind is None:
                raise ValueError(f"a {self.evidence_status} field needs a provenance_kind")
        if self.evidence_status == "derived" and not self.derivation:
            raise ValueError("a derived field must record its derivation")
        if self.evidence_status != "derived" and self.derivation:
            raise ValueError("derivation is only allowed on derived fields")

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass(frozen=True)
class Snapshot:
    retrieval_time: str  # UTC ISO-8601, local clock
    source_api: str
    raw_payload_hash: str
    raw_payload_location: str
    provider_updated_at: Optional[str] = None
    calibration_or_characterization_id: Optional[str] = None


@dataclass(frozen=True)
class ContextRecord:
    provider: str
    backend_id: str
    task_or_job_id: str
    execution_start: Optional[str]
    execution_end: Optional[str]
    snapshots: tuple[Snapshot, ...] = ()
    fields: tuple[ContextField, ...] = field(default_factory=tuple)

    def crosses_characterization_change(self) -> Optional[bool]:
        """For pre/post snapshot pairs: did the characterization id or provider timestamp
        change between the first and last snapshot? ``None`` when it cannot be decided."""
        if len(self.snapshots) < 2:
            return None
        first, last = self.snapshots[0], self.snapshots[-1]
        ids = (first.calibration_or_characterization_id, last.calibration_or_characterization_id)
        times = (first.provider_updated_at, last.provider_updated_at)
        if None in ids and None in times:
            return None
        return ids[0] != ids[1] or times[0] != times[1]

    def to_dict(self) -> dict:
        return {
            "provider": self.provider,
            "backend_id": self.backend_id,
            "task_or_job_id": self.task_or_job_id,
            "execution_start": self.execution_start,
            "execution_end": self.execution_end,
            "snapshots": [{k: v for k, v in asdict(s).items() if v is not None} for s in self.snapshots],
            "fields": [f.to_dict() for f in self.fields],
        }
