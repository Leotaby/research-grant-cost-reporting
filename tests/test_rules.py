import pandas as pd
import pytest

from grantcheck.rules import check_expenses

PROJECT = {"start": "2025-01-01", "end": "2028-12-31", "subcontracts_in_annex1": ["SC-01"],
           "travel_policy": {"flight_class": "economy"}, "direct_award_limit_eur": 140_000}
PERIOD = {"start": "2025-01-01", "end": "2026-06-30"}
BASE = dict(category="C3", description="Item", wp="WP1", supplier="Supplier", invoice_ref="F-1",
            net_eur=100.0, vat_eur=22.0, vat_recoverable=False, declared_eur=122.0, procurement="direct award",
            purchase_price_eur=None, useful_life_months=None, available_from=None, use_share=None,
            flight_class=None, economy_fare_eur=None, subcontract_id=None, other_eu_grant=None)


def run(**overrides):
    row = {**BASE, "expense_id": "X-1", "date": "2025-06-01", **overrides}
    lines, issues = check_expenses(pd.DataFrame([row]), PROJECT, PERIOD)
    return lines.iloc[0] if len(lines) else None, [i["rule"] for i in issues]


def test_clean_line_passes():
    line, rules = run()
    assert rules == [] and line.eligible_eur == 122.0


def test_cost_before_the_start_is_ineligible():
    line, rules = run(date="2024-12-18")
    assert rules == ["R01"] and line.eligible_eur == 0


def test_line_of_a_later_period_is_left_out():
    line, rules = run(date="2027-03-01")
    assert line is None and rules == []


def test_missing_invoice():
    line, rules = run(invoice_ref=None)
    assert rules == ["R05"] and line.ineligible_eur == 122.0


def test_recoverable_vat_is_removed():
    line, rules = run(vat_recoverable=True)
    assert rules == ["R06"] and line.eligible_eur == pytest.approx(100.0)


def test_double_funding():
    _, rules = run(other_eu_grant="ERC-DEMO")
    assert rules == ["R07"]


def test_bank_charges_and_interest():
    assert run(category="bank_charges", vat_eur=0.0, declared_eur=35.0)[1] == ["R08"]
    assert run(category="interest", vat_eur=0.0, declared_eur=180.0)[1] == ["R09"]


def test_equipment_declared_at_full_price():
    line, rules = run(category="C2", net_eur=48_000.0, vat_eur=0.0, declared_eur=48_000.0,
                      purchase_price_eur=48_000.0, useful_life_months=60, available_from="2025-03-01",
                      use_share=1.0, procurement="negotiated")
    assert rules == ["R04"]
    assert line.eligible_eur == pytest.approx(12_800) and line.ineligible_eur == pytest.approx(35_200)


def test_business_class_is_at_risk_above_the_economy_fare():
    line, rules = run(category="C1", vat_eur=0.0, net_eur=4150.0, declared_eur=4150.0,
                      flight_class="business", economy_fare_eur=1350.0, procurement="framework")
    assert rules == ["W01"] and line.at_risk_eur == pytest.approx(2800)


def test_subcontract_outside_annex1_is_at_risk():
    line, rules = run(category="B", subcontract_id="SC-02")
    assert rules == ["W02"] and line.at_risk_eur == pytest.approx(122.0)


def test_direct_award_from_140k():
    _, rules = run(category="C2", net_eur=150_000.0, vat_eur=0.0, declared_eur=25_000.0,
                   purchase_price_eur=150_000.0, useful_life_months=60, available_from="2025-09-01",
                   use_share=1.0)
    assert rules == ["W03"]
    assert run(net_eur=139_999.0, vat_eur=0.0, declared_eur=139_999.0)[1] == []
