from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)
from finai.presentation.theme.styles import PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY


class CommandPaletteDialog(QDialog):
    """
    Pro-App Command Palette (Ctrl+Shift+P) Modal Overlay.
    Enables instant keyboard search and direct navigation to any page or tool.
    Clean vector design - zero OS emojis.
    """

    action_selected = Signal(int)  # Page index signal

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type a command or page (e.g. 'gst', 'scan', 'budget', 'reports')...")
        self.search_input.setStyleSheet(
            f"background: #FFFFFF; color: {TEXT_PRIMARY}; border: 2px solid {PRIMARY}; border-radius: 10px; padding: 10px 14px; font-size: 14px;"
        )
        self.search_input.textChanged.connect(self.filter_commands)
        self.search_input.returnPressed.connect(self.trigger_selected)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(
            f"""
            QListWidget {{
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                color: {TEXT_PRIMARY};
                font-size: 14px;
            }}
            QListWidget::item {{
                padding: 10px 14px;
                border-bottom: 1px solid #F1F5F9;
            }}
            QListWidget::item:selected {{
                background: #EFF6FF;
                color: {PRIMARY};
                font-weight: 600;
                border-radius: 8px;
            }}
            """
        )
        self.list_widget.itemDoubleClicked.connect(self.trigger_item)

        layout.addWidget(self.search_input)
        layout.addWidget(self.list_widget)

        self.commands = [
            ("Dashboard Overview", 0),
            ("Ask FinAI Offline Co-Pilot", 1),
            ("Calculate GST (Forward & Reverse)", 2),
            ("Scan Receipt (OCR & Input Tax Credit)", 3),
            ("Budget Planner & What-If Simulator", 4),
            ("Expense Tracker & Virtualized Table", 5),
            ("Investment Planner (FD, SIP, PPF)", 6),
            ("Business Advisor & KPI Insights", 7),
            ("Generate Financial Audit PDF Report", 8),
            ("Global Full-Text Search (FTS5)", 9),
            ("Knowledge Base & Financial Articles", 10),
            ("Past History Audit Trail", 11),
            ("Settings & Encrypted Backup / Restore", 12),
            ("About FinAI & Privacy Architecture", 13),
        ]

        self.populate_list(self.commands)

    def populate_list(self, items):
        self.list_widget.clear()
        for title, idx in items:
            item = QListWidgetItem(title)
            item.setData(Qt.UserRole, idx)
            self.list_widget.addItem(item)
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def filter_commands(self, text: str):
        query = text.lower().strip()
        filtered = [cmd for cmd in self.commands if query in cmd[0].lower()]
        self.populate_list(filtered)

    def trigger_selected(self):
        curr = self.list_widget.currentItem()
        if curr:
            self.trigger_item(curr)

    def trigger_item(self, item: QListWidgetItem):
        page_idx = item.data(Qt.UserRole)
        self.action_selected.emit(page_idx)
        self.accept()
