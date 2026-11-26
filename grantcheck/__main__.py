"""Run the checks for one reporting period.

    python -m grantcheck --period RP1
    python -m grantcheck --period RP1 --programme STANDARD   # same data under a 7% flat rate
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .config import PROGRAMMES
from .deadlines import cfs_status, closing_dates, report_due, reporting_calendar
from .deliverables import deliverable_status
from .personnel import personnel_costs
from .report import write_outputs
from .rules import check_expenses
from .statement import financial_statement, person_months


def run(data_dir: Path, period_id: str, out_dir: Path, programme_key: str | None = None):
    project = json.loads((data_dir / "project.json").read_text())
    programme = PROGRAMMES[programme_key or project["programme"]]
    period = project["reporting_periods"][period_id]
    staff = pd.read_csv(data_dir / "staff.csv")
    records = pd.read_csv(data_dir / "time_records.csv")
    expenses = pd.read_csv(data_dir / "expenses.csv")

    personnel, wp_days, p_issues = personnel_costs(staff, records, period, programme)
    lines, e_issues = check_expenses(expenses, project, period)
    issues = pd.DataFrame(p_issues + e_issues)
    statement, summary = financial_statement(personnel, lines, project, programme, period)
    wps = person_months(wp_days, project, summary["time_elapsed_pct"])
    # the report is prepared for the day it is due: 60 days after the period ends
    summary["report_date"] = report_due(period["end"], programme).date().isoformat()
    deliv = None
    if (data_dir / "deliverables.csv").exists():
        deliv = deliverable_status(pd.read_csv(data_dir / "deliverables.csv"), project["start"],
                                   summary["report_date"])
    calendar = {"periods": reporting_calendar(project, programme), "closing": closing_dates(project, programme),
                "cfs": cfs_status(summary["requested_contribution_eur"], programme,
                                  summary["months_done"], summary["months_total"])}
    report = write_outputs(out_dir, period_id, period, project, programme, personnel, lines, issues,
                           statement, summary, wps, deliv, calendar)
    return statement, summary, issues, report


def main():
    ap = argparse.ArgumentParser(description="Cost eligibility checks and financial report for one period")
    ap.add_argument("--data", default="data", type=Path)
    ap.add_argument("--period", default="RP1")
    ap.add_argument("--out", default="reports", type=Path)
    ap.add_argument("--programme", choices=sorted(PROGRAMMES), default=None,
                    help="override the programme set in project.json")
    a = ap.parse_args()
    statement, summary, issues, report = run(a.data, a.period, a.out, a.programme)
    pd.set_option("display.width", 140)
    print(statement.to_string(index=False))
    print(f"\nEligible EUR {summary['eligible_eur']:,.2f} of EUR {summary['declared_eur']:,.2f} booked; "
          f"{len(issues)} findings; report written to {report}")


if __name__ == "__main__":
    main()
