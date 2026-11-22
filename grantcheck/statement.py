"""Financial statement for a reporting period, budget use and person-months per work package."""
import pandas as pd

from .config import CATEGORIES, CATEGORY_NAMES

DAYS_PER_PERSON_MONTH = 215 / 12


def indirect_costs(direct: dict, programme) -> float:
    """Flat-rate indirect costs on the direct costs that form the base (AGA Art. 6.2.E)."""
    base = sum(v for k, v in direct.items() if k not in programme.indirect_base_excludes)
    return round(base * programme.indirect_rate, 2)


def financial_statement(personnel: pd.DataFrame, lines: pd.DataFrame, project: dict, programme,
                        period: dict) -> tuple[pd.DataFrame, dict]:
    sums = {c: {"declared_eur": 0.0, "eligible_eur": 0.0, "ineligible_eur": 0.0, "at_risk_eur": 0.0}
            for c in CATEGORIES}
    for col in ("declared_eur", "eligible_eur", "ineligible_eur"):
        sums["A"][col] = float(personnel[col].sum())
    for cat, g in lines.groupby("category"):
        for col in ("declared_eur", "eligible_eur", "ineligible_eur", "at_risk_eur"):
            sums[cat][col] += float(g[col].sum())

    budget = dict(project["budget_eur"])
    budget["E"] = indirect_costs({c: budget.get(c, 0) for c in CATEGORIES}, programme)
    e_declared = indirect_costs({c: sums[c]["declared_eur"] for c in CATEGORIES}, programme)
    e_eligible = indirect_costs({c: sums[c]["eligible_eur"] for c in CATEGORIES}, programme)
    # indirect costs that fall away if the amounts at risk are rejected
    e_risk = e_eligible - indirect_costs({c: sums[c]["eligible_eur"] - sums[c]["at_risk_eur"]
                                          for c in CATEGORIES}, programme)
    sums["E"] = {"declared_eur": e_declared, "eligible_eur": e_eligible,
                 "ineligible_eur": e_declared - e_eligible, "at_risk_eur": e_risk}

    rows = []
    for c in CATEGORIES + ["E"]:
        s = sums[c]
        b = float(budget.get(c, 0))
        rows.append({"category": CATEGORY_NAMES[c], "budget_eur": b,
                     **{k: round(v, 2) for k, v in s.items()},
                     "budget_used_pct": round(100 * s["eligible_eur"] / b, 1) if b else None})
    st = pd.DataFrame(rows)
    total = {k: round(float(st[k].sum()), 2) for k in ("budget_eur", "declared_eur", "eligible_eur",
                                                     "ineligible_eur", "at_risk_eur")}
    st = pd.concat([st, pd.DataFrame([{"category": "Total", **total,
                                       "budget_used_pct": round(100 * total["eligible_eur"] / total["budget_eur"], 1)}])],
                   ignore_index=True)

    start, end = pd.Timestamp(project["start"]), pd.Timestamp(project["end"])
    p_end = pd.Timestamp(period["end"])
    months_total = (end.year - start.year) * 12 + end.month - start.month + 1
    months_done = (p_end.year - start.year) * 12 + p_end.month - start.month + 1
    contribution = round(total["eligible_eur"] * project["funding_rate"], 2)
    summary = {
        "declared_eur": total["declared_eur"], "eligible_eur": total["eligible_eur"],
        "ineligible_eur": total["ineligible_eur"], "at_risk_eur": total["at_risk_eur"],
        "indirect_eur": e_eligible, "requested_contribution_eur": contribution,
        "budget_eur": total["budget_eur"], "time_elapsed_pct": round(100 * months_done / months_total, 1),
        "months_done": months_done, "months_total": months_total,
        "cfs_threshold_eur": programme.cfs_threshold_eur,
    }
    return st, summary


def person_months(wp_days: pd.DataFrame, project: dict, time_elapsed_pct: float) -> pd.DataFrame:
    done = wp_days.groupby("wp")["days_eligible"].sum() / DAYS_PER_PERSON_MONTH
    rows = []
    for wp, info in project["work_packages"].items():
        planned = info["planned_person_months"]
        pm = float(done.get(wp, 0.0))
        rows.append({"wp": wp, "name": info["name"], "planned_pm": planned,
                     "expected_pm_to_date": round(planned * time_elapsed_pct / 100, 1),
                     "eligible_pm": round(pm, 1), "planned_used_pct": round(100 * pm / planned, 1)})
    return pd.DataFrame(rows)
