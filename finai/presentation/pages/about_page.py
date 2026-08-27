from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from finai.presentation.theme.styles import CARD_BG, PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY


class AboutPage(QWidget):
    def __init__(self, on_start_tour=None, parent=None):
        super().__init__(parent)
        self.on_start_tour = on_start_tour
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        header = QLabel("About FinAI & Architecture")
        header.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {TEXT_PRIMARY}; letter-spacing: -0.02em;")
        layout.addWidget(header)

        card = QFrame()
        card.setStyleSheet(f"background-color: {CARD_BG}; border: 1px solid rgba(15, 23, 42, 0.06); border-radius: 16px; padding: 20px;")
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(12)

        info = QLabel(
            f"<h2 style='color: {PRIMARY}; margin-top:0;'>FinAI — Offline Financial Assistant</h2>"
            f"<p style='font-size: 14px; color: {TEXT_SECONDARY};'>Version 1.0.0 (Production Edition)</p>"
            f"<hr style='border: none; border-top: 1px solid #E2E8F0;'>"
            f"<h3>How Your Data Stays 100% Private</h3>"
            f"<ul>"
            f"<li><b>Zero Cloud Telemetry</b>: All OCR, tax rules, and local LLM chat run strictly on your local PC.</li>"
            f"<li><b>SHA-256 Hash Chain Ledger</b>: Append-only cryptographic audit trail guarantees calculation integrity.</li>"
            f"<li><b>100% Deterministic Rule Engine</b>: Tax, GST, and EMI calculations never hallucinate numbers.</li>"
            f"<li><b>Offline RAG Grounding</b>: AI Chat grounds answers in local Knowledge Base articles with source citations.</li>"
            f"</ul>"
        )
        info.setTextFormat(Qt.RichText)
        c_layout.addWidget(info)

        if self.on_start_tour:
            btn_tour = QPushButton("Launch Interactive App Guide")
            btn_tour.setStyleSheet("background-color: #2563EB; color: #FFFFFF; font-weight: 600; font-size: 14px; min-height: 40px; border-radius: 10px;")
            btn_tour.clicked.connect(self.on_start_tour)
            c_layout.addWidget(btn_tour)

        layout.addWidget(card)
        layout.addStretch()
