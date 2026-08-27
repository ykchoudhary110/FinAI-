from typing import Dict, List
from finai.data.db import DatabaseManager


class BudgetRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def set_budget(self, category: str, monthly_limit: float):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO budgets (category, monthly_limit)
            VALUES (?, ?)
            ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit
            """,
            (category, monthly_limit),
        )
        conn.commit()
        conn.close()

    def get_all_budgets(self) -> Dict[str, float]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT category, monthly_limit FROM budgets")
        rows = cursor.fetchall()
        conn.close()
        return {r["category"]: r["monthly_limit"] for r in rows}
