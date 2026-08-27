from typing import Any, List
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class ExpenseTableModel(QAbstractTableModel):
    """
    Virtualized QAbstractTableModel for sub-millisecond rendering of expense transaction lists.
    Prevents Qt GUI thread freezing when handling thousands of rows.
    """

    def __init__(self, expenses: List[dict] = None, parent=None):
        super().__init__(parent)
        self.headers = ["ID", "Date", "Vendor", "Category", "Amount (₹)", "Business"]
        self.expenses = expenses or []

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.expenses)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.headers)

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

    def data(self, index: QModelIndex, role=Qt.DisplayRole) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self.expenses)):
            return None

        row_data = self.expenses[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return str(row_data.get("id", ""))
            elif col == 1:
                return str(row_data.get("date", ""))
            elif col == 2:
                return str(row_data.get("vendor", ""))
            elif col == 3:
                return str(row_data.get("category", ""))
            elif col == 4:
                return f"₹{row_data.get('amount', 0.0):,.2f}"
            elif col == 5:
                return "Yes" if row_data.get("is_business") else "No"

        elif role == Qt.TextAlignmentRole:
            if col in (0, 4):
                return int(Qt.AlignRight | Qt.AlignVCenter)
            return int(Qt.AlignLeft | Qt.AlignVCenter)

        return None

    def update_expenses(self, new_expenses: List[dict]):
        self.beginResetModel()
        self.expenses = new_expenses
        self.endResetModel()
