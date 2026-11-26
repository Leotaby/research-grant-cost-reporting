"""Personnel costs declared as actual costs (AGA Art. 6.2.A.1).

    cost       = daily rate x day-equivalents worked on the action
    daily rate = actual personnel costs during the months within the reporting period
                 / maximum declarable day-equivalents
    maximum declarable day-equivalents
               = 215 / 12 x months within the reporting period x working-time factor

Day-equivalents are rounded to the nearest half-day. The rate is worked out per person, here
separately for each calendar year within the reporting period, which the AGA allows if it is done
consistently. For a full year of full-time work it comes to annual personnel costs / 215.

Two ceilings apply. A person cannot declare more than the maximum for the months concerned, because
no more than 100% of the personnel costs can be charged; and no more than 215 day-equivalents a year
across all EU grants. Time worked needs monthly declarations signed by the person and the
supervisor, or a reliable time-recording system (MGA Art. 20).
"""
import pandas as pd

from .config import RULES


def round_half_day(days: float) -> float:
    """Nearest half-day (a quarter-day rounds up)."""
    return int(days * 2 + 0.5) / 2


def max_declarable_days(months: float, working_time: float = 1.0, days_per_year: int = 215) -> float:
    """Most day-equivalents a person can declare for `months` months within the reporting period."""
    return round_half_day(days_per_year / 12 * months * working_time)


def daily_rate(personnel_costs: float, months: float = 12, working_time: float = 1.0,
               days_per_year: int = 215) -> float:
    """Personnel costs of the months within the reporting period over the maximum declarable days."""
    return personnel_costs / max_declarable_days(months, working_time, days_per_year)


def _issue(line, rule, amount, detail):
    title, ref, action = RULES[rule]
    return {"line": line, "category": "A", "rule": rule, "title": title, "reference": ref,
            "severity": "ineligible", "amount_eur": round(amount, 2), "detail": detail, "action": action}


def personnel_costs(staff: pd.DataFrame, records: pd.DataFrame, period: dict, programme):
    """Cost the time records of a reporting period.

    `staff` gives, for each calendar year, the personnel costs of the months within the reporting
    period (`cost_<year>`) and the number of those months the person was employed (`months_<year>`).
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
        months = float(st.loc[sid, f"months_{year}"])
        maximum = max_declarable_days(months, days_per_year=programme.day_cap)
        rate = float(st.loc[sid, f"cost_{year}"]) / maximum
        recorded = round_half_day(g["days"].sum())
        unsupported = round_half_day(g.loc[~g["supported"], "days"].sum())
        supported = recorded - unsupported
        other = float(st.loc[sid, f"other_eu_grant_days_{year}"])
        room = max(min(maximum, programme.day_cap - other), 0.0)
        above_cap = max(supported - room, 0.0)
        eligible = supported - above_cap

        if unsupported:
            which = ", ".join(sorted({str(m) for m in g.loc[~g["supported"], "month"]}))
            kind = g["record_type"].iloc[0]
            issues.append(_issue(f"{sid} {year}", "R03", unsupported * rate,
                                 f"{sid}: {unsupported:g} days in {which} without a {kind} signed by "
                                 "the person and the supervisor"))
        if above_cap:
            others = f" + {other:g} on other EU grants" if other else ""
            issues.append(_issue(f"{sid} {year}", "R02", above_cap * rate,
                                 f"{sid}: {supported:g} days on this action{others} in {year}; at most "
                                 f"{room:g} can be declared here"))

        rows.append({"staff_id": sid, "role": st.loc[sid, "role"], "year": int(year),
                     "months_in_period": months, "max_declarable_days": maximum,
                     "daily_rate_eur": round(rate, 2), "days_recorded": recorded,
                     "days_unsupported": unsupported, "days_other_eu_grants": other,
                     "days_above_cap": above_cap, "days_eligible": eligible,
                     "declared_eur": round(recorded * rate, 2), "eligible_eur": round(eligible * rate, 2),
                     "ineligible_eur": round((recorded - eligible) * rate, 2)})

        # eligible days per work package: supported days, scaled down if a ceiling bites
        sup = g[g["supported"]].groupby("wp")["days"].sum()
        scale = eligible / supported if supported else 0.0
        for wp, d in sup.items():
            wp_days.append({"staff_id": sid, "year": int(year), "wp": wp, "days_eligible": d * scale})

    return pd.DataFrame(rows), pd.DataFrame(wp_days), issues
