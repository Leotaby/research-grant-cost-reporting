import pytest

from grantcheck.equipment import depreciation_for_period, months_of_use


def test_months_from_availability_to_period_end():
    assert months_of_use("2025-03-01", "2025-01-01", "2026-06-30") == 16


def test_asset_available_before_the_period_counts_from_the_period_start():
    assert months_of_use("2024-06-01", "2025-01-01", "2025-12-31") == 12


def test_asset_available_after_the_period_gives_nothing():
    assert months_of_use("2027-01-01", "2025-01-01", "2026-06-30") == 0


def test_straight_line_depreciation_for_the_period():
    assert depreciation_for_period(48_000, 60, "2025-03-01", "2025-01-01", "2026-06-30") == pytest.approx(12_800)


def test_only_the_share_used_for_the_action():
    assert depreciation_for_period(60_000, 60, "2025-11-01", "2025-01-01", "2026-06-30", 0.7) == pytest.approx(5_600)


def test_never_more_than_the_purchase_price():
    assert depreciation_for_period(1_000, 10, "2020-01-01", "2025-01-01", "2026-12-31") == 1_000
    assert depreciation_for_period(1_000, 10, "2020-01-01", "2025-01-01", "2026-12-31", already_charged=900) == 100
