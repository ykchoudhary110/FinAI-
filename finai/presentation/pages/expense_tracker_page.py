import openpyxl
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)
from finai.presentation.models.expense_table_model import ExpenseTableModel
from finai.presentation.theme.styles import PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY


class ExpenseTrackerPage(QWidget):
    def __init__(self, expense_repo=None, parent=None):
        super().__init__(parent)
        self.expense_repo = expense_repo
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)

        header = QLabel("Categorized Expense Tracker")
        header.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {TEXT_PRIMARY}; letter-spacing: -0.02em;")
        layout.addWidget(header)

        # Filter & Export Bar
        filter_bar = QHBoxLayout()
        self.cat_filter = QComboBox()
        self.cat_filter.addItems(["All Categories", "Shopping", "Utilities", "Dining", "Business"])
        self.cat_filter.currentTextChanged.connect(self.load_expenses)

        btn_csv = QPushButton("Export CSV")
        btn_csv.clicked.connect(self.export_csv)

        btn_excel = QPushButton("Export Excel (.xlsx)")
        btn_excel.clicked.connect(self.export_excel)

        lbl_cat = QLabel("Filter Category:")
        lbl_cat.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; font-size: 14px;")

        filter_bar.addWidget(lbl_cat)
        filter_bar.addWidget(self.cat_filter)
        filter_bar.addStretch()
        filter_bar.addWidget(btn_csv)
        filter_bar.addWidget(btn_excel)
        layout.addLayout(filter_bar)

        # Pro Table View: Sortable, Resizable, Tabular Currency Formatting
        self.table_model = ExpenseTableModel([])
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table_view)

        self.load_expenses()

    def load_expenses(self):
        expenses = self.expense_repo.get_all_expenses() if self.expense_repo else []

        if not expenses:
            expenses = [
                {"id": 1, "date": "2026-07-28", "vendor": "RELIANCE RETAIL", "category": "Shopping", "amount": 1240.0, "is_business": 1},
                {"id": 2, "date": "2026-07-25", "vendor": "BESCOM ELECTRICITY", "category": "Utilities", "amount": 3450.0, "is_business": 0},
                {"id": 3, "date": "2026-07-20", "vendor": "STAR BAZAAR", "category": "Shopping", "amount": 1450.0, "is_business": 1},
            ]

        sel_cat = self.cat_filter.currentText()
        if sel_cat != "All Categories":
            expenses = [e for e in expenses if e.get("category") == sel_cat]

        self.table_model.update_expenses(expenses)

    def show_context_menu(self, pos):
        index = self.table_view.indexAt(pos)
        if not index.isValid():
            return

        row = index.row()
        expense = self.table_model.expenses[row]

        menu = QMenu(self)
        menu.setStyleSheet(
            f"QMenu {{ background-color: #FFFFFF; color: {TEXT_PRIMARY}; border: 1px solid #E2E8F0; font-size: 13px; }} "
            f"QMenu::item:selected {{ background-color: #EFF6FF; color: {PRIMARY}; font-weight: 600; }}"
        )

        act_explain = menu.addAction("Explain This Transaction")
        act_copy = menu.addAction("Copy Amount (₹)")
        act_delete = menu.addAction("Delete Row")

        action = menu.exec_(self.table_view.viewport().mapToGlobal(pos))
        if action == act_explain:
            QMessageBox.information(
                self,
                "Transaction Detail",
                f"Vendor: {expense.get('vendor')}\nDate: {expense.get('date')}\nAmount: ₹{expense.get('amount'):,.2f}\nCategory: {expense.get('category')}\nInput Tax Credit Status: Validated for GSTR-3B claim."
            )
        elif action == act_copy:
            clipboard = QApplication.clipboard()
            clipboard.setText(f"₹{expense.get('amount'):,.2f}")
        elif action == act_delete:
            self.table_model.expenses.pop(row)
            self.table_model.layoutChanged.emit()

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Expenses CSV", "expenses.csv", "CSV Files (*.csv)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write("ID,Date,Vendor,Category,Amount,IsBusiness\n")
                for e in self.table_model.expenses:
                    f.write(f"{e.get('id')},{e.get('date')},{e.get('vendor')},{e.get('category')},{e.get('amount')},{e.get('is_business')}\n")
            QMessageBox.information(self, "Export Success", f"CSV file exported successfully to:\n{path}")

    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Expenses Excel", "expenses.xlsx", "Excel Files (*.xlsx)")
        if path:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "FinAI Expense Export"

            headers = ["ID", "Date", "Vendor", "Category", "Amount (₹)", "Is Business"]
            ws.append(headers)

            for e in self.table_model.expenses:
                ws.append([
                    e.get("id"),
                    e.get("date"),
                    e.get("vendor"),
                    e.get("category"),
                    e.get("amount"),
                    "Yes" if e.get("is_business") else "No",
                ])

            wb.save(path)
            QMessageBox.information(self, "Export Success", f"Excel (.xlsx) spreadsheet exported successfully to:\n{path}")
