import pytest

from pariquant.shots import ShotAccounting, from_counts


def test_postselection_does_not_reduce_requested_or_executed():
    acc = from_counts(1000, {"00": 600, "11": 400}, retained_counts={"00": 500, "11": 400})
    assert acc.requested_shots == 1000
    assert acc.returned_samples == 1000
    assert acc.retained_samples == 900
    assert acc.postselection_loss == pytest.approx(0.1)
    assert acc.provider_reported_executed is None and not acc.execution_count_known


def test_executed_never_defaults_to_the_request():
    acc = ShotAccounting(requested_shots=1000)
    assert acc.provider_reported_executed is None
    assert acc.returned_samples is None and acc.postselection_loss is None


def test_repeated_jobs_are_separate_from_shots():
    acc = ShotAccounting(requested_shots=1000, repeated_jobs=5)
    assert acc.total_requested_over_jobs == 5000


def test_validation():
    with pytest.raises(ValueError):
        ShotAccounting(requested_shots=0)
    with pytest.raises(ValueError):
        ShotAccounting(requested_shots=10, returned_samples=5, retained_samples=6)
