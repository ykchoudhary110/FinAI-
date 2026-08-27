from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class SpendForecastResult:
    predicted_next_month_spend: float
    slope: float
    intercept: float
    trend_direction: str  # "Increasing", "Decreasing", "Stable"
    confidence_description: str


def predict_next_month_spend(monthly_expenses: List[float]) -> SpendForecastResult:
    """
    Deterministic next-month spend forecast using Ordinary Least Squares (OLS) Linear Regression.
    Rule-engine tier (100% deterministic, explainable mathematical projection).
    """
    if not monthly_expenses:
        return SpendForecastResult(0.0, 0.0, 0.0, "Stable", "No historical expense data available")

    if len(monthly_expenses) == 1:
        return SpendForecastResult(
            monthly_expenses[0],
            0.0,
            monthly_expenses[0],
            "Stable",
            "Single data point projection"
        )

    n = len(monthly_expenses)
    x = list(range(1, n + 1))
    y = monthly_expenses

    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi ** 2 for xi in x)

    denominator = (n * sum_x2) - (sum_x ** 2)
    if denominator == 0:
        slope = 0.0
    else:
        slope = ((n * sum_xy) - (sum_x * sum_y)) / denominator

    intercept = (sum_y - (slope * sum_x)) / n

    next_x = n + 1
    predicted = max(0.0, (slope * next_x) + intercept)

    if slope > 500:
        trend = "Increasing"
    elif slope < -500:
        trend = "Decreasing"
    else:
        trend = "Stable"

    return SpendForecastResult(
        predicted_next_month_spend=round(predicted, 2),
        slope=round(slope, 2),
        intercept=round(intercept, 2),
        trend_direction=trend,
        confidence_description=f"Linear Regression OLS over {n} months (Slope: {slope:+.2f}/mo)"
    )
