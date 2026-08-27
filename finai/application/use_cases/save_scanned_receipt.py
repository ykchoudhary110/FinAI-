from datetime import datetime
from typing import Dict, Optional
from finai.data.db import DatabaseManager
from finai.data.repositories.expense_repo import ExpenseRepository
from finai.data.repositories.gst_repo import GstRepository
from finai.domain.rules.gst_rules import calculate_gst_forward
from finai.domain.rules.health_score_rules import calculate_financial_health_score


class SaveScannedReceiptUseCase:
    """
    Implements Section 5.1 & Requirement 2 End-to-End Interconnection Flow:
    Receipt Scan -> Expense Tracker -> Vendor Mapping -> GST ITC Tracking -> Health Score Recalculation.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.expense_repo = ExpenseRepository(db_manager)
        self.gst_repo = GstRepository(db_manager)

    def execute(
        self,
        vendor: str,
        date_str: str,
        total_amount: float,
        category: str = "General Business",
        gstin: Optional[str] = None,
        is_business: bool = False,
        confidence_score: float = 1.0,
    ) -> Dict:
        # 1. Create Expense Entry
        gst_split = calculate_gst_forward(total_amount / 1.18, 18.0) if is_business else None
        gst_amt = gst_split.gst_amount if gst_split else 0.0

        expense_id = self.expense_repo.add_expense(
            date_str=date_str,
            vendor=vendor,
            category=category,
            amount=total_amount,
            gst_amount=gst_amt,
            is_business=is_business,
            notes=f"Auto-populated from receipt scan (GSTIN: {gstin or 'N/A'})",
            confidence_score=confidence_score,
        )

        # 2. Upsert Vendor -> Category Mapping
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO vendor_category_map (vendor_keyword, category)
            VALUES (?, ?)
            ON CONFLICT(vendor_keyword) DO UPDATE SET category = excluded.category, updated_at = CURRENT_TIMESTAMP
            """,
            (vendor.lower().strip(), category),
        )

        # 3. Create GST ITC Record if business-related
        itc_record_id = None
        if is_business and gst_split:
            itc_record_id = self.gst_repo.add_itc_record(
                expense_id=expense_id,
                vendor_gstin=gstin or "UNREGISTERED",
                invoice_number=f"INV-{expense_id:04d}",
                invoice_date=date_str,
                taxable_value=gst_split.base_amount,
                cgst=gst_split.cgst_amount,
                sgst=gst_split.sgst_amount,
                igst=gst_split.igst_amount,
                total_gst=gst_split.gst_amount,
                itc_claimed=True,
            )

        # 4. Re-calculate Financial Health Score & record history
        ym = datetime.now().strftime("%Y-%m")
        monthly_exp = self.expense_repo.get_monthly_total(ym)
        health_score = calculate_financial_health_score(
            income=100000.0,
            expenses=monthly_exp,
            budget_adherence_percent=90.0,
            punctuality_percent=100.0,
            total_monthly_emi=15000.0,
        )

        cursor.execute(
            """
            INSERT INTO health_score_history (date, score, savings_score, budget_score, punctuality_score, dti_score, gst_score, lowest_factor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                date_str,
                health_score.total_score,
                health_score.savings_rate_score,
                health_score.budget_adherence_score,
                health_score.payment_punctuality_score,
                health_score.debt_to_income_score,
                health_score.gst_compliance_score,
                health_score.lowest_scoring_factor,
            ),
        )
        conn.commit()
        conn.close()

        return {
            "expense_id": expense_id,
            "itc_record_id": itc_record_id,
            "health_score": health_score.total_score,
            "status": "success",
        }
