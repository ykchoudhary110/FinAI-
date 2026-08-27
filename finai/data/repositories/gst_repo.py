from typing import Dict, List
from finai.data.db import DatabaseManager


class GstRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def add_itc_record(
        self,
        expense_id: int,
        vendor_gstin: str,
        invoice_number: str,
        invoice_date: str,
        taxable_value: float,
        cgst: float,
        sgst: float,
        igst: float,
        total_gst: float,
        itc_claimed: bool = True,
    ) -> int:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO gst_records (expense_id, vendor_gstin, invoice_number, invoice_date, taxable_value, cgst, sgst, igst, total_gst, itc_claimed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                expense_id,
                vendor_gstin,
                invoice_number,
                invoice_date,
                taxable_value,
                cgst,
                sgst,
                igst,
                total_gst,
                1 if itc_claimed else 0,
            ),
        )
        rec_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return rec_id

    def get_all_itc_records((self) -> List[Dict]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gst_records ORDER BY invoice_date DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_total_itc_claimed(self) -> float:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total_gst) FROM gst_records WHERE itc_claimed = 1")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row[0] is not None else 0.0
