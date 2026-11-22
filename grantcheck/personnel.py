"""Personnel costs declared as actual costs (AGA Art. 6.2.A).

    cost       = daily rate x day-equivalents worked on the action
    daily rate = annual personnel costs for the person / 215

Day-equivalents are rounded to the nearest half-day. A person cannot declare more than 215
day-equivalents a year across all EU grants. If a financial year is not yet closed when the report
is prepared, the daily rate of the last closed financial year is used. Every month of work needs a
signed time record (a timesheet, or a monthly day-declaration for people working only on the action).
"""
import pandas as pd

from .config import RULES


def daily_rate(annual_personnel_costs: float, days_per_year: int = 215) -> float:
    return annual_personnel_costs / days_per_year


def round_half_day(days: float) -> float:
    """Nearest half-day (a quarter-day rounds up)."""
    return int(days * 2 + 0.5) / 2


def rate_year(year: int, closed_years) -> int:
    """Year whose costs set the daily rate: the year itself if closed, otherwise the last closed one."""
    if year in closed_years:
        return year
    earlier = [y for y in closed_years if y < year]
    if not earlier:
        raise ValueError(f"no closed financial year available to cost {year}")
    return max(earlier)


def _issue(line, rule, amount, detail):
    title, ref, action = RULES[rule]
    return {"line": line, "category": "A", "rule": rule, "title": title, "reference": ref,
            "severity": "ineligible", "amount_eur": round(amount, 2), "detail": detail, "action": action}


def personnel_costs(staff: pd.DataFrame, records: pd.DataFrame, period: dict, programme):
    """Cost the time records of a reporting period.

    Returns a table per person and year, eligible day-equivalents per work package, and the issues.
    """
    start, end = pd.Period(period["start"][:7], "M"), pd.Period(period["end"][:7], "M")
    rec = records.copy()
    rec["month"] = pd.PeriodIndex(rec["month"], freq="M")
    rec = rec[(rec["month"] >= start) & (rec["month"] <= end)].copy()
    rec["year"] = rec["month"].dt.year
    rec["supported"] = rec["signed_by_person"].astype(bool) & rec["signed_by_supervisor"].astype(bool)
    st = staff.set_index("staff_id")

    rows, wp_days, issues = [], [], []
    for (sid, year), g in rec.groupby(["staff_id", "year"]):
        ry = rate_year(int(year), period["closed_financial_years"])
        rate = daily_rate(float(st.loc[sid, f"annual_cost_{ry}"]), programme.day_cap)
        recorded = round_half_day(g["days"].sum())
        unsupported = round_half_day(g.loc[~g["supported"], "days"].sum())
        supported = recorded - unsupported
        other = float(st.loc[sid, f"other_eu_grant_days_{year}"])
        room = max(programme.day_cap - other, 0.0)
        above_cap = max(supported - room, 0.0)
        eligible = supported - above_cap

        if unsupported:
            months = ", ".join(sorted({str(m) for m in g.loc[~g["supported"], "month"]}))
            kind = g["record_type"].iloc[0]
            issues.append(_issue(f"{sid} {year}", "R03", unsupported * rate,
                                 f"{sid}: {unsupported:g} days in {months} without a {kind} signed by "
                                 "the person and the supervisor"))
        if above_cap:
            others = f" + {other:g} on other EU grants" if other else ""
            issues.append(_issue(f"{sid} {year}", "R02", above_cap * rate,
                                 f"{sid}: {supported:g} days on this action{others} in {year}; at most "
                                 f"{room:g} can be declared here"))

        rows.append({"staff_id": sid, "role": st.loc[sid, "role"], "year": int(year), "rate_year": ry,
                     "daily_rate_eur": round(rate, 2), "days_recorded": recorded,
                     "days_unsupported": unsupported, "days_other_eu_grants": other,
                     "days_above_cap": above_cap, "days_eligible": eligible,
                     "declared_eur": round(recorded * rate, 2), "eligible_eur": round(eligible * rate, 2),
                     "ineligible_eur": round((recorded - eligible) * rate, 2)})

        # eligible days per work package: supported days, scaled down if the cap bites
        sup = g[g["supported"]].groupby("wp")["days"].sum()
        scale = eligible / supported if supported else 0.0
        for wp, d in sup.items():
            wp_days.append({"staff_id": sid, "year": int(year), "wp": wp, "days_eligible": d * scale})

    return pd.DataFrame(rows), pd.DataFrame(wp_days), issues
