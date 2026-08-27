import pytest
from finai.domain.ocr.receipt_parser import parse_ocr_text


def test_ocr_parser_empty_and_whitespace():
    res = parse_ocr_text("   \n\n  \t ")
    assert res.vendor_name == "Unknown Vendor"
    assert res.total_amount == 0.0
    assert res.is_low_confidence is True


def test_ocr_parser_multiple_currency_numbers():
    text = """
    D-MART SUPERMARKET
    Date: 12-05-2026
    Item 1: Rs. 150.00
    Item 2: Rs. 350.00
    Subtotal: Rs. 500.00
    GST 18%: Rs. 90.00
    GRAND TOTAL: Rs. 590.00
    Amount Paid: Rs. 1000.00
    Change Given: Rs. 410.00
    """
    res = parse_ocr_text(text)
    assert res.vendor_name == "D-MART SUPERMARKET"
    assert res.receipt_date == "12-05-2026"
    assert res.total_amount == 590.00  # Picks GRAND TOTAL match over change given
    assert len(res.line_items) >= 2


def test_ocr_parser_missing_gstin():
    text = """
    CORNER COFFEE SHOP
    01/01/2026
    Espresso Rs 120.00
    TOTAL Rs 120.00
    """
    res = parse_ocr_text(text)
    assert res.vendor_name == "CORNER COFFEE SHOP"
    assert res.gstin is None
    assert res.total_amount == 120.00


def test_ocr_parser_malformed_text_and_dates():
    text = """
    ### CAFE COFFEE DAY ###
    INV DATE: 2026/04/15
    GSTIN: 07AAAAA0000A1Z5
    Cold Coffee   220.00
    Brownie       180.00
    NET PAYABLE   400.00
    """
    res = parse_ocr_text(text)
    assert "CAFE COFFEE DAY" in res.vendor_name
    assert res.receipt_date == "2026/04/15"
    assert res.gstin == "07AAAAA0000A1Z5"
    assert res.total_amount == 400.00
