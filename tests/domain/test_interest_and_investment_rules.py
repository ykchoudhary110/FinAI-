import pytest
from finai.domain.rules.interest_rules import (
    calculate_compound_interest,
    calculate_depreciation,
    calculate_investment_sip,
    calculate_simple_interest,
)


def test_simple_interest():
    res = calculate_simple_interest(10000.0, 8.5, 2.0)
    assert res["principal"] == 10000.0
    assert res["interest"] == 1700.0
    assert res["total_amount"] == 11700.0


def test_compound_interest():
    res = calculate_compound_interest(10000.0, 10.0, 2.0, compounding_frequency=1)
    assert res["principal"] == 10000.0
    assert res["total_amount"] == 12100.0
    assert res["interest"] == 2100.0


def test_depreciation_straight_line():
    res = calculate_depreciation(
        asset_cost=100000.0, salvage_value=10000.0, useful_life_years=5, is_wdv=False
    )
    assert res.method == "straight_line"
    assert len(res.annual_depreciation) == 5
    assert res.annual_depreciation[0] == 18000.0
    assert res.book_values[-1] == 10000.0


def test_depreciation_wdv():
    res = calculate_depreciation(
        asset_cost=100000.0, salvage_value=10000.0, useful_life_years=5, rate_percent=20.0, is_wdv=True
    )
    assert res.method == "written_down_value"
    assert len(res.annual_depreciation) == 5
    assert res.annual_depreciation[0] == 20000.0


def test_investment_sip():
    res = calculate_investment_sip(monthly_investment=5000.0, annual_rate=12.0, tenure_years=5)
    assert res.tool_type == "SIP"
    assert res.total_invested == 300000.0
    assert res.final_corpus > 300000.0
    assert len(res.breakdown) == 5


def test_interest_invalid_inputs():
    with pytest.raises(ValueError):
        calculate_simple_interest(-100.0, 5.0, 1.0)
    with pytest.raises(ValueError):
        calculate_compound_interest(100.0, 5.0, -1.0)
    with pytest.raises(ValueError):
        calculate_depreciation(0.0, 10.0, 5)
    with pytest.raises(ValueError):
        calculate_investment_sip(-500.0, 10.0, 5)
