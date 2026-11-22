"""Equipment declared as depreciation (AGA Art. 6.2.C.2).

Only the depreciation for the months the asset is used in the reporting period can be charged,
times the share of its use for the action. Depreciation starts when the asset is available for use,
and the total charged can never exceed the purchase price.
"""
import pandas as pd


def months_of_use(available_from: str, period_start: str, period_end: str) -> int:
    """Whole months from the month the asset became available (or the period start, if later) to the
    end of the period, both included."""
    first = max(pd.Period(str(available_from)[:7], "M"), pd.Period(str(period_start)[:7], "M"))
    last = pd.Period(str(period_end)[:7], "M")
    return max((last.year - first.year) * 12 + last.month - first.month + 1, 0)


def depreciation_for_period(price: float, useful_life_months: int, available_from: str,
                            period_start: str, period_end: str, use_share: float = 1.0,
                            already_charged: float = 0.0) -> float:
    """Straight-line depreciation for the months of use in the period, times the share of use."""
    months = months_of_use(available_from, period_start, period_end)
    amount = price / useful_life_months * months * use_share
    return round(max(min(amount, price - already_charged), 0.0), 2)
