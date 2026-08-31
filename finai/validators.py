from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def money(value) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def validate_gst(base: float, gst_amount: float, cgst: float, sgst: float, igst: float, total: float, is_interstate: bool) -> dict:
    """
    Verify arithmetic consistency of a GST calculation.
    Returns {"valid": bool, "checks": [str, ...]}
    """
    checks = []
    valid = True
    tolerance = 0.02  # ₹0.02 rounding tolerance
    
    # 1. Non-negative
    for label, value in [("base", base), ("gst_amount", gst_amount), ("cgst", cgst), ("sgst", sgst), ("igst", igst), ("total", total)]:
        if value < 0:
            valid = False
            checks.append(f"FAIL: {label} is negative ({value})")
    if valid:
        checks.append("✓ All amounts non-negative")
    
    # 2. Split reconciliation
    if is_interstate:
        if abs(igst - gst_amount) > tolerance:
            valid = False
            checks.append(f"FAIL: IGST ({igst}) ≠ total GST ({gst_amount})")
        else:
            checks.append(f"✓ IGST reconciled: ₹{igst:,.2f}")
    else:
        split_sum = money(cgst + sgst)
        if abs(split_sum - gst_amount) > tolerance:
            valid = False
            checks.append(f"FAIL: CGST ({cgst}) + SGST ({sgst}) = {split_sum} ≠ total GST ({gst_amount})")
        else:
            checks.append(f"✓ CGST + SGST reconciled: ₹{cgst:,.2f} + ₹{sgst:,.2f} = ₹{gst_amount:,.2f}")
    
    # 3. Invoice total
    expected_total = money(base + gst_amount)
    if abs(total - expected_total) > tolerance:
        valid = False
        checks.append(f"FAIL: base ({base}) + GST ({gst_amount}) = {expected_total} ≠ total ({total})")
    else:
        checks.append(f"✓ Invoice total reconciled: ₹{base:,.2f} + ₹{gst_amount:,.2f} = ₹{total:,.2f}")
    
    return {"valid": valid, "checks": checks}
