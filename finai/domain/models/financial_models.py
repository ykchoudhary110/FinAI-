from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TaxRegime(str, Enum):
    NEW = "new"
    OLD = "old"


class TaxpayerCategory(str, Enum):
    INDIVIDUAL = "individual"
    SENIOR = "senior"  # 60 to 80 yrs
    SUPER_SENIOR = "super_senior"  # > 80 yrs


class GstSplit(BaseModel):
    is_interstate: bool = False
    base_amount: float
    gst_rate: float
    gst_amount: float
    total_amount: float
    cgst_rate: float = 0.0
    cgst_amount: float = 0.0
    sgst_rate: float = 0.0
    sgst_amount: float = 0.0
    igst_rate: float = 0.0
    igst_amount: float = 0.0


class TaxSlabBreakdown(BaseModel):
    slab_label: str
    taxable_in_slab: float
    rate_percent: float
    tax_amount: float


class TaxCalculationResult(BaseModel):
    assessment_year: str = "2026-27"
    financial_year: str = "2025-26"
    regime: TaxRegime
    gross_income: float
    standard_deduction: float
    other_deductions: float = 0.0  # 80C, 80D etc (Old regime)
    taxable_income: float
    slab_tax: float
    slab_breakdown: List[TaxSlabBreakdown]
    section_87a_rebate: float
    tax_after_rebate: float
    surcharge: float
    marginal_relief: float = 0.0
    cess: float  # 4% Health & Education Cess
    total_tax_payable: float
    effective_tax_rate: float


class EmiAmortizationRow(BaseModel):
    month: int
    opening_balance: float
    emi: float
    principal_paid: float
    interest_paid: float
    closing_balance: float


class EmiCalculationResult(BaseModel):
    principal: float
    annual_rate: float
    tenure_months: int
    monthly_emi: float
    total_interest: float
    total_payment: float
    amortization_schedule: List[EmiAmortizationRow]


class DepreciationResult(BaseModel):
    method: str  # "straight_line" or "written_down_value"
    asset_cost: float
    salvage_value: float
    useful_life_years: int
    rate_percent: float
    annual_depreciation: List[float]
    book_values: List[float]


class InvestmentProjectionRow(BaseModel):
    year: int
    invested_amount: float
    estimated_returns: float
    total_value: float


class InvestmentResult(BaseModel):
    tool_type: str  # FD, RD, SIP, PPF, NPS
    principal_or_monthly: float
    annual_rate: float
    tenure_years: int
    total_invested: float
    estimated_returns: float
    final_corpus: float
    breakdown: List[InvestmentProjectionRow]


class ReceiptLineItem(BaseModel):
    description: str
    amount: float
    confidence: float = 1.0


class ParsedReceipt(BaseModel):
    vendor_name: str
    receipt_date: Optional[str] = None
    total_amount: float
    gstin: Optional[str] = None
    gst_amount: Optional[float] = None
    line_items: List[ReceiptLineItem] = Field(default_factory=list)
    confidence_score: float = 1.0
    is_low_confidence: bool = False


class HealthScoreBreakdown(BaseModel):
    total_score: int  # 0 to 100
    savings_rate_score: float  # max 30
    budget_adherence_score: float  # max 25
    payment_punctuality_score: float  # max 20
    debt_to_income_score: float  # max 15
    gst_compliance_score: float  # max 10
    lowest_scoring_factor: str
    ai_suggestion: str = ""
