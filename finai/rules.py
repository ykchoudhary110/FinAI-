from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP


def money(value: float | Decimal) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def gst(base_amount: float, rate: float, interstate: bool) -> dict:
    base = money(base_amount)
    gst_amount = money(Decimal(str(base)) * Decimal(str(rate)) / Decimal("100"))
    return {
        "taxable_value": base,
        "rate": rate,
        "gst_amount": gst_amount,
        "cgst": 0.0 if interstate else money(Decimal(str(gst_amount)) / Decimal("2")),
        "sgst": 0.0 if interstate else money(Decimal(str(gst_amount)) / Decimal("2")),
        "igst": gst_amount if interstate else 0.0,
        "invoice_total": money(Decimal(str(base)) + Decimal(str(gst_amount))),
    }


def _slab_tax(income: float, slabs: list[tuple[float, float]]) -> float:
    inc = Decimal(str(income))
    lower = Decimal("0")
    total = Decimal("0")
    for upper, rate in slabs:
        upper_d = Decimal(str(upper)) if upper != float("inf") else Decimal("99999999999")
        if inc > lower:
            taxable_chunk = min(inc, upper_d) - lower
            total += taxable_chunk * Decimal(str(rate))
        lower = upper_d
        if inc <= upper_d:
            break
    return money(total)


def income_tax(gross: float, regime: str, deductions: float = 0, hra: float = 0, home_loan: float = 0) -> dict:
    standard = 75000.0 if regime == "new" else 50000.0
    allowed = standard if regime == "new" else standard + min(deductions, 300000.0) + max(0.0, hra) + min(home_loan, 200000.0)
    taxable = max(0.0, gross - allowed)
    slabs = (
        [(400000, 0), (800000, .05), (1200000, .10), (1600000, .15), (2000000, .20), (2400000, .25), (float("inf"), .30)]
        if regime == "new" else
        [(250000, 0), (500000, .05), (1000000, .20), (float("inf"), .30)]
    )
    slab_tax = _slab_tax(taxable, slabs)
    rebate_limit = 1200000.0 if regime == "new" else 500000.0
    rebate = slab_tax if taxable <= rebate_limit else 0.0
    after_rebate = max(0.0, slab_tax - rebate)
    cess = money(Decimal(str(after_rebate)) * Decimal("0.04"))
    return {
        "regime": regime,
        "gross_income": money(gross),
        "deductions_allowed": money(allowed),
        "taxable_income": money(taxable),
        "slab_tax": slab_tax,
        "rebate": money(rebate),
        "cess": cess,
        "total_tax": money(after_rebate + cess),
    }


def capital_gains(stcg_equity: float = 0, ltcg_equity: float = 0, ltcg_property: float = 0) -> dict:
    stcg_tax = money(Decimal(str(stcg_equity)) * Decimal("0.20"))
    ltcg_eq = max(Decimal("0"), Decimal(str(ltcg_equity)))
    exemption = min(ltcg_eq, Decimal("125000"))
    taxable_ltcg_equity = ltcg_eq - exemption
    ltcg_equity_tax = money(taxable_ltcg_equity * Decimal("0.125"))
    ltcg_property_tax = money(Decimal(str(ltcg_property)) * Decimal("0.125"))
    total_before_cess = money(Decimal(str(stcg_tax)) + Decimal(str(ltcg_equity_tax)) + Decimal(str(ltcg_property_tax)))
    cess = money(Decimal(str(total_before_cess)) * Decimal("0.04"))
    return {
        "stcg_tax": stcg_tax,
        "ltcg_equity_exemption": money(exemption),
        "taxable_ltcg_equity": money(taxable_ltcg_equity),
        "ltcg_equity_tax": ltcg_equity_tax,
        "ltcg_property_tax": ltcg_property_tax,
        "total_before_cess": total_before_cess,
        "cess": cess,
        "total_capital_gains_tax": money(Decimal(str(total_before_cess)) + Decimal(str(cess))),
    }


def emi(principal: float, annual_rate: float, tenure_months: int) -> dict:
    P = Decimal(str(principal))
    r = Decimal(str(annual_rate)) / Decimal("12") / Decimal("100")
    n = Decimal(str(tenure_months))
    if r == 0:
        monthly_emi = P / n if n > 0 else Decimal("0")
    else:
        monthly_emi = P * r * ((Decimal("1") + r) ** n) / (((Decimal("1") + r) ** n) - Decimal("1"))
    total_payment = monthly_emi * n
    total_interest = total_payment - P
    return {
        "principal": money(principal),
        "annual_rate": float(annual_rate),
        "tenure_months": int(tenure_months),
        "monthly_emi": money(monthly_emi),
        "total_interest": money(total_interest),
        "total_payment": money(total_payment),
    }


def hra_exemption(basic_salary: float, hra_received: float, rent_paid: float, is_metro: bool) -> dict:
    actual = Decimal(str(hra_received))
    percent_basic = Decimal(str(basic_salary)) * (Decimal("0.5") if is_metro else Decimal("0.4"))
    rent_minus = max(Decimal("0"), Decimal(str(rent_paid)) - Decimal(str(basic_salary)) * Decimal("0.1"))
    exempt = min(actual, percent_basic, rent_minus)
    taxable = max(Decimal("0"), actual - exempt)
    return {
        "actual_hra": money(actual),
        "percent_of_basic": money(percent_basic),
        "rent_minus_10pct": money(rent_minus),
        "exempt_hra": money(exempt),
        "taxable_hra": money(taxable),
    }


def presumptive_44ada(gross_receipts: float) -> dict:
    gross = Decimal(str(gross_receipts))
    profit = gross * Decimal("0.5")
    return {"gross_receipts": money(gross), "presumptive_rate": 50.0, "taxable_profit": money(profit)}


def presumptive_44ad(digital_turnover: float, cash_turnover: float) -> dict:
    digital = Decimal(str(digital_turnover))
    cash = Decimal(str(cash_turnover))
    dp = digital * Decimal("0.06")
    cp = cash * Decimal("0.08")
    return {
        "digital_turnover": money(digital),
        "cash_turnover": money(cash),
        "digital_profit": money(dp),
        "cash_profit": money(cp),
        "total_profit": money(dp + cp),
    }


def blocked_credit_17_5(category: str) -> dict:
    cat = category.lower()
    if "motor vehicle" in cat or "car" in cat:
        return {"is_blocked": True, "section": "17(5)(a)", "reason": "Motor vehicles — blocked unless used for further supply or transport"}
    if any(w in cat for w in ("food", "catering", "restaurant")):
        return {"is_blocked": True, "section": "17(5)(b)(i)", "reason": "Food, beverages and outdoor catering — blocked"}
    if any(w in cat for w in ("health", "fitness", "club")):
        return {"is_blocked": True, "section": "17(5)(b)(ii)", "reason": "Health/fitness or club membership — blocked"}
    if any(w in cat for w in ("rent-a-cab", "travel", "flight", "ticket")):
        return {"is_blocked": True, "section": "17(5)(b)(iii)", "reason": "Travel including rent-a-cab — blocked unless further supply"}
    if any(w in cat for w in ("insurance", "cosmetic", "beauty", "plastic surgery")):
        return {"is_blocked": True, "section": "17(5)(b)(iv)", "reason": "Personal insurance/cosmetics — blocked"}
    if "gift" in cat or "free sample" in cat:
        return {"is_blocked": True, "section": "17(5)(h)", "reason": "Gifts/free samples exceeding ₹50,000 — blocked"}
    return {"is_blocked": False, "section": "", "reason": "ITC eligible subject to Section 16 conditions"}


def rule_86b_check(monthly_output_tax: float, monthly_cash_paid: float) -> dict:
    output = Decimal(str(monthly_output_tax))
    cash = Decimal(str(monthly_cash_paid))
    min_cash = output * Decimal("0.01")
    return {
        "threshold_exceeded": True,
        "minimum_cash_required": money(min_cash),
        "cash_paid": money(cash),
        "compliant": cash >= min_cash,
    }
