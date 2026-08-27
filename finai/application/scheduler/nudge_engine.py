from datetime import datetime, timedelta
from typing import Dict, List
from apscheduler.schedulers.background import BackgroundScheduler
from finai.data.db import DatabaseManager


class NudgeEngine:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.scheduler = BackgroundScheduler()

    def start(self):
        if not self.scheduler.running:
            self.scheduler.add_job(self.check_all_nudges, "interval", hours=24)
            self.scheduler.start()
        # Run immediate check on app launch
        self.check_all_nudges()

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()

    def check_all_nudges(self):
        """Evaluates rule-based triggers and creates pending nudges."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        today = datetime.now()

        # 1. GST Filing Due Date (GSTR-3B is 20th of every month, lead time 5 days)
        gst_due = today.replace(day=20) if today.day <= 20 else (today + timedelta(days=30)).replace(day=20)
        days_until_gst = (gst_due - today).days
        if 0 <= days_until_gst <= 5:
            self._create_nudge(
                cursor,
                trigger_type="gst_due",
                title="GST Filing Reminder",
                message=f"GSTR-3B filing due date is approaching on {gst_due.strftime('%d %b %Y')} ({days_until_gst} days left).",
                due_date=gst_due.strftime("%Y-%m-%d"),
            )

        # 2. Budget Overshoot Check (> 90% threshold)
        cursor.execute("SELECT category, monthly_limit FROM budgets")
        budgets = cursor.fetchall()
        ym = today.strftime("%Y-%m")

        for b in budgets:
            category = b["category"]
            cap = b["monthly_limit"]
            cursor.execute(
                "SELECT SUM(amount) FROM expenses WHERE category = ? AND date LIKE ?",
                (category, f"{ym}%"),
            )
            spend_row = cursor.fetchone()
            spend = spend_row[0] if spend_row and spend_row[0] else 0.0

            if cap > 0 and (spend / cap) >= 0.90:
                self._create_nudge(
                    cursor,
                    trigger_type="budget_overshoot",
                    title="Budget Alert",
                    message=f"Category '{category}' has reached {int((spend/cap)*100)}% of monthly cap (₹{spend:,.0f} / ₹{cap:,.0f}).",
                    due_date=today.strftime("%Y-%m-%d"),
                )

        conn.commit()
        conn.close()

    def _create_nudge(self, cursor, trigger_type: str, title: str, message: str, due_date: str):
        cursor.execute(
            """
            SELECT id FROM nudges WHERE trigger_type = ? AND due_date = ? AND is_dismissed = 0
            """,
            (trigger_type, due_date),
        )
        if not cursor.fetchone():
            cursor.execute(
                """
                INSERT INTO nudges (trigger_type, title, message, due_date)
                VALUES (?, ?, ?, ?)
                """,
                (trigger_type, title, message, due_date),
            )

    def get_active_nudges(self) -> List[Dict]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM nudges WHERE is_dismissed = 0 ORDER BY created_at DESC"
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def dismiss_nudge(self, nudge_id: int):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE nudges SET is_dismissed = 1 WHERE id = ?", (nudge_id,))
        conn.commit()
        conn.close()
