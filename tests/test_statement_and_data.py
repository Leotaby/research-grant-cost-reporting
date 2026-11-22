from pathlib import Path

import pandas as pd
import pytest

from grantcheck.__main__ import run
from grantcheck.config import PROGRAMMES
from grantcheck.statement import indirect_costs

ROOT = Path(__file__).resolve().parents[1]
DIRECT = {"A": 100.0, "B": 50.0, "C1": 0.0, "C2": 0.0, "C3": 0.0, "D": 0.0}


def test_horizon_flat_rate_leaves_out_subcontracting():
    assert indirect_costs(DIRECT, PROGRAMMES["HORIZON"]) == pytest.approx(25.0)


def test_standard_flat_rate_keeps_subcontracting_in_the_base():
    assert indirect_costs(DIRECT, PROGRAMMES["STANDARD"]) == pytest.approx(10.5)


# the problems planted in data/ (see data/README.md): the checks must find all of them, and nothing else
PLANTED = {("S05 2025", "R03"), ("S10 2026", "R03"), ("S08 2025", "R02"), ("S09 2025", "R02"),
           ("E-01", "R04"), ("E-06", "R04"), ("C-005", "R06"), ("C-006", "R06"), ("C-007", "R06"),
           ("C-011", "R05"), ("C-012", "R05"), ("C-016", "R07"), ("C-900", "R01"), ("F-01", "R08"),
           ("F-02", "R09"), ("T-019", "W01"), ("SC-02", "W02"), ("E-04", "W03")}


@pytest.fixture(scope="module")
def rp1(tmp_path_factory):
    return run(ROOT / "data", "RP1", tmp_path_factory.mktemp("reports"))


def test_all_planted_problems_are_found(rp1):
    _, _, issues, _ = rp1
    assert set(zip(issues["line"], issues["rule"])) == PLANTED


def test_statement_adds_up(rp1):
    statement, summary, _, _ = rp1
    body = statement[statement["category"] != "Total"]
    assert (body["declared_eur"] - body["eligible_eur"] - body["ineligible_eur"]).abs().max() < 0.01
    assert summary["eligible_eur"] == pytest.approx(body["eligible_eur"].sum(), abs=0.01)


def test_indirect_costs_are_25_percent_of_the_base(rp1):
    statement, _, _, _ = rp1
    s = statement.set_index("category")["eligible_eur"]
    base = s.drop(["B. Subcontracting costs", "E. Indirect costs", "Total"]).sum()
    assert s["E. Indirect costs"] == pytest.approx(0.25 * base, abs=0.01)
