from typing import Dict, List, Tuple
from finai.domain.models.financial_models import (
    DepreciationResult,
    InvestmentProjectionRow,
    InvestmentResult,
)


def calculate_simple_interest(principal: float, rate_percent: float, time_years: float) -> Dict[str, float]:
    if principal < 0 or rate_percent < 0 or time_years < 0:
        raise ValueError("Inputs cannot be negative.")
    interest = round((principal * rate_percent * time_years) / 100.0, 2)
    return {
        "principal": round(principal, 2),
        "rate_percent": rate_percent,
        "time_years": time_years,
        "interest": interest,
        "total_amount": round(principal + interest, 2),
    }


def calculate_compound_interest(
    principal: float, rate_percent: float, time_years: float, compounding_frequency: int = 1
) -> Dict[str, float]:
    """
    compounding_frequency: 1 = Annual, 2 = Half-yearly, 4 = Quarterly, 12 = Monthly
    """
    if principal < 0 or rate_percent < 0 or time_years < 0 or compounding_frequency < 1:
        raise ValueError("Invalid inputs for compound interest.")
    
    n = compounding_frequency
    r = rate_percent / 100.0
    amount = round(principal * ((1.0 + (r / n)) ** (n * time_years)), 2)
    interest = round(amount - principal, 2)
    
    return {
        "principal": round(principal, 2),
        "rate_percent": rate_percent,
        "time_years": time_years,
        "compounding_frequency": compounding_frequency,
        "interest": interest,
        "total_amount": amount,
    }


def calculate_depreciation(
    asset_cost: float,
    salvage_value: float,
    useful_life_years: int,
    rate_percent: float = 0.0,
    is_wdv: bool = False,
) -> DepreciationResult:
    if asset_cost <= 0 or salvage_value < 0 or useful_life_years <= 0:
        raise ValueError("Invalid asset depreciation parameters.")

    annual_dep: List[float] = []
    book_vals: List[float] = []
    current_val = asset_cost

    if not is_wdv:
        # Straight Line Method (SLM)
        dep_amount = round((asset_cost - salvage_value) / useful_life_years, 2)
        effective_rate = round((dep_amount / asset_cost) * 100.0, 2)
        for year in range(1, useful_life_years + 1):
            current_val = max(salvage_value, round(current_val - dep_amount, 2))
            annual_dep.append(dep_amount)
            book_vals.append(current_val)
        return DepreciationResult(
            method="straight_line",
            asset_cost=round(asset_cost, 2),
            salvage_value=round(salvage_value, 2),
            useful_life_years=useful_life_years,
            rate_percent=effective_rate,
            annual_depreciation=annual_dep,
            book_values=book_vals,
        )
    else:
        # Written Down Value Method (WDV)
        wdv_rate = rate_percent / 100.0 if rate_percent > 0 else 0.15
        for year in range(1, useful_life_years + 1):
            dep_amount = round(current_val * wdv_rate, 2)
            current_val = max(0.0, round(current_val - dep_amount, 2))
            annual_dep.append(dep_amount)
            book_vals.append(current_val)
        return DepreciationResult(
            method="written_down_value",
            asset_cost=round(asset_cost, 2),
            salvage_value=round(salvage_value, 2),
            useful_life_years=useful_life_years,
            rate_percent=rate_percent if rate_percent > 0 else 15.0,
            annual_depreciation=annual_dep,
            book_values=book_vals,
        )


def calculate_investment_sip(
    monthly_investment: float, annual_rate: float, tenure_years: int
) -> InvestmentResult:
    """
    SIP (Systematic Investment Plan) Future Value Formula:
    FV = P * [ ((1+i)^n - 1) / i ] * (1+i)
    """
    if monthly_investment <= 0 or annual_rate < 0 or tenure_years <= 0:
        raise ValueError("Invalid SIP parameters.")

    i = (annual_rate / 100.0) / 12.0
    n = tenure_years * 12
    
    if i == 0:
        final_corpus = monthly_investment * n
    else:
        final_corpus = monthly_investment * (((1 + i) ** n - 1) / i) * (1 + i)

    final_corpus = round(final_corpus, 2)
    total_invested = round(monthly_investment * n, 2)
    estimated_returns = round(final_corpus - total_invested, 2)

    breakdown: List[InvestmentProjectionRow] = []
    accumulated_invested = 0.0

    for yr in range(1, tenure_years + 1):
        accumulated_invested += monthly_investment * 12
        months_elapsed = yr * 12
        if i == 0:
            yr_corpus = accumulated_invested
        else:
            yr_corpus = monthly_investment * (((1 + i) ** months_elapsed - 1) / i) * (1 + i)
        breakdown.append(
            InvestmentProjectionRow(
                year=yr,
                invested_amount=round(accumulated_invested, 2),
                estimated_returns=round(yr_corpus - accumulated_invested, 2),
                total_value=round(yr_corpus, 2),
            )
        )

    return InvestmentResult(
        tool_type="SIP",
        principal_or_monthly=monthly_investment,
        annual_rate=annual_rate,
        tenure_years=tenure_years,
        total_invested=total_invested,
        estimated_returns=max(0.0, estimated_returns),
        final_corpus=final_corpus,
        breakdown=breakdown,
    )
