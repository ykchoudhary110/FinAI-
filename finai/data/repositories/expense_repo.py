import sqlite3
from typing import Dict, List, Optional
from finai.data.db import DatabaseManager


class ExpenseRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def add_expense(
        self,
        date_str: str,
        vendor: str,
        category: str,
        amount: float,
        gst_amount: float = 0.0,
        is_business: bool = False,
        notes: Optional[str] = None,
        receipt_image_path: Optional[str] = None,
        confidence_score: float = 1.0,
    ) -> int:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO expenses (date, vendor, category, amount, gst_amount, is_business, notes, receipt_image_path, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                date_str,
                vendor,
                category,
                amount,
                gst_amount,
                1 if is_business else 0,
                notes,
                receipt_image_path,
                confidence_score,
            ),
        )
        expense_id = cursor.lastrowid

        # Update FTS5 index
        cursor.execute(
            """
            INSERT INTO search_index (source_type, source_id, title, content)
            VALUES ('expense', ?, ?, ?)
            """,
            (str(expense_id), f"{vendor} - ₹{amount}", f"{category} {notes or ''} {date_str}"),
        )

        conn.commit()
        conn.close()
        return expense_id

    def get_all_expenses(self, limit: int = 100) -> List[Dict]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM expenses ORDER BY date DESC, id DESC LIMIT ?", (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_monthly_total(self, year_month: str) -> float:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT SUM(amount) FROM expenses WHERE date LIKE ?", (f"{year_month}%",)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row[0] is not None else 0.0

    def get_spend_by_category(self, year_month: str) -> Dict[str, float]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE date LIKE ?
            GROUP BY category
            """,
            (f"{year_month}%",),
        )
        rows = cursor.fetchall()
        conn.close()
        return {r["category"]: r["total"] for r in rows}
