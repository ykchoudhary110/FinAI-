import pytest
from finai.domain.ocr.receipt_parser import parse_ocr_text
from finai.domain.rules.emi_rules import calculate_emi
from finai.domain.rules.health_score_rules import calculate_financial_health_score


def test_emi_calculation_standard():
    res = calculate_emi(principal=100000.0, annual_rate=12.0, tenure_months=12)
    assert res.principal == 100000.0
    assert res.monthly_emi == 8884.88
    assert len(res.amortization_schedule) == 12
    assert res.amortization_schedule[-1].closing_balance == 0.0


def test_emi_zero_interest():
    res = calculate_emi(principal=120000.0, annual_rate=0.0, tenure_months=12)
    assert res.monthly_emi == 10000.0
    assert res.total_interest == 0.0


def test_emi_invalid_inputs():
    with pytest.raises(ValueError):
        calculate_emi(-10000.0, 10.0, 12)
    with pytest.raises(ValueError):
        calculate_emi(10000.0, 10.0, 0)


def test_ocr_parser_text_parsing():
    raw_ocr = """
    RELIANCE RETAIL LIMITED
    DATE: 15/08/2025
    GSTIN: 27AAAAA0000A1Z5
    Item 1 Milk    Rs. 60.00
    Item 2 Bread   Rs. 40.00
    TAX 18%        Rs. 18.00
    TOTAL AMOUNT   Rs. 118.00
    """
    receipt = parse_ocr_text(raw_ocr)
    assert receipt.vendor_name == "RELIANCE RETAIL LIMITED"
    assert receipt.receipt_date == "15/08/2025"
    assert receipt.gstin == "27AAAAA0000A1Z5"
    assert receipt.total_amount == 118.00
    assert receipt.confidence_score >= 0.7
    assert receipt.is_low_confidence is False


def test_ocr_parser_low_confidence():
    raw_ocr = "random noise string without total or date"
    receipt = parse_ocr_text(raw_ocr)
    assert receipt.total_amount == 0.0
    assert receipt.is_low_confidence is True


def test_health_score_calculation():
    score = calculate_financial_health_score(
        income=100000.0,
        expenses=40000.0,
        budget_adherence_percent=95.0,
        punctuality_percent=100.0,
        total_monthly_emi=15000.0,
        gst_compliance_percent=100.0,
    )
    assert 0 <= score.total_score <= 100
    assert score.total_score >= 80
    assert score.lowest_scoring_factor != ""
