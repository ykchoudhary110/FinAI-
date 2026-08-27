from typing import List
from finai.domain.models.financial_models import EmiAmortizationRow, EmiCalculationResult


def calculate_emi(
    principal: float,
    annual_rate: float,
    tenure_months: int,
) -> EmiCalculationResult:
    """
    Computes Loan EMI using standard reducing balance formula and generates month-by-month amortization schedule.
    """
    if principal <= 0:
        raise ValueError("Principal must be positive.")
    if annual_rate < 0:
        raise ValueError("Interest rate cannot be negative.")
    if tenure_months <= 0:
        raise ValueError("Tenure must be at least 1 month.")

    monthly_rate = (annual_rate / 100.0) / 12.0

    if monthly_rate == 0:
        monthly_emi = round(principal / tenure_months, 2)
    else:
        num = monthly_rate * ((1 + monthly_rate) ** tenure_months)
        den = ((1 + monthly_rate) ** tenure_months) - 1
        monthly_emi = round(principal * (num / den), 2)

    total_payment = round(monthly_emi * tenure_months, 2)
    total_interest = round(total_payment - principal, 2)

    schedule: List[EmiAmortizationRow] = []
    current_balance = principal

    for m in range(1, tenure_months + 1):
        interest_paid = round(current_balance * monthly_rate, 2) if monthly_rate > 0 else 0.0
        principal_paid = round(monthly_emi - interest_paid, 2)
        
        # Adjust last month rounding differences
        if m == tenure_months:
            principal_paid = round(current_balance, 2)
            closing_balance = 0.0
        else:
            closing_balance = max(0.0, round(current_balance - principal_paid, 2))

        schedule.append(
            EmiAmortizationRow(
                month=m,
                opening_balance=round(current_balance, 2),
                emi=monthly_emi,
                principal_paid=principal_paid,
                interest_paid=interest_paid,
                closing_balance=closing_balance,
            )
        )
        current_balance = closing_balance

    return EmiCalculationResult(
        principal=round(principal, 2),
        annual_rate=annual_rate,
        tenure_months=tenure_months,
        monthly_emi=monthly_emi,
        total_interest=max(0.0, total_interest),
        total_payment=total_payment,
        amortization_schedule=schedule,
    )
