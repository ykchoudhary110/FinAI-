import pytest
from finai.domain.rules.gst_rules import calculate_gst_forward, calculate_gst_reverse


def test_gst_forward_standard():
    res = calculate_gst_forward(1000.0, 18.0, is_interstate=False)
    assert res.base_amount == 1000.0
    assert res.gst_amount == 180.0
    assert res.total_amount == 1180.0
    assert res.cgst_amount == 90.0
    assert res.sgst_amount == 90.0
    assert res.igst_amount == 0.0


def test_gst_forward_interstate():
    res = calculate_gst_forward(1000.0, 18.0, is_interstate=True)
    assert res.is_interstate is True
    assert res.igst_amount == 180.0
    assert res.cgst_amount == 0.0


def test_gst_forward_zero_rate():
    res = calculate_gst_forward(500.0, 0.0)
    assert res.gst_amount == 0.0
    assert res.total_amount == 500.0


def test_gst_forward_28_percent():
    res = calculate_gst_forward(10000.0, 28.0)
    assert res.gst_amount == 2800.0
    assert res.total_amount == 12800.0


def test_gst_reverse_standard():
    res = calculate_gst_reverse(1180.0, 18.0)
    assert res.base_amount == 1000.0
    assert res.gst_amount == 180.0
    assert res.total_amount == 1180.0


def test_gst_reverse_zero_rate():
    res = calculate_gst_reverse(1000.0, 0.0)
    assert res.base_amount == 1000.0
    assert res.gst_amount == 0.0


def test_gst_negative_inputs():
    with pytest.raises(ValueError):
        calculate_gst_forward(-100.0, 18.0)
    with pytest.raises(ValueError):
        calculate_gst_reverse(100.0, -5.0)
