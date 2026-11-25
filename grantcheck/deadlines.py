"""Reporting calendar and audit certificate.

Time limits of the EU grant agreement (standard values; the Data Sheet of each grant sets them):

- the periodic report is due within 60 days after the end of each reporting period (MGA Art. 21);
- the granting authority pays within 90 days of receiving the report (MGA Art. 22);
- the final report comes with the last periodic report, within 60 days after the end of the action;
- a certificate on the financial statements (CFS) comes with the final report if the EU
  contribution the beneficiary requests for actual costs over the whole action reaches the
  threshold; flat-rate costs, such as indirect costs, do not count (MGA Art. 24);
- records are kept for 5 years after the payment of the balance (MGA Art. 20), and the granting
  authority can start an audit up to 2 years after it (MGA Art. 25).
"""
import pandas as pd


def report_due(period_end: str, programme) -> pd.Timestamp:
    """Last day for submitting the report of a period."""
    return pd.Timestamp(period_end) + pd.Timedelta(days=programme.report_days)


def reporting_calendar(project: dict, programme) -> pd.DataFrame:
    """One row per reporting period: when the report is due and when the payment should arrive.

    The payment date assumes the report is submitted on its due date and accepted without a
    request for corrections, which stops the clock.
    """
    periods = project["reporting_periods"]
    last = list(periods)[-1]
    rows = []
    for pid, p in periods.items():
        due = report_due(p["end"], programme)
        rows.append({
            "period": pid, "from": p["start"], "to": p["end"],
            "report": "Periodic and final report" if pid == last else "Periodic report",
            "report_due": due.date().isoformat(),
            "payment": "Payment of the balance" if pid == last else "Interim payment",
            "payment_by": (due + pd.Timedelta(days=programme.payment_days)).date().isoformat(),
        })
    return pd.DataFrame(rows)


def closing_dates(project: dict, programme) -> dict:
    """Dates that follow the payment of the balance, if every step takes its full time limit."""
    last = list(project["reporting_periods"].values())[-1]
    balance = report_due(last["end"], programme) + pd.Timedelta(days=programme.payment_days)
    return {
        "balance_by": balance.date().isoformat(),
        "audits_can_start_until": (balance + pd.DateOffset(years=programme.audit_years)).date().isoformat(),
        "keep_records_until": (balance + pd.DateOffset(years=programme.record_years)).date().isoformat(),
    }


def cfs_status(requested_for_actual_costs_eur: float, programme, months_done: int, months_total: int):
    """Where the beneficiary stands against the CFS threshold, and where it is heading.

    The projection keeps the pace of the periods reported so far; it is a planning figure.
    """
    threshold = programme.cfs_threshold_eur
    if not threshold:
        return None
    projected = requested_for_actual_costs_eur / months_done * months_total
    return {
        "threshold_eur": threshold,
        "requested_so_far_eur": round(requested_for_actual_costs_eur, 2),
        "share_of_threshold_pct": round(100 * requested_for_actual_costs_eur / threshold, 1),
        "projected_eur": round(projected, 2),
        "reached": requested_for_actual_costs_eur >= threshold,
        "expected": projected >= threshold,
    }
