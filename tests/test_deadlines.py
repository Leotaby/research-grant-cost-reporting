import pytest

from grantcheck.config import PROGRAMMES
from grantcheck.deadlines import cfs_status, closing_dates, report_due, reporting_calendar

HE = PROGRAMMES["HORIZON"]
PROJECT = {"reporting_periods": {
    "RP1": {"start": "2025-01-01", "end": "2026-06-30"},
    "RP2": {"start": "2026-07-01", "end": "2027-12-31"},
    "RP3": {"start": "2028-01-01", "end": "2028-12-31"},
}}


def test_report_is_due_60_days_after_the_period_ends():
    assert report_due("2026-06-30", HE).date().isoformat() == "2026-08-29"
    assert report_due("2027-12-31", HE).date().isoformat() == "2028-02-29"      # leap year


def test_calendar_has_one_row_per_period_and_a_final_report():
    cal = reporting_calendar(PROJECT, HE).set_index("period")
    assert list(cal.index) == ["RP1", "RP2", "RP3"]
    assert cal.loc["RP1", "report_due"] == "2026-08-29"
    assert cal.loc["RP1", "payment_by"] == "2026-11-27"                         # 90 days later
    assert cal.loc["RP3", "report"] == "Periodic and final report"
    assert cal.loc["RP3", "payment"] == "Payment of the balance"


def test_records_and_audits_run_from_the_balance_payment():
    c = closing_dates(PROJECT, HE)
    assert c["balance_by"] == "2029-05-30"
    assert c["audits_can_start_until"] == "2031-05-30"
    assert c["keep_records_until"] == "2034-05-30"


def test_cfs_threshold_and_projection():
    s = cfs_status(315_261.75, HE, months_done=18, months_total=48)
    assert not s["reached"] and s["expected"]
    assert s["share_of_threshold_pct"] == pytest.approx(73.3)
    assert s["projected_eur"] == pytest.approx(840_698.0)
    assert cfs_status(100_000, HE, 18, 48)["expected"] is False
    assert cfs_status(100_000, PROGRAMMES["STANDARD"], 18, 48) is None          # threshold set per call
