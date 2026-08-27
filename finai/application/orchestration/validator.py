from typing import Any, Dict, Tuple


def validate_rule_output(rule_name: str, result_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Sanity checks specific to domain per Section 4:
    - Tax owed must not exceed taxable income
    - EMI must be positive
    - GST split components must sum to total
    """
    if rule_name == "calculate_income_tax":
        taxable_income = result_data.get("taxable_income", 0.0)
        total_tax = result_data.get("total_tax_payable", 0.0)
        if total_tax > taxable_income:
            return False, "Tax owed exceeds taxable income."

    elif rule_name == "calculate_emi":
        emi = result_data.get("monthly_emi", 0.0)
        if emi <= 0:
            return False, "EMI must be positive."

    elif rule_name == "calculate_gst_forward" or rule_name == "calculate_gst_reverse":
        base = result_data.get("base_amount", 0.0)
        gst = result_data.get("gst_amount", 0.0)
        total = result_data.get("total_amount", 0.0)
        if abs((base + gst) - total) > 0.05:
            return False, "GST split components do not sum to total."

    return True, "Validation clean."
