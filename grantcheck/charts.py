"""Figures for the periodic report."""
from pathlib import Path

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, BASE = "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, SAND, GREY = "#2a78d6", "#eb6834", "#f3c3a8", "#c9c7bf"
plt.rcParams.update({
    "font.family": ["Inter", "DejaVu Sans"], "font.size": 10,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": BASE,
    "axes.labelcolor": INK2, "text.color": INK, "xtick.color": MUTED, "ytick.color": MUTED,
})


def _tidy(ax, grid_axis="x"):
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.tick_params(axis="y", labelcolor=INK)


def _titles(fig, main, sub, note):
    fig.text(0.02, 0.965, main, fontsize=13, fontweight="bold", va="top")
    fig.text(0.02, 0.905, sub, fontsize=9.5, color=INK2, va="top")
    fig.text(0.02, 0.02, note, fontsize=8, color=MUTED, va="bottom")


SHORT = {"R01": "Outside the action duration", "R02": "Above 215 days a year",
         "R03": "No signed time records", "R04": "Equipment above depreciation", "R05": "No invoice",
         "R06": "Recoverable VAT", "R07": "Declared on another EU grant",
         "R08": "Bank charges on EU transfers", "R09": "Interest owed", "W01": "Business-class travel",
         "W02": "Subcontract not in Annex 1", "W03": "Direct award from EUR 140k"}


def eur(v):
    if abs(v) >= 1_000_000:
        return f"EUR {v / 1_000_000:,.2f}m"
    return f"EUR {v / 1000:,.1f}k" if abs(v) >= 1000 else f"EUR {v:,.0f}"


def _k_axis(ax):
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:,.0f}k" if v else "0"))

LABEL_BOX = dict(facecolor=SURFACE, edgecolor="none", pad=1.2)


def fig_declared_vs_eligible(statement, out: Path, period_id: str):
    st = statement[statement["category"] != "Total"]
    st = st[st["declared_eur"] > 0].iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    fig.subplots_adjust(top=0.80, bottom=0.17, left=0.31, right=0.97)
    y = range(len(st))
    ax.barh(y, st["eligible_eur"], color=BLUE, height=0.62, label="Eligible")
    ax.barh(y, st["ineligible_eur"], left=st["eligible_eur"], color=ORANGE, height=0.62, label="Ineligible")
    for i, (_, r) in enumerate(st.iterrows()):
        text = f"{eur(r.eligible_eur)} eligible"
        if r.ineligible_eur > 0:
            text += f" · {eur(r.ineligible_eur)} out"
        if r.at_risk_eur > 0:
            text += f" · {eur(r.at_risk_eur)} at risk"
        ax.text(r.declared_eur + st["declared_eur"].max() * 0.01, i, text, va="center", fontsize=8.5, color=INK2,
                bbox=LABEL_BOX)
    ax.set_yticks(list(y), st["category"])
    ax.set_xlim(0, st["declared_eur"].max() * 1.55)
    ax.set_xlabel("EUR")
    _k_axis(ax)
    _tidy(ax)
    ax.legend(frameon=False, loc="lower right", fontsize=9)
    total = statement[statement["category"] == "Total"].iloc[0]
    _titles(fig, f"{period_id}: what the department booked, and what survives the checks",
            f"Booked EUR {total.declared_eur:,.0f} · eligible EUR {total.eligible_eur:,.0f} · "
            f"ineligible EUR {total.ineligible_eur:,.0f} · at risk EUR {total.at_risk_eur:,.0f}",
            "Fictional data. Indirect costs (E) are the flat rate on the direct costs in the base, "
            "so they shrink with every ineligible direct cost.")
    fig.savefig(out, dpi=200)
    plt.close(fig)


def fig_budget_use(statement, summary, out: Path, period_id: str):
    st = statement[(statement["category"] != "Total") & (statement["budget_eur"] > 0)].iloc[::-1]
    t = summary["time_elapsed_pct"]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    fig.subplots_adjust(top=0.80, bottom=0.17, left=0.31, right=0.95)
    colors = [ORANGE if p > t + 15 else BLUE for p in st["budget_used_pct"]]
    ax.barh(range(len(st)), st["budget_used_pct"], color=colors, height=0.62)
    ax.axvline(t, color=INK2, linewidth=1.2, linestyle="--")
    ax.text(t + 0.8, len(st) - 0.45, f"time elapsed {t:.1f}%", fontsize=8.5, color=INK2, va="bottom")
    for i, (_, r) in enumerate(st.iterrows()):
        ax.text(r.budget_used_pct + 1, i, f"{r.budget_used_pct:.0f}% of {eur(r.budget_eur)}",
                va="center", fontsize=8.5, color=INK2, bbox=LABEL_BOX, zorder=3)
    ax.set_yticks(range(len(st)), st["category"])
    ax.set_xlim(0, max(100, st["budget_used_pct"].max() + 25))
    ax.set_xlabel("Eligible costs as a share of the budget for the whole action, %")
    _tidy(ax)
    _titles(fig, f"{period_id}: budget used by category against time elapsed",
            f"Month {summary['months_done']} of {summary['months_total']}; orange: more than 15 points "
            "ahead of time",
            "Fictional data. Eligible costs only.")
    fig.savefig(out, dpi=200)
    plt.close(fig)


def fig_days_cap(personnel, out: Path, year: int, cap: int = 215):
    p = personnel[personnel["year"] == year].sort_values("staff_id")
    fig, ax = plt.subplots(figsize=(9, 4.8))
    fig.subplots_adjust(top=0.80, bottom=0.17, left=0.08, right=0.97)
    x = range(len(p))
    out_days = p["days_recorded"] - p["days_eligible"]
    ax.bar(x, p["days_eligible"], color=BLUE, width=0.62, label="Days on this action, eligible")
    ax.bar(x, out_days, bottom=p["days_eligible"], color=ORANGE, width=0.62,
           label="Days on this action, not eligible")
    ax.bar(x, p["days_other_eu_grants"], bottom=p["days_recorded"], color=GREY, width=0.62,
           label="Days on other EU grants")
    ax.axhline(cap, color=INK2, linewidth=1.2, linestyle="--")
    ax.text(-0.4, cap + 3, f"{cap} day-equivalents a year", ha="left", fontsize=8.5, color=INK2)
    ax.set_xticks(list(x), p["staff_id"])
    ax.set_ylim(0, 300)
    ax.set_ylabel("Day-equivalents")
    _tidy(ax, "y")
    ax.legend(frameon=False, loc="upper left", fontsize=8.5, ncol=3)
    _titles(fig, f"Days declared per person in {year} against the yearly cap",
            "Orange: days above the cap or without signed time records",
            "Fictional data. The cap counts the days declared on all EU grants together (AGA Art. 6.2.A).")
    fig.savefig(out, dpi=200)
    plt.close(fig)


def fig_issues(issues, out: Path, period_id: str):
    g = issues.groupby(["rule", "title", "severity"])["amount_eur"].sum().reset_index()
    g = g.sort_values("amount_eur")
    fig, ax = plt.subplots(figsize=(9, 4.8))
    fig.subplots_adjust(top=0.80, bottom=0.15, left=0.33, right=0.95)
    colors = [ORANGE if s == "ineligible" else SAND for s in g["severity"]]
    ax.barh(range(len(g)), g["amount_eur"], color=colors, height=0.62)
    for i, v in enumerate(g["amount_eur"]):
        ax.text(v + g["amount_eur"].max() * 0.01, i, eur(v), va="center", fontsize=8.5, color=INK2)
    labels = [f"{r.rule}  {SHORT.get(r.rule, r.title)}" for r in g.itertuples()]
    ax.set_yticks(range(len(g)), labels, fontsize=9)
    ax.set_xlim(0, g["amount_eur"].max() * 1.2)
    ax.set_xlabel("EUR")
    _k_axis(ax)
    _tidy(ax)
    _titles(fig, f"{period_id}: findings by check",
            "Orange: ineligible, cut automatically · light orange: at risk, needs a decision",
            "Fictional data. Direct costs only; the indirect costs lost on top are in the statement.")
    fig.savefig(out, dpi=200)
    plt.close(fig)


def fig_deliverables(items, out: Path, project_start: str, as_of: str, period_id: str):
    from matplotlib.lines import Line2D

    from .deliverables import month_position

    d = items.sort_values(["due_month", "id"]).reset_index(drop=True)
    now = month_position(project_start, as_of)
    pos = list(range(len(d)))[::-1]
    fig, ax = plt.subplots(figsize=(9, 5.4))
    fig.subplots_adjust(top=0.80, bottom=0.2, left=0.40, right=0.97)
    for yi, r in zip(pos, d.itertuples()):
        due = float(r.due_month)
        if r.status == "on time":
            ax.plot(due, yi, "o", color=BLUE, ms=8, zorder=3)
        elif r.status == "late":
            sub = month_position(project_start, r.submitted_date)
            ax.plot([due, sub], [yi, yi], color=ORANGE, lw=3, solid_capstyle="round", zorder=2)
            ax.plot(sub, yi, "o", color=ORANGE, ms=8, zorder=3)
            ax.plot(due, yi, "|", color=INK2, ms=12, mew=1.5, zorder=3)
        elif r.status == "overdue":
            ax.plot([due, now], [yi, yi], color=ORANGE, lw=3, linestyle=(0, (1.5, 1)), zorder=2)
            ax.plot(due, yi, "X", color=ORANGE, ms=9, zorder=3)
        else:
            ax.plot(due, yi, "o", mfc=SURFACE, mec=MUTED, ms=8, mew=1.5, zorder=3)
    ax.axvline(now, color=INK2, linewidth=1.1, linestyle="--")
    ax.text(now + 0.2, len(d) - 0.4, "report date", fontsize=8.5, color=INK2, va="bottom")
    ax.set_yticks(pos, [f"{r.id}  {r.title}" for r in d.itertuples()], fontsize=8.5)
    ax.set_ylim(-0.7, len(d) - 0.1)
    ax.set_xlim(0, 25)
    ax.set_xticks(range(0, 25, 3))
    ax.set_xlabel("Project month (due at the end of the month)")
    _tidy(ax)
    handles = [Line2D([], [], marker="o", color=BLUE, ls="", ms=7, label="On time"),
               Line2D([], [], marker="o", color=ORANGE, lw=3, ms=7, label="Late: due date to submission"),
               Line2D([], [], marker="X", color=ORANGE, lw=3, ls=(0, (1.5, 1)), ms=7, label="Overdue"),
               Line2D([], [], marker="o", mfc=SURFACE, mec=MUTED, ls="", ms=7, label="Upcoming")]
    ax.legend(handles=handles, frameon=False, fontsize=8, ncol=4, loc="upper center",
              bbox_to_anchor=(0.32, -0.13))
    counts = d["status"].value_counts()
    _titles(fig, f"{period_id}: deliverables and milestones against their due dates",
            f"At the report date ({as_of}): {counts.get('on time', 0)} on time, {counts.get('late', 0)} late, "
            f"{counts.get('overdue', 0)} overdue, {counts.get('upcoming', 0)} upcoming",
            "Fictional data.")
    fig.savefig(out, dpi=200)
    plt.close(fig)
