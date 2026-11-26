import pandas as pd
import pytest

from grantcheck.config import PROGRAMMES
from grantcheck.personnel import daily_rate, max_declarable_days, personnel_costs, round_half_day

HE = PROGRAMMES["HORIZON"]


def test_daily_rate_for_a_full_year_is_annual_costs_over_215():
    assert daily_rate(43_000) == pytest.approx(200.0)


@pytest.mark.parametrize("days, expected", [(10.2, 10.0), (10.25, 10.5), (10.74, 10.5), (10.75, 11.0)])
def test_rounding_to_half_days(days, expected):
    assert round_half_day(days) == expected


def test_part_year_rate_uses_the_months_within_the_reporting_period():
    # examples in the AGA (Art. 6.2.A.1): six months full time, six months half time, one month half time
    assert max_declarable_days(6) == 107.5
    assert max_declarable_days(6, working_time=0.5) == 54
    assert max_declarable_days(1, working_time=0.5) == 9
    assert daily_rate(21_500, months=6) == pytest.approx(200.0)
    # AGA example: EUR 75 000 over six months at half time followed by twelve months full time
    assert round_half_day(215 / 12 * 6 * 0.5 + 215) == 269
    assert 75_000 / 269 == pytest.approx(278.81, abs=0.005)


def _staff(cost=43_000, months=12, other_days=0):
    return pd.DataFrame([{"staff_id": "X1", "role": "Researcher", "cost_2025": cost, "months_2025": months,
                          "other_eu_grant_days_2025": other_days}])


def _records(days_per_month=20.0, unsigned=(), months=range(1, 13)):
    return pd.DataFrame([{"staff_id": "X1", "month": f"2025-{m:02d}", "wp": "WP1", "days": days_per_month,
                          "record_type": "timesheet", "signed_by_person": True,
                          "signed_by_supervisor": f"2025-{m:02d}" not in unsigned} for m in months])


PERIOD = {"start": "2025-01-01", "end": "2025-12-31"}


def test_days_above_a_ceiling_are_cut():
    # a full year: 240 days recorded, 215 at most
    table, wp, issues = personnel_costs(_staff(), _records(20.0), PERIOD, HE)
    row = table.iloc[0]
    assert row.days_recorded == 240
    assert row.days_above_cap == 25
    assert row.eligible_eur == pytest.approx(215 * 200)
    assert [i["rule"] for i in issues] == ["R02"]
    assert wp["days_eligible"].sum() == pytest.approx(215)
    # six months in the period: 120 days recorded, 107.5 at most, so never more than the actual costs
    half_year = {"start": "2025-01-01", "end": "2025-06-30"}
    table, _, _ = personnel_costs(_staff(cost=21_500, months=6), _records(20.0, months=range(1, 7)),
                                  half_year, HE)
    assert table.iloc[0].days_eligible == 107.5
    assert table.iloc[0].eligible_eur == pytest.approx(21_500)


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
