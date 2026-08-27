from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)
from finai.presentation.theme.styles import PRIMARY, TEXT_MUTED, TEXT_PRIMARY, TEXT_SECONDARY


class AppGuideDialog(QDialog):
    """
    Interactive Step-by-Step App Guide Dialog per User Specification:
    - Displays feature explanation with 'Step X of Y' progress header.
    - Features interactive '< Previous', 'Next >', and 'Close' controls.
    - Triggers navigation to each feature page upon step change.
    """

    def __init__(self, on_navigate=None, parent=None):
        super().__init__(parent)
        self.on_navigate = on_navigate
        self.current_step = 0

        self.setWindowTitle("FinAI App Guide")
        self.resize(500, 260)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.guide_steps = [
            (
                0,
                "1. Financial Dashboard",
                "Welcome to FinAI! The Dashboard displays your Financial Health Score, Ordinary Least Squares (OLS) spend forecast, category spend charts, and live hardware resource monitoring.",
            ),
            (
                3,
                "2. Receipt Scanner (OCR)",
                "Upload or drag & drop paper receipts or invoice PDFs. FinAI automatically extracts merchant names, total amounts, transaction dates, and GSTINs using Tesseract OCR.",
            ),
            (
                5,
                "3. Categorized Expense Tracker",
                "View, search, and track all your financial transactions. You can export formatted Excel (.xlsx) spreadsheets or CSV files anytime for reporting.",
            ),
            (
                2,
                "4. Financial Tools & GST Invoice",
                "Calculate loan EMIs, GST Input Tax Credits (ITC), and generate official B2B tax invoices featuring scannable QR codes.",
            ),
            (
                1,
                "5. Offline RAG AI Co-Pilot",
                "Ask financial or tax questions. FinAI retrieves grounded passages from local offline Knowledge Base guides and cites sources directly.",
            ),
            (
                12,
                "6. Cryptographic Audit Trail",
                "In Settings, run 'Verify Audit Trail Integrity' to recompute the append-only SHA-256 hash chain and guarantee 100% calculation data integrity.",
            ),
        ]

        self.init_ui()
        self.update_step_display()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Outer Glass Card Container
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: rgba(255, 255, 255, 0.98); border: 2px solid #2563EB; border-radius: 16px; }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(10)

        # Header Row: Title & Step Badge
        header_row = QHBoxLayout()
        self.badge_lbl = QLabel("Step 1 of 6")
        self.badge_lbl.setStyleSheet(
            f"background-color: #EFF6FF; color: {PRIMARY}; font-weight: 700; font-size: 12px; border-radius: 6px; padding: 4px 10px; border: 1px solid #BFDBFE;"
        )

        self.title_lbl = QLabel("1. Financial Dashboard")
        self.title_lbl.setStyleSheet("font-size: 17px; font-weight: 700; color: #0F172A;")

        btn_close_x = QPushButton("✕")
        btn_close_x.setFixedSize(28, 28)
        btn_close_x.setStyleSheet(
            "QPushButton { background: transparent; color: #64748B; font-weight: bold; font-size: 14px; border: none; } QPushButton:hover { color: #DC2626; }"
        )
        btn_close_x.clicked.connect(self.accept)

        header_row.addWidget(self.badge_lbl)
        header_row.addSpacing(8)
        header_row.addWidget(self.title_lbl)
        header_row.addStretch()
        header_row.addWidget(btn_close_x)
        card_layout.addLayout(header_row)

        # Body Message Text
        self.msg_lbl = QLabel()
        self.msg_lbl.setWordWrap(True)
        self.msg_lbl.setStyleSheet("font-size: 13px; color: #334155; line-height: 1.4;")
        card_layout.addWidget(self.msg_lbl)
        card_layout.addStretch()

        # Footer Row: Action Buttons
        footer_row = QHBoxLayout()
        footer_row.setSpacing(10)

        self.btn_prev = QPushButton("◄ Previous")
        self.btn_prev.setFixedWidth(110)
        self.btn_prev.setStyleSheet(
            "QPushButton { background-color: #F1F5F9; color: #0F172A; font-weight: 600; font-size: 13px; border-radius: 8px; padding: 6px 12px; border: 1px solid #CBD5E1; } "
            "QPushButton:hover { background-color: #E2E8F0; } "
            "QPushButton:disabled { color: #94A3B8; background-color: #F8FAFC; border-color: #E2E8F0; }"
        )
        self.btn_prev.clicked.connect(self.prev_step)

        self.btn_next = QPushButton("Next ►")
        self.btn_next.setFixedWidth(110)
        self.btn_next.setStyleSheet(
            "QPushButton { background-color: #2563EB; color: #FFFFFF; font-weight: 600; font-size: 13px; border-radius: 8px; padding: 6px 12px; border: none; } "
            "QPushButton:hover { background-color: #1D4ED8; }"
        )
        self.btn_next.clicked.connect(self.next_step)

        btn_close = QPushButton("Close")
        btn_close.setFixedWidth(80)
        btn_close.setStyleSheet(
            "QPushButton { background-color: transparent; color: #64748B; font-weight: 600; font-size: 13px; border: none; } "
            "QPushButton:hover { color: #0F172A; }"
        )
        btn_close.clicked.connect(self.accept)

        footer_row.addWidget(self.btn_prev)
        footer_row.addWidget(self.btn_next)
        footer_row.addStretch()
        footer_row.addWidget(btn_close)
        card_layout.addLayout(footer_row)

        main_layout.addWidget(card)

    def update_step_display(self):
        page_idx, title, message = self.guide_steps[self.current_step]
        total = len(self.guide_steps)

        self.badge_lbl.setText(f"Step {self.current_step + 1} of {total}")
        self.title_lbl.setText(title)
        self.msg_lbl.setText(message)

        self.btn_prev.setEnabled(self.current_step > 0)
        if self.current_step == total - 1:
            self.btn_next.setText("Finish ✓")
        else:
            self.btn_next.setText("Next ►")

        if self.on_navigate:
            self.on_navigate(page_idx)

    def next_step(self):
        if self.current_step < len(self.guide_steps) - 1:
            self.current_step += 1
            self.update_step_display()
        else:
            self.accept()

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step_display()
