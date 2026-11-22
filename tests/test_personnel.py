import pandas as pd
import pytest

from grantcheck.config import PROGRAMMES
from grantcheck.personnel import daily_rate, personnel_costs, rate_year, round_half_day

HE = PROGRAMMES["HORIZON"]


def test_daily_rate_is_annual_costs_over_215():
    assert daily_rate(43_000) == pytest.approx(200.0)


@pytest.mark.parametrize("days, expected", [(10.2, 10.0), (10.25, 10.5), (10.74, 10.5), (10.75, 11.0)])
def test_rounding_to_half_days(days, expected):
    assert round_half_day(days) == expected


def test_open_year_uses_last_closed_year():
    assert rate_year(2025, [2025]) == 2025
    assert rate_year(2026, [2025]) == 2025
    with pytest.raises(ValueError):
        rate_year(2025, [])


def _staff(other_days=0):
    return pd.DataFrame([{"staff_id": "X1", "role": "Researcher", "annual_cost_2025": 43_000,
                          "other_eu_grant_days_2025": other_days}])


def _records(days_per_month=20.0, unsigned=()):
    return pd.DataFrame([{"staff_id": "X1", "month": f"2025-{m:02d}", "wp": "WP1", "days": days_per_month,
                          "record_type": "timesheet", "signed_by_person": True,
                          "signed_by_supervisor": f"2025-{m:02d}" not in unsigned} for m in range(1, 13)])


PERIOD = {"start": "2025-01-01", "end": "2025-12-31", "closed_financial_years": [2025]}


def test_days_above_the_yearly_cap_are_cut():
    table, wp, issues = personnel_costs(_staff(), _records(20.0), PERIOD, HE)
    row = table.iloc[0]
    assert row.days_recorded == 240
    assert row.days_above_cap == 25
    assert row.eligible_eur == pytest.approx(215 * 200)
    assert [i["rule"] for i in issues] == ["R02"]
    assert wp["days_eligible"].sum() == pytest.approx(215)


def test_days_on_other_eu_grants_count_towards_the_cap():
    table, _, issues = personnel_costs(_staff(other_days=50), _records(15.0), PERIOD, HE)
    assert table.iloc[0].days_above_cap == 180 - 165
    assert issues[0]["amount_eur"] == pytest.approx(15 * 200)


def test_unsigned_months_are_ineligible():
    table, _, issues = personnel_costs(_staff(), _records(10.0, unsigned=("2025-03", "2025-04")), PERIOD, HE)
    row = table.iloc[0]
    assert row.days_unsupported == 20
    assert row.ineligible_eur == pytest.approx(20 * 200)
    assert issues[0]["rule"] == "R03"
