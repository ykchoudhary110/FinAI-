from typing import List, Tuple, Dict, Any
from finai.domain.models.financial_models import (
    TaxCalculationResult,
    TaxRegime,
    TaxSlabBreakdown,
    TaxpayerCategory,
)


def calculate_income_tax(
    gross_income: float,
    regime: TaxRegime = TaxRegime.NEW,
    is_salaried: bool = True,
    other_deductions: float = 0.0,  # 80C, 80D etc (applicable to Old Regime)
    category: TaxpayerCategory = TaxpayerCategory.INDIVIDUAL,
) -> TaxCalculationResult:
    """
    Computes Income Tax for FY 2025-26 (AY 2026-27) per Indian Tax Code.
    Strict implementation of Section 6 of FinAI Master Specification.
    """
    if gross_income < 0:
        raise ValueError("Gross income cannot be negative.")
    if other_deductions < 0:
        raise ValueError("Deductions cannot be negative.")

    # 1. Standard Deduction
    if regime == TaxRegime.NEW:
        std_deduction = 75000.0 if is_salaried else 0.0
        applied_other_deductions = 0.0  # Old regime deductions not allowed in New regime
    else:
        std_deduction = 50000.0 if is_salaried else 0.0
        applied_other_deductions = other_deductions

    # 2. Taxable Income
    total_deductions = std_deduction + applied_other_deductions
    taxable_income = max(0.0, gross_income - total_deductions)

    # 3. Slab Tax Computation
    slab_breakdown: List[TaxSlabBreakdown] = []
    slab_tax = 0.0

    if regime == TaxRegime.NEW:
        # FY 2025-26 New Regime Slabs
        slabs: List[Tuple[float, float, float, str]] = [
            (0.0, 400000.0, 0.0, "₹0 - ₹4L (Nil)"),
            (400000.0, 800000.0, 5.0, "₹4L - ₹8L (5%)"),
            (800000.0, 1200000.0, 10.0, "₹8L - ₹12L (10%)"),
            (1200000.0, 1600000.0, 15.0, "₹12L - ₹16L (15%)"),
            (1600000.0, 2000000.0, 20.0, "₹16L - ₹20L (20%)"),
            (2000000.0, 2400000.0, 25.0, "₹20L - ₹24L (25%)"),
            (2400000.0, float("inf"), 30.0, "Above ₹24L (30%)"),
        ]
        for min_val, max_val, rate, label in slabs:
            if taxable_income > min_val:
                taxable_in_slab = min(taxable_income, max_val) - min_val
                tax_amount = taxable_in_slab * (rate / 100.0)
                slab_tax += tax_amount
                slab_breakdown.append(
                    TaxSlabBreakdown(
                        slab_label=label,
                        taxable_in_slab=round(taxable_in_slab, 2),
                        rate_percent=rate,
                        tax_amount=round(tax_amount, 2),
                    )
                )
    else:
        # Old Regime Slabs (varies by age category)
        if category == TaxpayerCategory.SUPER_SENIOR:
            basic_exemption = 500000.0
        elif category == TaxpayerCategory.SENIOR:
            basic_exemption = 300000.0
        else:
            basic_exemption = 250000.0

        if basic_exemption == 500000.0:
            slabs = [
                (0.0, 500000.0, 0.0, "₹0 - ₹5L (Nil)"),
                (500000.0, 1000000.0, 20.0, "₹5L - ₹10L (20%)"),
                (1000000.0, float("inf"), 30.0, "Above ₹10L (30%)"),
            ]
        elif basic_exemption == 300000.0:
            slabs = [
                (0.0, 300000.0, 0.0, "₹0 - ₹3L (Nil)"),
                (300000.0, 500000.0, 5.0, "₹3L - ₹5L (5%)"),
                (500000.0, 1000000.0, 20.0, "₹5L - ₹10L (20%)"),
                (1000000.0, float("inf"), 30.0, "Above ₹10L (30%)"),
            ]
        else:
            slabs = [
                (0.0, 250000.0, 0.0, "₹0 - ₹2.5L (Nil)"),
                (250000.0, 500000.0, 5.0, "₹2.5L - ₹5L (5%)"),
                (500000.0, 1000000.0, 20.0, "₹5L - ₹10L (20%)"),
                (1000000.0, float("inf"), 30.0, "Above ₹10L (30%)"),
            ]

        for min_val, max_val, rate, label in slabs:
            if taxable_income > min_val:
                taxable_in_slab = min(taxable_income, max_val) - min_val
                tax_amount = taxable_in_slab * (rate / 100.0)
                slab_tax += tax_amount
                slab_breakdown.append(
                    TaxSlabBreakdown(
                        slab_label=label,
                        taxable_in_slab=round(taxable_in_slab, 2),
                        rate_percent=rate,
                        tax_amount=round(tax_amount, 2),
                    )
                )

    # 4. Section 87A Rebate
    rebate = 0.0
    if regime == TaxRegime.NEW:
        if taxable_income <= 1200000.0:
            rebate = min(slab_tax, 60000.0)
    else:
        if taxable_income <= 500000.0:
            rebate = min(slab_tax, 12500.0)

    tax_after_rebate = max(0.0, slab_tax - rebate)

    # 5. Surcharge & Marginal Relief
    surcharge = 0.0
    marginal_relief = 0.0

    if tax_after_rebate > 0 and taxable_income > 5000000.0:
        if taxable_income > 50000000.0:  # > 5Cr
            threshold = 50000000.0
            surcharge_rate = 0.25 if regime == TaxRegime.NEW else 0.37
        elif taxable_income > 20000000.0:  # > 2Cr
            threshold = 20000000.0
            surcharge_rate = 0.25
        elif taxable_income > 10000000.0:  # > 1Cr
            threshold = 10000000.0
            surcharge_rate = 0.15
        else:  # > 50L
            threshold = 5000000.0
            surcharge_rate = 0.10

        raw_surcharge = tax_after_rebate * surcharge_rate

        # Compute tax on threshold
        tax_on_threshold_res = calculate_income_tax(
            gross_income=threshold + total_deductions,
            regime=regime,
            is_salaried=is_salaried,
            other_deductions=applied_other_deductions,
            category=category,
        )
        tax_on_threshold = tax_on_threshold_res.tax_after_rebate
        total_with_surcharge = tax_after_rebate + raw_surcharge
        max_allowed_tax = tax_on_threshold + (taxable_income - threshold)

        if total_with_surcharge > max_allowed_tax:
            marginal_relief = round(total_with_surcharge - max_allowed_tax, 2)
            surcharge = round(raw_surcharge - marginal_relief, 2)
        else:
            surcharge = round(raw_surcharge, 2)

    # 6. Health & Education Cess (4%)
    tax_subject_to_cess = tax_after_rebate + surcharge
    cess = round(tax_subject_to_cess * 0.04, 2)
    total_tax_payable = round(tax_subject_to_cess + cess, 2)

    effective_tax_rate = (
        round((total_tax_payable / gross_income) * 100.0, 2) if gross_income > 0 else 0.0
    )

    return TaxCalculationResult(
        assessment_year="2026-27",
        financial_year="2025-26",
        regime=regime,
        gross_income=round(gross_income, 2),
        standard_deduction=std_deduction,
        other_deductions=applied_other_deductions,
        taxable_income=round(taxable_income, 2),
        slab_tax=slab_tax,
        slab_breakdown=slab_breakdown,
        section_87a_rebate=round(rebate, 2),
        tax_after_rebate=round(tax_after_rebate, 2),
        surcharge=surcharge,
        marginal_relief=marginal_relief,
        cess=cess,
        total_tax_payable=total_tax_payable,
        effective_tax_rate=effective_tax_rate,
    )


def calculate_hra_exemption(
    basic_salary: float,
    hra_received: float,
    rent_paid: float,
    is_metro: bool = True
) -> Dict[str, Any]:
    """
    Computes House Rent Allowance (HRA) Exemption under Section 10(13A) of Income Tax Act 1961.
    Rule: Minimum of:
      1. Actual HRA received
      2. Rent paid minus 10% of Basic Salary
      3. 50% of Basic (Metro: Delhi, Mumbai, Kolkata, Chennai) or 40% (Non-Metro)
    """
    if basic_salary <= 0 or hra_received <= 0:
        return {"exempt_hra": 0.0, "taxable_hra": max(0.0, hra_received), "details": "No HRA exemption applicable."}

    condition1 = hra_received
    condition2 = max(0.0, rent_paid - (0.10 * basic_salary))
    condition3 = 0.50 * basic_salary if is_metro else 0.40 * basic_salary

    exempt_hra = round(min(condition1, condition2, condition3), 2)
    taxable_hra = round(max(0.0, hra_received - exempt_hra), 2)

    return {
        "exempt_hra": exempt_hra,
        "taxable_hra": taxable_hra,
        "actual_hra": round(hra_received, 2),
        "rent_minus_10pct_basic": round(condition2, 2),
        "salary_pct_limit": round(condition3, 2),
        "is_metro": is_metro
    }


def calculate_presumptive_tax_44ada(
    gross_receipts: float,
    actual_expenses: float = 0.0
) -> Dict[str, Any]:
    """
    Computes Presumptive Income for Professionals (Freelancers, Developers, CAs, Doctors, Consultants)
    under Section 44ADA of Income Tax Act 1961.
    Threshold: Gross receipts up to ₹75 Lakhs (if digital receipts >= 95%).
    Deemed Net Profit: Minimum 50% of Gross Receipts.
    """
    if gross_receipts > 7500000.0:
        is_eligible = False
        message = "Gross receipts exceed ₹75 Lakhs threshold. Tax audit required under Section 44AB."
    else:
        is_eligible = True
        message = "Eligible for Section 44ADA presumptive taxation."

    deemed_profit = round(gross_receipts * 0.50, 2)
    actual_profit = max(0.0, gross_receipts - actual_expenses)
    taxable_profit = deemed_profit if is_eligible else actual_profit

    return {
        "is_eligible": is_eligible,
        "gross_receipts": round(gross_receipts, 2),
        "deemed_profit_50pct": deemed_profit,
        "actual_profit": round(actual_profit, 2),
        "taxable_presumptive_income": taxable_profit,
        "message": message
    }


def calculate_presumptive_tax_44ad(
    digital_turnover: float,
    cash_turnover: float = 0.0
) -> Dict[str, Any]:
    """
    Computes Presumptive Income for Small Businesses under Section 44AD of Income Tax Act 1961.
    Threshold: Turnover up to ₹3 Crores (if cash receipts <= 5%).
    Deemed Net Profit: 6% on digital/banking turnover + 8% on cash turnover.
    """
    total_turnover = digital_turnover + cash_turnover
    if total_turnover > 30000000.0:
        is_eligible = False
        message = "Total turnover exceeds ₹3 Crores limit. Formal tax audit mandatory under Section 44AB."
    else:
        is_eligible = True
        message = "Eligible for Section 44AD presumptive business taxation."

    deemed_digital_profit = round(digital_turnover * 0.06, 2)
    deemed_cash_profit = round(cash_turnover * 0.08, 2)
    total_deemed_profit = round(deemed_digital_profit + deemed_cash_profit, 2)

    return {
        "is_eligible": is_eligible,
        "total_turnover": round(total_turnover, 2),
        "digital_turnover": round(digital_turnover, 2),
        "cash_turnover": round(cash_turnover, 2),
        "deemed_digital_profit_6pct": deemed_digital_profit,
        "deemed_cash_profit_8pct": deemed_cash_profit,
        "total_presumptive_profit": total_deemed_profit,
        "message": message
    }


def calculate_capital_gains_tax(
    stcg_equity: float = 0.0,
    ltcg_equity: float = 0.0,
    ltcg_property_gold: float = 0.0
) -> Dict[str, Any]:
    """
    Computes Capital Gains Tax under Budget 2024/2025 Revised Rates:
    - STCG on Listed Equity (Sec 111A): 20% (increased from 15%)
    - LTCG on Listed Equity (Sec 112A): 12.5% (with ₹1.25 Lakh annual exemption, increased from ₹1 Lakh @ 10%)
    - LTCG on Real Estate / Gold / Unlisted (Sec 112): 12.5% without indexation
    """
    tax_stcg_equity = round(max(0.0, stcg_equity) * 0.20, 2)
    
    taxable_ltcg_equity = max(0.0, ltcg_equity - 125000.0)
    tax_ltcg_equity = round(taxable_ltcg_equity * 0.125, 2)
    
    tax_ltcg_property = round(max(0.0, ltcg_property_gold) * 0.125, 2)
    
    total_capital_gains_tax = round(tax_stcg_equity + tax_ltcg_equity + tax_ltcg_property, 2)
    total_cess = round(total_capital_gains_tax * 0.04, 2)
    final_tax = round(total_capital_gains_tax + total_cess, 2)

    return {
        "stcg_equity_gain": round(stcg_equity, 2),
        "stcg_equity_tax_20pct": tax_stcg_equity,
        "ltcg_equity_gain": round(ltcg_equity, 2),
        "ltcg_equity_exemption": 125000.0,
        "taxable_ltcg_equity": round(taxable_ltcg_equity, 2),
        "ltcg_equity_tax_12_5pct": tax_ltcg_equity,
        "ltcg_property_gain": round(ltcg_property_gold, 2),
        "ltcg_property_tax_12_5pct": tax_ltcg_property,
        "total_capital_gains_tax": total_capital_gains_tax,
        "cess_4pct": total_cess,
        "final_capital_gains_tax_payable": final_tax
    }


def compare_tax_regimes(
    gross_income: float,
    is_salaried: bool = True,
    deductions_80c: float = 0.0,
    deductions_80d: float = 0.0,
    deductions_80ccd: float = 0.0,
    hra_exemption: float = 0.0,
    home_loan_interest_24b: float = 0.0,
    other_deductions: float = 0.0
) -> Dict[str, Any]:
    """
    Auto-Optimizer: Compares Old Regime vs New Regime (Sec 115BAC) and recommends the maximum tax saving option.
    """
    total_old_deductions = (
        min(150000.0, deductions_80c) +
        min(100000.0, deductions_80d) +
        min(50000.0, deductions_80ccd) +
        hra_exemption +
        min(200000.0, home_loan_interest_24b) +
        other_deductions
    )

    new_result = calculate_income_tax(
        gross_income=gross_income,
        regime=TaxRegime.NEW,
        is_salaried=is_salaried,
        other_deductions=0.0
    )

    old_result = calculate_income_tax(
        gross_income=gross_income,
        regime=TaxRegime.OLD,
        is_salaried=is_salaried,
        other_deductions=total_old_deductions
    )

    if new_result.total_tax_payable < old_result.total_tax_payable:
        recommended = "NEW"
        savings = round(old_result.total_tax_payable - new_result.total_tax_payable, 2)
        advice = f"New Tax Regime (Section 115BAC) is recommended. Saves ₹{savings:,.2f} in tax."
    elif old_result.total_tax_payable < new_result.total_tax_payable:
        recommended = "OLD"
        savings = round(new_result.total_tax_payable - old_result.total_tax_payable, 2)
        advice = f"Old Tax Regime is recommended due to high Chapter VI-A deductions. Saves ₹{savings:,.2f} in tax."
    else:
        recommended = "EQUAL"
        savings = 0.0
        advice = "Both Old and New Tax Regimes result in identical tax liability."

    return {
        "gross_income": gross_income,
        "new_regime": {
            "standard_deduction": new_result.standard_deduction,
            "taxable_income": new_result.taxable_income,
            "slab_tax": new_result.slab_tax,
            "rebate_87a": new_result.section_87a_rebate,
            "cess": new_result.cess,
            "total_tax": new_result.total_tax_payable
        },
        "old_regime": {
            "standard_deduction": old_result.standard_deduction,
            "chapter_via_deductions": total_old_deductions,
            "taxable_income": old_result.taxable_income,
            "slab_tax": old_result.slab_tax,
            "rebate_87a": old_result.section_87a_rebate,
            "cess": old_result.cess,
            "total_tax": old_result.total_tax_payable
        },
        "recommended_regime": recommended,
        "tax_savings": savings,
        "advice": advice
    }
