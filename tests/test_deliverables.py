import pandas as pd

from grantcheck.deliverables import deliverable_status, due_date, month_position

START = "2025-01-01"


def test_due_date_is_the_last_day_of_the_project_month():
    assert due_date(START, 1) == pd.Timestamp("2025-01-31")
    assert due_date(START, 18) == pd.Timestamp("2026-06-30")


def test_month_position():
    assert month_position(START, "2025-03-31") == 3.0
    assert month_position(START, "2026-08-31") == 20.0


def test_statuses_at_the_report_date():
    items = pd.DataFrame([
        {"id": "A", "due_month": 3, "submitted_date": "2025-03-28"},
        {"id": "B", "due_month": 6, "submitted_date": "2025-07-14"},
        {"id": "C", "due_month": 18, "submitted_date": None},
        {"id": "D", "due_month": 24, "submitted_date": None},
    ])
    out = deliverable_status(items, START, "2026-08-31").set_index("id")
    assert out.loc["A", "status"] == "on time"
    assert (out.loc["B", "status"], out.loc["B", "days_late"]) == ("late", 14)
    assert (out.loc["C", "status"], out.loc["C", "days_late"]) == ("overdue", 62)
    assert out.loc["D", "status"] == "upcoming"
