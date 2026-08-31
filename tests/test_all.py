"""Test suite for FinAI deterministic rule engines."""
from __future__ import annotations

import pytest
from finai.rules import (
    gst, income_tax, capital_gains, emi, hra_exemption,
    presumptive_44ada, presumptive_44ad, blocked_credit_17_5, rule_86b_check,
)
from finai.gst_engine import resolve_rate
from finai.validators import validate_gst
from finai.catalog import by_code, find_candidates, CATALOG
from finai.parser import parse_transaction


# ==================== GST rules ====================

class TestGST:
    def test_intrastate(self):
        r = gst(100000, 18, False)
        assert r["taxable_value"] == 100000.0
        assert r["gst_amount"] == 18000.0
        assert r["cgst"] == 9000.0
        assert r["sgst"] == 9000.0
        assert r["igst"] == 0.0
        assert r["invoice_total"] == 118000.0

    def test_interstate(self):
        r = gst(100000, 18, True)
        assert r["igst"] == 18000.0
        assert r["cgst"] == 0.0
        assert r["sgst"] == 0.0

    def test_exempt_zero_rate(self):
        r = gst(50000, 0, False)
        assert r["gst_amount"] == 0.0
        assert r["invoice_total"] == 50000.0

    def test_28_percent(self):
        r = gst(200000, 28, False)
        assert r["gst_amount"] == 56000.0
        assert r["cgst"] == 28000.0

    def test_5_percent(self):
        r = gst(100000, 5, True)
        assert r["gst_amount"] == 5000.0
        assert r["igst"] == 5000.0


# ==================== GST engine ====================

class TestGSTEngine:
    def test_valid_code(self):
        r = resolve_rate("9403")
        assert r.rate == 18.0
        assert r.name == "Office furniture"

    def test_unknown_code_raises(self):
        with pytest.raises(ValueError, match="Unrecognized"):
            resolve_rate("9999999")

    def test_interstate_split(self):
        r = resolve_rate("8703", is_interstate=True)
        assert r.igst == 28.0
        assert r.cgst == 0.0

    def test_date_valid(self):
        r = resolve_rate("9403", transaction_date="2024-06-15")
        assert r.is_valid_for_date is True

    def test_date_before_gst(self):
        r = resolve_rate("9403", transaction_date="2016-01-01")
        assert r.is_valid_for_date is False

    def test_blocked_credit_flag(self):
        r = resolve_rate("8703")
        assert r.itc_eligible is False


# ==================== Validators ====================

class TestValidators:
    def test_valid_intrastate(self):
        r = validate_gst(100000, 18000, 9000, 9000, 0, 118000, False)
        assert r["valid"] is True

    def test_valid_interstate(self):
        r = validate_gst(100000, 18000, 0, 0, 18000, 118000, True)
        assert r["valid"] is True

    def test_bad_split(self):
        r = validate_gst(100000, 18000, 5000, 5000, 0, 118000, False)
        assert r["valid"] is False

    def test_bad_total(self):
        r = validate_gst(100000, 18000, 9000, 9000, 0, 999999, False)
        assert r["valid"] is False

    def test_negative(self):
        r = validate_gst(-100, 18000, 9000, 9000, 0, 118000, False)
        assert r["valid"] is False


# ==================== Income tax ====================

class TestIncomeTax:
    def test_new_regime_below_rebate(self):
        t = income_tax(1200000, "new")
        assert t["total_tax"] == 0.0

    def test_new_regime_above_rebate(self):
        t = income_tax(2000000, "new")
        assert t["total_tax"] > 0

    def test_old_regime_with_deductions(self):
        t = income_tax(1200000, "old", deductions=150000, hra=100000, home_loan=200000)
        assert t["deductions_allowed"] > 50000

    def test_old_vs_new(self):
        new = income_tax(800000, "new")
        old = income_tax(800000, "old")
        assert new["total_tax"] == 0.0  # Both should be 0 under rebate


# ==================== Capital gains ====================

class TestCapitalGains:
    def test_stcg(self):
        cg = capital_gains(100000, 0, 0)
        assert cg["stcg_tax"] == 20000.0

    def test_ltcg_exemption(self):
        cg = capital_gains(0, 125000, 0)
        assert cg["ltcg_equity_tax"] == 0.0  # Fully exempt

    def test_ltcg_above_exemption(self):
        cg = capital_gains(0, 225000, 0)
        assert cg["taxable_ltcg_equity"] == 100000.0
        assert cg["ltcg_equity_tax"] == 12500.0

    def test_cess_applied(self):
        cg = capital_gains(100000, 0, 0)
        assert cg["cess"] > 0


# ==================== EMI ====================

class TestEMI:
    def test_basic_emi(self):
        e = emi(5000000, 8.5, 240)
        assert e["monthly_emi"] > 0
        assert e["total_payment"] > e["principal"]

    def test_zero_rate(self):
        e = emi(1200000, 0, 12)
        assert e["monthly_emi"] == 100000.0

    def test_total_interest(self):
        e = emi(1000000, 10, 120)
        assert e["total_interest"] > 0
        assert abs(e["total_payment"] - (e["principal"] + e["total_interest"])) < 0.02


# ==================== HRA ====================

class TestHRA:
    def test_metro(self):
        h = hra_exemption(600000, 240000, 240000, True)
        assert h["exempt_hra"] > 0
        assert h["exempt_hra"] <= h["actual_hra"]

    def test_non_metro(self):
        h = hra_exemption(600000, 240000, 240000, False)
        assert h["percent_of_basic"] == 240000.0  # 40% of 600k

    def test_zero_rent(self):
        h = hra_exemption(600000, 240000, 0, True)
        assert h["exempt_hra"] == 0.0  # rent - 10% basic = negative → 0


# ==================== Presumptive tax ====================

class TestPresumptive:
    def test_44ada(self):
        r = presumptive_44ada(5000000)
        assert r["taxable_profit"] == 2500000.0

    def test_44ad(self):
        r = presumptive_44ad(8000000, 2000000)
        assert r["digital_profit"] == 480000.0
        assert r["cash_profit"] == 160000.0
        assert r["total_profit"] == 640000.0


# ==================== Blocked credit ====================

class TestBlockedCredit:
    def test_motor_vehicle(self):
        r = blocked_credit_17_5("motor vehicle")
        assert r["is_blocked"] is True
        assert "17(5)(a)" in r["section"]

    def test_food(self):
        r = blocked_credit_17_5("restaurant catering")
        assert r["is_blocked"] is True

    def test_eligible(self):
        r = blocked_credit_17_5("office supplies")
        assert r["is_blocked"] is False


# ==================== Rule 86B ====================

class TestRule86B:
    def test_compliant(self):
        r = rule_86b_check(500000, 10000)
        assert r["compliant"] is True

    def test_non_compliant(self):
        r = rule_86b_check(500000, 100)
        assert r["compliant"] is False


# ==================== Catalog ====================

class TestCatalog:
    def test_catalog_size(self):
        assert len(CATALOG) >= 20

    def test_by_code(self):
        item = by_code("9403")
        assert item is not None
        assert item["kind"] == "HSN"

    def test_find_candidates(self):
        results = find_candidates("laptop computer")
        assert len(results) > 0


# ==================== Parser ====================

class TestParser:
    def test_amount_extraction(self):
        r = parse_transaction("I sold goods for Rs 50,000")
        assert r["amount"] == 50000.0

    def test_purchase_detection(self):
        r = parse_transaction("I purchased a laptop for 45000")
        assert r["transaction_type"] == "purchase"

    def test_interstate_detection(self):
        r = parse_transaction("sold to customer in Mumbai interstate")
        assert r["interstate"] is True

    def test_needs_classification(self):
        r = parse_transaction("I made a sale of 200000")
        assert r["needs_classification"] is True
        assert len(r["quick_picks"]) > 0

    def test_no_classification_needed(self):
        r = parse_transaction("sold 5 office chairs for 45000")
        assert r["needs_classification"] is False
