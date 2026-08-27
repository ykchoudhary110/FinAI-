from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class HistoryPage(QWidget):
    def __init__(self, db_manager=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("History & Audit Trail")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #005FB8;")
        layout.addWidget(header)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Module / Activity", "Formula / Context", "Summary Output"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.load_history()

    def load_history(self):
        history = [
            {"timestamp": "2026-07-29 19:50", "activity": "Income Tax Calculation", "formula": "tax_rules.v1 (FY 2025-26)", "output": "Tax Payable: ₹0 (Rebate ₹60k applied)"},
            {"timestamp": "2026-07-29 18:30", "activity": "GST Forward Calculation", "formula": "gst_rules.v1 (18%)", "output": "Total Amount: ₹1,180.00"},
            {"timestamp": "2026-07-28 14:15", "activity": "Receipt OCR Scan", "formula": "receipt_parser.v1", "output": "RELIANCE RETAIL (₹1,240.00)"},
        ]
        self.table.setRowCount(len(history))
        for r, h in enumerate(history):
            self.table.setItem(r, 0, QTableWidgetItem(h["timestamp"]))
            self.table.setItem(r, 1, QTableWidgetItem(h["activity"]))
            self.table.setItem(r, 2, QTableWidgetItem(h["formula"]))
            self.table.setItem(r, 3, QTableWidgetItem(h["output"]))
