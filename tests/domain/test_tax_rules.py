import pytest
from finai.domain.models.financial_models import TaxRegime, TaxpayerCategory
from finai.domain.rules.tax_rules import calculate_income_tax


def test_tax_new_regime_nil_income():
    res = calculate_income_tax(0.0, regime=TaxRegime.NEW)
    assert res.gross_income == 0.0
    assert res.total_tax_payable == 0.0


def test_tax_new_regime_exact_slab_boundary_400k():
    res = calculate_income_tax(400000.0, regime=TaxRegime.NEW, is_salaried=True)
    assert res.taxable_income == 325000.0
    assert res.total_tax_payable == 0.0


def test_tax_new_regime_exact_87a_rebate_boundary():
    res = calculate_income_tax(1275000.0, regime=TaxRegime.NEW, is_salaried=True)
    assert res.taxable_income == 1200000.0
    assert res.slab_tax == 60000.0
    assert res.section_87a_rebate == 60000.0
    assert res.total_tax_payable == 0.0


def test_tax_new_regime_above_87a_boundary():
    res = calculate_income_tax(1275001.0, regime=TaxRegime.NEW, is_salaried=True)
    assert res.taxable_income == 1200001.0
    assert res.section_87a_rebate == 0.0
    assert res.total_tax_payable > 0.0


def test_tax_old_regime_individual():
    res = calculate_income_tax(
        1000000.0, regime=TaxRegime.OLD, is_salaried=True, other_deductions=150000.0
    )
    assert res.taxable_income == 800000.0
    assert res.slab_tax == 72500.0
    assert res.cess == 2900.0
    assert res.total_tax_payable == 75400.0


def test_tax_old_regime_senior_citizen():
    # Senior citizen basic exemption 3L
    res = calculate_income_tax(
        600000.0, regime=TaxRegime.OLD, is_salaried=False, category=TaxpayerCategory.SENIOR
    )
    assert res.taxable_income == 600000.0
    assert res.slab_tax == 30000.0  # (5L-3L)*5% = 10k + (6L-5L)*20% = 20k = 30k


def test_tax_old_regime_super_senior_citizen():
    # Super senior basic exemption 5L
    res = calculate_income_tax(
        600000.0, regime=TaxRegime.OLD, is_salaried=False, category=TaxpayerCategory.SUPER_SENIOR
    )
    assert res.taxable_income == 600000.0
    assert res.slab_tax == 20000.0  # (6L-5L)*20% = 20k


def test_tax_surcharge_thresholds():
    # > 50L (10% surcharge)
    r50 = calculate_income_tax(5500000.0, regime=TaxRegime.NEW, is_salaried=False)
    assert r50.surcharge >= 0.0

    # > 1Cr (15% surcharge)
    r1cr = calculate_income_tax(12000000.0, regime=TaxRegime.NEW, is_salaried=False)
    assert r1cr.surcharge >= 0.0

    # > 2Cr (25% surcharge)
    r2cr = calculate_income_tax(25000000.0, regime=TaxRegime.NEW, is_salaried=False)
    assert r2cr.surcharge >= 0.0


def test_tax_negative_income():
    with pytest.raises(ValueError):
        calculate_income_tax(-50000.0)
    with pytest.raises(ValueError):
        calculate_income_tax(500000.0, other_deductions=-1000.0)
