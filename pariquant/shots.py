"""Shot accounting.

The study treats the *requested* shot count as a resource-setting variable chosen by the
experimenter, not as an intrinsic property of a QPU or an unexplained provider default.
Four quantities are recorded separately; ``None`` means "not observable" and is never
silently replaced by the request.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping, Optional


@dataclass(frozen=True)
class ShotAccounting:
    requested_shots: int  # sampling budget submitted for this circuit / execution unit
    provider_reported_executed: Optional[int] = None  # only where the provider exposes it
    returned_samples: Optional[int] = None  # samples present in the returned data
    retained_samples: Optional[int] = None  # after any filtering / postselection
    repeated_jobs: int = 1  # whole-job repetitions (run-to-run / drift), distinct from shots

    def __post_init__(self) -> None:
        if self.requested_shots <= 0:
            raise ValueError("requested_shots must be positive")
        if self.repeated_jobs <= 0:
            raise ValueError("repeated_jobs must be positive")
        for name in ("provider_reported_executed", "returned_samples", "retained_samples"):
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError(f"{name} must be non-negative or None")
        if (
            self.returned_samples is not None
            and self.retained_samples is not None
            and self.retained_samples > self.returned_samples
        ):
            raise ValueError("retained_samples cannot exceed returned_samples")

    @property
    def postselection_loss(self) -> Optional[float]:
        """Fraction of returned samples discarded by postprocessing, if both are known."""
        if self.returned_samples in (None, 0) or self.retained_samples is None:
            return None
        return 1.0 - self.retained_samples / self.returned_samples

    @property
    def execution_count_known(self) -> bool:
        """True only when the provider reports executed repetitions explicitly."""
        return self.provider_reported_executed is not None

    @property
    def total_requested_over_jobs(self) -> int:
        return self.requested_shots * self.repeated_jobs

    def to_dict(self) -> dict:
        return asdict(self)


def from_counts(
    requested_shots: int,
    counts: Mapping[str, int],
    retained_counts: Optional[Mapping[str, int]] = None,
    provider_reported_executed: Optional[int] = None,
    repeated_jobs: int = 1,
) -> ShotAccounting:
    """Build a record from raw counts.

    For simple unfiltered count data, the sum of the returned counts documents the
    returned sample count. It does not expose physical work the service may have done
    (retries, expanded circuits, mitigation overhead), which stays ``None``.
    """
    returned = sum(counts.values())
    retained = returned if retained_counts is None else sum(retained_counts.values())
    return ShotAccounting(
        requested_shots=requested_shots,
        provider_reported_executed=provider_reported_executed,
        returned_samples=returned,
        retained_samples=retained,
        repeated_jobs=repeated_jobs,
    )
