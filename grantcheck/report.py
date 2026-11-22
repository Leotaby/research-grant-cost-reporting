"""Write the outputs of a reporting period: CSV tables, figures and a Markdown report."""
from pathlib import Path

import pandas as pd

from . import charts


def _money(v):
    return f"{v:,.2f}"


def _md_table(df: pd.DataFrame, money_cols=(), pct_cols=()) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---:" if c in money_cols or c in pct_cols
                                                          else "---" for c in cols) + " |"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if c in money_cols:
                cells.append(_money(v))
            elif c in pct_cols:
                cells.append("" if pd.isna(v) else f"{v:.1f}%")
            else:
                cells.append(str(v).replace("|", "/"))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def write_outputs(out_dir: Path, period_id: str, period: dict, project: dict, programme,
                  personnel, lines, issues, statement, summary, wps):
    out_dir = Path(out_dir)
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    personnel.to_csv(out_dir / f"{period_id}_personnel.csv", index=False)
    lines.to_csv(out_dir / f"{period_id}_expenses_checked.csv", index=False)
    issues.to_csv(out_dir / f"{period_id}_issues_log.csv", index=False)
    statement.to_csv(out_dir / f"{period_id}_financial_statement.csv", index=False)
    wps.to_csv(out_dir / f"{period_id}_work_packages.csv", index=False)

    figs = {
        "fig1_declared_vs_eligible.png": lambda p: charts.fig_declared_vs_eligible(statement, p, period_id),
        "fig2_budget_use.png": lambda p: charts.fig_budget_use(statement, summary, p, period_id),
        "fig3_days_against_cap.png": lambda p: charts.fig_days_cap(personnel, p, int(period["start"][:4]),
                                                                   programme.day_cap),
        "fig4_findings_by_check.png": lambda p: charts.fig_issues(issues, p, period_id),
    }
    for name, draw in figs.items():
        draw(fig_dir / name)

    # ---- Markdown report --------------------------------------------------------------------------
    s = summary
    ahead = statement[(statement["category"] != "Total") & statement["budget_used_pct"].notna()
                      & (statement["budget_used_pct"] > s["time_elapsed_pct"] + 15)]
    behind = wps[wps["eligible_pm"] < 0.8 * wps["expected_pm_to_date"]]
    fast = wps[wps["eligible_pm"] > 1.25 * wps["expected_pm_to_date"]]
    inel = issues[issues["severity"] == "ineligible"]
    risk = issues[issues["severity"] == "at risk"]

    notes = []
    for _, r in ahead.iterrows():
        notes.append(f"**{r['category']}** has used {r['budget_used_pct']:.0f}% of its budget at "
                     f"{s['time_elapsed_pct']:.1f}% of the action: plan the remaining spending or a "
                     "transfer between categories.")
    for _, r in fast.iterrows():
        notes.append(f"**{r['wp']} {r['name']}** has used {r['eligible_pm']:.1f} person-months against "
                     f"about {r['expected_pm_to_date']:.1f} expected by now ({r['planned_used_pct']:.0f}% of "
                     "its plan): check that the remaining work fits the remaining effort.")
    for _, r in behind.iterrows():
        notes.append(f"**{r['wp']} {r['name']}** has {r['eligible_pm']:.1f} eligible person-months "
                     f"against about {r['expected_pm_to_date']:.1f} expected by now: check whether time is "
                     "being worked but not recorded.")
    if s["cfs_threshold_eur"]:
        thr, req = s["cfs_threshold_eur"], s["requested_contribution_eur"]
        if req >= thr:
            notes.append(f"This period alone requests EUR {req:,.0f}, above the EUR {thr:,.0f} threshold: a "
                         "certificate on the financial statements (CFS) covering all periods will be needed "
                         "with the final report. Budget the audit fee now.")
        else:
            notes.append(f"A certificate on the financial statements (CFS) is needed with the final report "
                         f"if the requested EU contribution reaches EUR {thr:,.0f}; this period requests "
                         f"EUR {req:,.0f} ({100 * req / thr:.0f}% of it).")
    people = sorted({i.split()[0] for i in inel.loc[inel["category"] == "A", "line"]})
    if people:
        notes.append(f"Personnel findings concern {len(people)} people ({', '.join(people)}): fix the time "
                     "records and the cap before the report is submitted.")

    fig_md = "\n\n".join(f"![{n}](figures/{n})" for n in figs)
    st_md = statement.rename(columns={"category": "Category", "budget_eur": "Budget (action)",
                                      "declared_eur": "Booked", "eligible_eur": "Eligible",
                                      "ineligible_eur": "Ineligible", "at_risk_eur": "At risk",
                                      "budget_used_pct": "Budget used"})
    iss = issues.sort_values(["severity", "amount_eur"], ascending=[False, False])
    iss_md = iss[["rule", "line", "severity", "amount_eur", "detail", "action"]].rename(
        columns={"rule": "Check", "line": "Line", "severity": "Status", "amount_eur": "EUR",
                 "detail": "Finding", "action": "Action"})
    wp_md = wps.rename(columns={"wp": "WP", "name": "Work package", "planned_pm": "Planned PM (action)",
                                "expected_pm_to_date": "Expected PM to date", "eligible_pm": "Eligible PM",
                                "planned_used_pct": "Planned PM used"})

    md = f"""# {project['project']}: financial report, {period_id} ({period['start']} to {period['end']})

*Fictional project and data, produced by `python -m grantcheck --period {period_id}`.
Programme rules: {programme.name}, indirect costs {programme.indirect_rate:.0%} flat rate,
funding rate {project['funding_rate']:.0%}.*

## Key figures

| | EUR |
| --- | ---: |
| Booked to the project by the department | {_money(s['declared_eur'])} |
| Eligible after the checks | {_money(s['eligible_eur'])} |
| Ineligible (cut, including the indirect costs on them) | {_money(s['ineligible_eur'])} |
| At risk: eligible only if a decision or document comes through | {_money(s['at_risk_eur'])} |
| Indirect costs included in the eligible total | {_money(s['indirect_eur'])} |
| EU contribution requested for the period | {_money(s['requested_contribution_eur'])} |

Month {s['months_done']} of {s['months_total']} ({s['time_elapsed_pct']:.1f}% of the action);
{100 * s['eligible_eur'] / s['budget_eur']:.1f}% of the total budget used.
{len(inel)} findings make costs ineligible and {len(risk)} need a decision.

## Points for the coordinator

""" + "\n".join(f"- {n}" for n in notes) + f"""

## Financial statement by cost category

{_md_table(st_md, money_cols=("Budget (action)", "Booked", "Eligible", "Ineligible", "At risk"), pct_cols=("Budget used",))}

## Findings and actions

{_md_table(iss_md, money_cols=("EUR",))}

## Person-months by work package

{_md_table(wp_md, pct_cols=("Planned PM used",))}

One person-month = 215 / 12 = 17.9 day-equivalents.

## Figures

{fig_md}
"""
    (out_dir / f"{period_id}_report.md").write_text(md)
    return out_dir / f"{period_id}_report.md"
