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


def _calendar_md(calendar: dict, programme) -> str:
    cal = calendar["periods"].rename(columns={"period": "Period", "from": "From", "to": "To", "report": "Report",
                                              "report_due": "Report due", "payment": "Payment",
                                              "payment_by": "Payment by"})
    c = calendar["closing"]
    cfs = calendar["cfs"]
    if cfs:
        cfs_line = (f"- Certificate on the financial statements (CFS): due with the final report if the EU "
                    f"contribution requested reaches EUR {cfs['threshold_eur']:,.0f} over the whole action "
                    f"(the flat rate for indirect costs counts too). So far: "
                    f"EUR {cfs['requested_so_far_eur']:,.2f} ({cfs['share_of_threshold_pct']:.1f}%); at this pace: "
                    f"about EUR {cfs['projected_eur']:,.0f}.")
    else:
        cfs_line = ("- Certificate on the financial statements (CFS): the threshold is set in the Data Sheet "
                    "of the grant agreement.")
    return f"""
## Reporting calendar and audit certificate

Each report is due {programme.report_days} days after its period ends; payment follows within
{programme.payment_days} days if the report is sent on the due date and accepted as it stands.

{_md_table(cal)}

{cfs_line}
- Audits by the granting authority can start until {c['audits_can_start_until']}
  ({programme.audit_years} years after the balance, if it is paid by {c['balance_by']}).
- Keep every supporting document until {c['keep_records_until']} ({programme.record_years} years after the balance).
"""


def write_outputs(out_dir: Path, period_id: str, period: dict, project: dict, programme,
                  personnel, lines, issues, statement, summary, wps, deliverables=None, calendar=None):
    out_dir = Path(out_dir)
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    personnel.to_csv(out_dir / f"{period_id}_personnel.csv", index=False)
    lines.to_csv(out_dir / f"{period_id}_expenses_checked.csv", index=False)
    issues.to_csv(out_dir / f"{period_id}_issues_log.csv", index=False)
    statement.to_csv(out_dir / f"{period_id}_financial_statement.csv", index=False)
    wps.to_csv(out_dir / f"{period_id}_work_packages.csv", index=False)
    if deliverables is not None:
        deliverables.to_csv(out_dir / f"{period_id}_deliverables.csv", index=False)
    if calendar is not None:
        calendar["periods"].to_csv(out_dir / f"{period_id}_reporting_calendar.csv", index=False)

    figs = {
        "fig1_declared_vs_eligible.png": lambda p: charts.fig_declared_vs_eligible(statement, p, period_id),
        "fig2_budget_use.png": lambda p: charts.fig_budget_use(statement, summary, p, period_id),
        "fig3_days_against_cap.png": lambda p: charts.fig_days_cap(personnel, p, int(period["start"][:4]),
                                                                   programme.day_cap),
        "fig4_findings_by_check.png": lambda p: charts.fig_issues(issues, p, period_id),
    }
    if deliverables is not None:
        as_of = summary.get("report_date", period["end"])
        figs["fig5_deliverables.png"] = lambda p: charts.fig_deliverables(deliverables, p, project["start"],
                                                                          as_of, period_id)
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
    cfs = calendar["cfs"] if calendar else None
    if cfs:
        so_far = (f"EUR {cfs['requested_so_far_eur']:,.0f} of EU contribution requested so far, "
                  f"{cfs['share_of_threshold_pct']:.0f}% of the EUR {cfs['threshold_eur']:,.0f} threshold")
        if cfs["reached"]:
            notes.append(f"Audit certificate: {so_far}. A certificate on the financial statements (CFS) is "
                         "due with the final report: appoint the auditor and budget the fee.")
        elif cfs["expected"]:
            notes.append(f"Audit certificate: {so_far}. At this pace the total reaches about "
                         f"EUR {cfs['projected_eur']:,.0f}, so a certificate on the financial statements (CFS) "
                         "will be due with the final report: budget the audit fee now.")
        else:
            notes.append(f"Audit certificate: {so_far}; at this pace the threshold is not reached, so no "
                         "certificate on the financial statements (CFS) is expected.")
    if deliverables is not None:
        late = deliverables[deliverables["status"].isin(["late", "overdue"])]
        over = deliverables[deliverables["status"] == "overdue"]
        if len(over):
            notes.append("Overdue at the report date: " + "; ".join(f"{r.id} {r.title} ({r.days_late} days)"
                                                                     for r in over.itertuples())
                         + ". Explain the delay and the new date in the technical report.")
        if len(late) > len(over):
            notes.append(f"{len(late) - len(over)} other items were submitted late "
                         f"(on average {late.loc[late['status'] == 'late', 'days_late'].mean():.0f} days).")
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
Rules: {programme.name} ({project.get('funding_scheme', '')}), indirect costs {programme.indirect_rate:.0%}
flat rate, EU funding rate {project['funding_rate']:.0%}.*

## Key figures

| | EUR |
| --- | ---: |
| Booked to the project by the department | {_money(s['declared_eur'])} |
| Eligible after the checks | {_money(s['eligible_eur'])} |
| Ineligible (cut, including the indirect costs on them) | {_money(s['ineligible_eur'])} |
| At risk: eligible only if a decision or document comes through | {_money(s['at_risk_eur'])} |
| Indirect costs included in the eligible total | {_money(s['indirect_eur'])} |
| EU contribution requested ({s['funding_rate']:.0%} of the eligible costs) | {_money(s['requested_contribution_eur'])} |
| Not covered by the EU: national co-funding or own resources | {_money(s['not_covered_eur'])} |

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
""" + (f"""
## Deliverables and milestones

Status at the report date, {s.get('report_date', period['end'])}.

{_md_table(deliverables[['id', 'type', 'title', 'wp', 'due_date', 'submitted_date', 'status', 'days_late']].fillna('').rename(columns={'id': 'ID', 'type': 'Type', 'title': 'Title', 'wp': 'WP', 'due_date': 'Due', 'submitted_date': 'Submitted', 'status': 'Status', 'days_late': 'Days late'}))}
""" if deliverables is not None else "") + (_calendar_md(calendar, programme) if calendar else "") + f"""
## Figures

{fig_md}
"""
    (out_dir / f"{period_id}_report.md").write_text(md)
    return out_dir / f"{period_id}_report.md"
