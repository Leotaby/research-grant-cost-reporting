"""Deliverables and milestones from Annex 1: due dates and status at the report date.

A deliverable due in project month m is due on the last day of that month (month 1 is the month the
action starts). At the report date each item is on time, late (submitted after its due date),
overdue (due and not yet submitted) or upcoming.
"""
import pandas as pd


def due_date(project_start: str, month: int) -> pd.Timestamp:
    """Last day of project month `month`."""
    return pd.Timestamp(project_start) + pd.DateOffset(months=int(month)) - pd.Timedelta(days=1)


def month_position(project_start: str, date) -> float:
    """Date as a position on the project-month axis (the end of month m is m.0)."""
    s, d = pd.Timestamp(project_start), pd.Timestamp(date)
    return (d.year - s.year) * 12 + (d.month - s.month) + d.day / d.days_in_month


def deliverable_status(items: pd.DataFrame, project_start: str, as_of: str) -> pd.DataFrame:
    as_of = pd.Timestamp(as_of)
    out = items.copy()
    due = pd.Series([due_date(project_start, m) for m in out["due_month"]], index=out.index)
    sub = pd.to_datetime(out["submitted_date"], errors="coerce")
    status, days_late = [], []
    for s, d in zip(sub, due):
        if pd.isna(s):
            status.append("overdue" if d < as_of else "upcoming")
            days_late.append((as_of - d).days if d < as_of else 0)
        else:
            late = (s - d).days
            status.append("late" if late > 0 else "on time")
            days_late.append(max(late, 0))
    out["due_date"] = due.dt.date.astype(str)
    out["status"] = status
    out["days_late"] = days_late
    return out
