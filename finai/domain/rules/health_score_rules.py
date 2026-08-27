from finai.domain.models.financial_models import HealthScoreBreakdown


def calculate_financial_health_score(
    income: float,
    expenses: float,
    budget_adherence_percent: float,  # 0 to 100%
    punctuality_percent: float,        # 0 to 100%
    total_monthly_emi: float,
    gst_compliance_percent: float = 100.0,  # 0 to 100%
) -> HealthScoreBreakdown:
    """
    Computes transparent Financial Health Score (0-100) based on weighted formula from Section 5.2:
    - Savings rate: 30%
    - Budget adherence: 25%
    - Bill/EMI punctuality: 20%
    - Debt-to-income ratio: 15%
    - GST compliance streak: 10%
    """
    safe_income = max(1.0, income)

    # 1. Savings Rate Score (Max 30)
    savings = max(0.0, safe_income - expenses)
    savings_rate = (savings / safe_income) * 100.0
    # Target savings rate: 30%+ earns full 30 points
    savings_score = min(30.0, (savings_rate / 30.0) * 30.0)

    # 2. Budget Adherence Score (Max 25)
    budget_score = (min(100.0, max(0.0, budget_adherence_percent)) / 100.0) * 25.0

    # 3. Bill/EMI Punctuality Score (Max 20)
    punctuality_score = (min(100.0, max(0.0, punctuality_percent)) / 100.0) * 20.0

    # 4. Debt-to-Income Score (Max 15)
    dti_ratio = (total_monthly_emi / safe_income) * 100.0
    # DTI <= 20% is ideal (15 pts), > 50% gets 0 pts
    if dti_ratio <= 20.0:
        dti_score = 15.0
    elif dti_ratio >= 50.0:
        dti_score = 0.0
    else:
        dti_score = 15.0 * (1.0 - ((dti_ratio - 20.0) / 30.0))

    # 5. GST Compliance Score (Max 10)
    gst_score = (min(100.0, max(0.0, gst_compliance_percent)) / 100.0) * 10.0

    total_score = int(
        round(savings_score + budget_score + punctuality_score + dti_score + gst_score)
    )
    total_score = max(0, min(100, total_score))

    # Identify lowest factor
    factors = [
        ("Savings Rate", (savings_score / 30.0)),
        ("Budget Adherence", (budget_score / 25.0)),
        ("Bill/EMI Punctuality", (punctuality_score / 20.0)),
        ("Debt-to-Income Ratio", (dti_score / 15.0)),
        ("GST Compliance", (gst_score / 10.0)),
    ]
    factors.sort(key=lambda x: x[1])
    lowest_factor = factors[0][0]

    # Generate rule-based suggestion for lowest factor
    suggestions = {
        "Savings Rate": "Try to save at least 20-30% of your income by automating transfers to a separate account on payday.",
        "Budget Adherence": "Set realistic category caps for dining out and shopping to prevent budget overshoots.",
        "Bill/EMI Punctuality": "Enable automatic bill payments or set reminders 3 days before due dates to protect your credit score.",
        "Debt-to-Income Ratio": "Keep total loan EMIs below 30% of monthly income. Consider prepaying high-interest loans first.",
        "GST Compliance": "File monthly GST returns (GSTR-1 and GSTR-3B) on or before due dates to maximize Input Tax Credit.",
    }

    return HealthScoreBreakdown(
        total_score=total_score,
        savings_rate_score=round(savings_score, 1),
        budget_adherence_score=round(budget_score, 1),
        payment_punctuality_score=round(punctuality_score, 1),
        debt_to_income_score=round(dti_score, 1),
        gst_compliance_score=round(gst_score, 1),
        lowest_scoring_factor=lowest_factor,
        ai_suggestion=suggestions.get(lowest_factor, "Maintain consistent financial records."),
    )
