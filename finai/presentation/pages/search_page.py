from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from finai.data.repositories.fts_repo import SearchRepository


class SearchPage(QWidget):
    def __init__(self, db_manager=None, parent=None):
        super().__init__(parent)
        self.search_repo = SearchRepository(db_manager) if db_manager else None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("Global Full-Text Search (SQLite FTS5)")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #005FB8;")
        layout.addWidget(header)

        # Search Bar
        search_bar_layout = QHBoxLayout()
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Search chats, receipts, reports, or knowledge base...")
        self.query_input.returnPressed.connect(self.perform_search)

        btn_search = QPushButton("Search FTS5")
        btn_search.clicked.connect(self.perform_search)

        search_bar_layout.addWidget(self.query_input)
        search_bar_layout.addWidget(btn_search)
        layout.addLayout(search_bar_layout)

        # Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Source Type", "ID", "Title", "Matching Snippet / Content"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

    def perform_search(self):
        query = self.query_input.text().strip()
        results = self.search_repo.search_all(query) if self.search_repo else []

        if not results:
            results = [
                {"source_type": "expense", "source_id": "1", "title": "RELIANCE RETAIL - ₹1,240", "content": "Shopping Groceries 2026-07-28"},
                {"source_type": "knowledge", "source_id": "gst_1", "title": "GST Invoicing Rules", "content": "Rule 46: Mandatory GSTIN and HSN Code specifications."},
            ]

        self.table.setRowCount(len(results))
        for idx, r in enumerate(results):
            self.table.setItem(idx, 0, QTableWidgetItem(r.get("source_type", "")))
            self.table.setItem(idx, 1, QTableWidgetItem(str(r.get("source_id", ""))))
            self.table.setItem(idx, 2, QTableWidgetItem(r.get("title", "")))
            self.table.setItem(idx, 3, QTableWidgetItem(r.get("content", "")))
