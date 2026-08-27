from typing import List, Dict, Any
from finai.domain.models.financial_models import GstSplit


def calculate_gst_forward(amount: float, rate_percent: float, is_interstate: bool = False) -> GstSplit:
    """
    Forward GST Calculation:
    Base Amount -> GST Amount & Total Amount.
    """
    if amount < 0 or rate_percent < 0:
        raise ValueError("Amount and rate must be non-negative.")
    
    gst_amount = round(amount * (rate_percent / 100.0), 2)
    total_amount = round(amount + gst_amount, 2)
    
    if is_interstate:
        return GstSplit(
            is_interstate=True,
            base_amount=round(amount, 2),
            gst_rate=rate_percent,
            gst_amount=gst_amount,
            total_amount=total_amount,
            igst_rate=rate_percent,
            igst_amount=gst_amount,
        )
    else:
        half_rate = round(rate_percent / 2.0, 2)
        half_gst = round(gst_amount / 2.0, 2)
        return GstSplit(
            is_interstate=False,
            base_amount=round(amount, 2),
            gst_rate=rate_percent,
            gst_amount=gst_amount,
            total_amount=total_amount,
            cgst_rate=half_rate,
            cgst_amount=half_gst,
            sgst_rate=half_rate,
            sgst_amount=half_gst,
        )


def calculate_gst_reverse(total_amount: float, rate_percent: float, is_interstate: bool = False) -> GstSplit:
    """
    Reverse GST Calculation:
    GST-inclusive Total -> Base Amount & GST Amount.
    """
    if total_amount < 0 or rate_percent < 0:
        raise ValueError("Total amount and rate must be non-negative.")
    
    if rate_percent == 0:
        base_amount = total_amount
        gst_amount = 0.0
    else:
        base_amount = round(total_amount / (1.0 + (rate_percent / 100.0)), 2)
        gst_amount = round(total_amount - base_amount, 2)
        
    if is_interstate:
        return GstSplit(
            is_interstate=True,
            base_amount=base_amount,
            gst_rate=rate_percent,
            gst_amount=gst_amount,
            total_amount=round(total_amount, 2),
            igst_rate=rate_percent,
            igst_amount=gst_amount,
        )
    else:
        half_rate = round(rate_percent / 2.0, 2)
        half_gst = round(gst_amount / 2.0, 2)
        return GstSplit(
            is_interstate=False,
            base_amount=base_amount,
            gst_rate=rate_percent,
            gst_amount=gst_amount,
            total_amount=round(total_amount, 2),
            cgst_rate=half_rate,
            cgst_amount=half_gst,
            sgst_rate=half_rate,
            sgst_amount=half_gst,
        )


def check_itc_eligibility_sec16(
    has_tax_invoice: bool = True,
    goods_services_received: bool = True,
    tax_paid_by_supplier: bool = True,
    return_filed_gstr3b: bool = True,
    is_payment_within_180_days: bool = True
) -> Dict[str, Any]:
    """
    Evaluates Input Tax Credit (ITC) eligibility under Section 16(2) of CGST Act 2017.
    All 4 statutory conditions must be met:
    1. Possession of tax invoice/debit note
    2. Actual receipt of goods or services
    3. Supplier has paid tax to government (reflected in GSTR-2B)
    4. Recipient has filed GSTR-3B return
    5. Payment to supplier within 180 days (or ITC must be reversed with interest)
    """
    conditions = {
        "1. Possession of Tax Invoice": has_tax_invoice,
        "2. Receipt of Goods/Services": goods_services_received,
        "3. Supplier Tax Paid (GSTR-2B Match)": tax_paid_by_supplier,
        "4. GSTR-3B Filed by Recipient": return_filed_gstr3b,
        "5. Supplier Paid within 180 Days": is_payment_within_180_days
    }
    
    is_eligible = all(conditions.values())
    
    failed_conditions = [name for name, passed in conditions.items() if not passed]
    
    if is_eligible:
        status_message = "100% Eligible for Input Tax Credit under Section 16."
    else:
        status_message = f"Ineligible for ITC due to failed conditions: {', '.join(failed_conditions)}"

    return {
        "is_eligible": is_eligible,
        "conditions_breakdown": conditions,
        "failed_conditions": failed_conditions,
        "status_message": status_message
    }


def check_blocked_credit_sec17_5(expense_category: str, seating_capacity: int = 5) -> Dict[str, Any]:
    """
    Identifies Ineligible / Blocked Input Tax Credit under Section 17(5) of CGST Act 2017:
    - Motor vehicles with seating capacity <= 13 (except for driving school/passenger transport)
    - Food, beverages, outdoor catering, beauty treatment
    - Membership of clubs, health and fitness centers
    - Travel benefits to employees (leave/home travel)
    - Goods lost, stolen, destroyed, written off or gifted
    - Works contract for construction of immovable property
    """
    category_lower = expense_category.lower().strip()
    
    blocked = False
    reason = "Eligible standard business expense."
    
    if any(k in category_lower for k in ["motor vehicle", "car", "automobile"]):
        if seating_capacity <= 13:
            blocked = True
            reason = "Blocked under Section 17(5)(a): Motor vehicles for transportation of persons with seating capacity <= 13."
    elif any(k in category_lower for k in ["food", "beverage", "catering", "restaurant", "dining"]):
        blocked = True
        reason = "Blocked under Section 17(5)(b)(i): Food and beverages, outdoor catering."
    elif any(k in category_lower for k in ["gym", "club", "fitness"]):
        blocked = True
        reason = "Blocked under Section 17(5)(b)(ii): Membership of club, health and fitness centre."
    elif any(k in category_lower for k in ["personal", "gift", "stolen", "lost"]):
        blocked = True
        reason = "Blocked under Section 17(5)(g)/(h): Goods used for personal consumption or gifted/lost."
    elif any(k in category_lower for k in ["civil construction", "building construction"]):
        blocked = True
        reason = "Blocked under Section 17(5)(c): Works contract services for construction of immovable property."

    return {
        "expense_category": expense_category,
        "is_blocked": blocked,
        "is_eligible_itc": not blocked,
        "statutory_reference": "CGST Act 2017, Section 17(5)",
        "audit_note": reason
    }


def check_rule_86b_compliance(
    monthly_taxable_turnover: float,
    output_tax_liability: float
) -> Dict[str, Any]:
    """
    Rule 86B Compliance of CGST Rules:
    Applicable if taxable supply in a month > ₹50 Lakhs (excluding exempt/zero-rated).
    Restriction: Maximum 99% of output tax liability can be discharged via Electronic Credit Ledger (ITC).
    Minimum 1% must be paid via Electronic Cash Ledger.
    """
    is_applicable = monthly_taxable_turnover > 5000000.0
    
    if is_applicable:
        max_itc_allowed = round(output_tax_liability * 0.99, 2)
        min_cash_payable = round(output_tax_liability * 0.01, 2)
        message = "Rule 86B Applicable: Taxable turnover > ₹50L. Minimum 1% must be paid in cash."
    else:
        max_itc_allowed = output_tax_liability
        min_cash_payable = 0.0
        message = "Rule 86B Not Applicable (Monthly turnover <= ₹50L). 100% ITC can be used."

    return {
        "is_rule_86b_applicable": is_applicable,
        "monthly_taxable_turnover": round(monthly_taxable_turnover, 2),
        "total_output_tax": round(output_tax_liability, 2),
        "max_itc_usable_99pct": max_itc_allowed,
        "min_mandatory_cash_1pct": min_cash_payable,
        "compliance_advice": message
    }


def reconcile_gstr2b_purchase_register(
    purchase_register: List[Dict[str, Any]],
    gstr2b_records: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    CA-Grade GSTR-2B vs Purchase Register Matcher.
    Categorizes invoices into:
    1. Matched Invoices (100% ITC Claimable)
    2. Missing in GSTR-2B (ITC cannot be claimed this month)
    3. Tax Mismatches (Discrepancy flagged for supplier follow-up)
    4. Blocked ITC under Section 17(5)
    """
    matched = []
    missing_in_2b = []
    tax_mismatches = []
    blocked_itc = []

    # Map 2B by invoice number
    gstr2b_map = {str(item.get("invoice_no", "")).strip().upper(): item for item in gstr2b_records}

    total_purchase_itc = 0.0
    total_eligible_2b_itc = 0.0
    total_blocked_itc = 0.0

    for p_inv in purchase_register:
        inv_no = str(p_inv.get("invoice_no", "")).strip().upper()
        p_tax = float(p_inv.get("tax_amount", 0.0))
        category = str(p_inv.get("category", ""))
        total_purchase_itc += p_tax

        # Check Section 17(5) Blocked Credit
        blocked_check = check_blocked_credit_sec17_5(category)
        if blocked_check["is_blocked"]:
            blocked_itc.append({
                **p_inv,
                "reason": blocked_check["audit_note"]
            })
            total_blocked_itc += p_tax
            continue

        if inv_no in gstr2b_map:
            two_b_inv = gstr2b_map[inv_no]
            two_b_tax = float(two_b_inv.get("tax_amount", 0.0))
            if abs(p_tax - two_b_tax) < 1.0:  # Matching within ₹1 tolerance
                matched.append(p_inv)
                total_eligible_2b_itc += p_tax
            else:
                tax_mismatches.append({
                    "purchase_invoice": p_inv,
                    "gstr2b_invoice": two_b_inv,
                    "difference": round(p_tax - two_b_tax, 2)
                })
        else:
            missing_in_2b.append(p_inv)

    return {
        "total_invoices_audited": len(purchase_register),
        "matched_count": len(matched),
        "missing_in_2b_count": len(missing_in_2b),
        "tax_mismatches_count": len(tax_mismatches),
        "blocked_itc_count": len(blocked_itc),
        "total_purchase_itc": round(total_purchase_itc, 2),
        "total_eligible_itc_to_claim": round(total_eligible_2b_itc, 2),
        "total_blocked_itc": round(total_blocked_itc, 2),
        "matched_invoices": matched,
        "missing_in_2b_invoices": missing_in_2b,
        "tax_mismatches": tax_mismatches,
        "blocked_invoices": blocked_itc
    }
