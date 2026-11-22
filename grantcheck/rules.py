"""Checks on purchase costs, subcontracting and other direct costs, line by line.

Each line ends up with an eligible amount, an ineligible amount and, for problems that need a
human decision (for example a subcontract that still needs approval), an amount at risk. Lines
dated inside the action but outside the reporting period are left for the report they belong to.
"""
import math

import pandas as pd

from .config import RULES
from .equipment import depreciation_for_period

STATEMENT_CATEGORY = {"bank_charges": "C3", "interest": "C3"}   # where the ledger had booked them


def _missing(v) -> bool:
    return v is None or (isinstance(v, float) and math.isnan(v)) or (isinstance(v, str) and not v.strip())


def _flag(v) -> bool:
    return str(v).strip().lower() in ("true", "1", "yes")


def _belongs(date, action, period) -> bool:
    if date < action[0]:
        return period[0] == action[0]          # pre-start costs surface in the first report
    if date > action[1]:
        return period[1] == action[1]          # post-end costs surface in the last report
    return period[0] <= date <= period[1]


def check_expenses(expenses: pd.DataFrame, project: dict, period: dict):
    """Return the checked lines and the list of issues for one reporting period."""
    action = (pd.Timestamp(project["start"]), pd.Timestamp(project["end"]))
    per = (pd.Timestamp(period["start"]), pd.Timestamp(period["end"]))
    annex1 = set(project.get("subcontracts_in_annex1", []))
    flight_class = project.get("travel_policy", {}).get("flight_class", "economy")
    award_limit = float(project.get("direct_award_limit_eur", 140_000))

    lines, issues = [], []
    for r in expenses.to_dict("records"):
        date = pd.Timestamp(r["date"])
        if not _belongs(date, action, per):
            continue
        cat = r["category"]
        declared = float(r["declared_eur"])
        eligible, at_risk, flags = declared, 0.0, []

        def issue(rule, amount, detail, severity="ineligible"):
            title, ref, action_text = RULES[rule]
            issues.append({"line": r["expense_id"], "category": STATEMENT_CATEGORY.get(cat, cat),
                           "rule": rule, "title": title, "reference": ref, "severity": severity,
                           "amount_eur": round(amount, 2), "detail": detail, "action": action_text})
            flags.append(rule)

        # costs that are ineligible as a whole
        if not action[0] <= date <= action[1]:
            issue("R01", declared, f"{r['description']}, dated {date.date()}; the action runs "
                                   f"{action[0].date()} to {action[1].date()}")
            eligible = 0.0
        elif cat == "bank_charges":
            issue("R08", declared, r["description"])
            eligible = 0.0
        elif cat == "interest":
            issue("R09", declared, r["description"])
            eligible = 0.0
        elif _missing(r["invoice_ref"]):
            issue("R05", declared, f"{r['description']} ({r['supplier']}), no invoice reference")
            eligible = 0.0
        elif not _missing(r["other_eu_grant"]):
            issue("R07", declared, f"{r['description']}: also charged to {r['other_eu_grant']}")
            eligible = 0.0

        if eligible > 0:
            # equipment: depreciation for the period only
            if cat == "C2":
                dep = depreciation_for_period(float(r["purchase_price_eur"]), int(r["useful_life_months"]),
                                              r["available_from"], period["start"], period["end"],
                                              float(r["use_share"]))
                if declared > dep + 0.005:
                    issue("R04", declared - dep,
                          f"{r['description']}: declared EUR {declared:,.2f}, depreciation for the period "
                          f"EUR {dep:,.2f} (price EUR {float(r['purchase_price_eur']):,.0f}, "
                          f"{int(r['useful_life_months'])} months' life, {float(r['use_share']):.0%} use)")
                    eligible = dep
            # VAT that the beneficiary can recover
            vat = 0.0 if _missing(r["vat_eur"]) else float(r["vat_eur"])
            if vat > 0 and _flag(r["vat_recoverable"]):
                issue("R06", vat, f"{r['description']}: EUR {vat:,.2f} of recoverable VAT")
                eligible -= vat
            # problems that need a decision rather than an automatic cut
            if cat == "C1" and str(r["flight_class"]) not in ("nan", flight_class):
                fare = None if _missing(r["economy_fare_eur"]) else float(r["economy_fare_eur"])
                risk = eligible - fare if fare is not None else eligible
                issue("W01", risk, f"{r['description']}: {r['flight_class']} class; economy fare about "
                                   f"EUR {fare:,.0f}" if fare else r["description"], "at risk")
                at_risk += risk
            if cat == "B" and r["subcontract_id"] not in annex1:
                issue("W02", eligible, f"{r['subcontract_id']}: {r['description']}", "at risk")
                at_risk += eligible
            value = float(r["purchase_price_eur"]) if cat == "C2" else float(r["net_eur"])
            if str(r["procurement"]).strip().lower() == "direct award" and value >= award_limit:
                issue("W03", eligible, f"{r['description']}: EUR {value:,.0f} awarded directly", "at risk")
                at_risk += eligible

        at_risk = min(at_risk, eligible)
        lines.append({"expense_id": r["expense_id"], "date": date.date().isoformat(),
                      "category": STATEMENT_CATEGORY.get(cat, cat), "description": r["description"],
                      "wp": r["wp"], "declared_eur": round(declared, 2), "eligible_eur": round(eligible, 2),
                      "ineligible_eur": round(declared - eligible, 2), "at_risk_eur": round(at_risk, 2),
                      "checks": ",".join(flags)})
    return pd.DataFrame(lines), issues
