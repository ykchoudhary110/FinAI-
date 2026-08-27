from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class BusinessAdvisorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header = QLabel("Business Financial Advisor & KPI Insights")
        header.setStyleSheet("font-size: 22px; font-weight: 800; color: #005FB8;")
        layout.addWidget(header)

        disclaimer = QLabel("ℹ️ General Business Guidance — Not Licensed Accounting / Legal Audit Advice.")
        disclaimer.setStyleSheet("background: #E0EEFF; color: #005FB8; padding: 10px 14px; border-radius: 8px; font-size: 13px; font-weight: 600;")
        layout.addWidget(disclaimer)

        # Key Business KPIs Card
        kpi_card = QFrame()
        kpi_card.setProperty("class", "Card")
        k_layout = QVBoxLayout(kpi_card)
        k_layout.setContentsMargins(15, 15, 15, 15)

        k_title = QLabel("Business Financial Ratios & Health Metrics")
        k_title.setStyleSheet("font-weight: bold; font-size: 15px; color: #111827;")
        k_layout.addWidget(k_title)

        k1 = QLabel("<b>Working Capital Ratio (Current Ratio)</b>: 1.85 (Healthy &gt; 1.5)")
        k2 = QLabel("<b>Inventory Turnover Ratio</b>: 6.2x per year (Good velocity)")
        k3 = QLabel("<b>Net Cash Flow Status</b>: Positive (+₹45,200 this month)")

        for k in (k1, k2, k3):
            k.setStyleSheet("color: #111827; font-size: 13px;")
            k_layout.addWidget(k)

        layout.addWidget(kpi_card)

        # AI Insights Card
        rec_card = QFrame()
        rec_card.setProperty("class", "Card")
        r_layout = QVBoxLayout(rec_card)
        r_layout.setContentsMargins(15, 15, 15, 15)

        r_title = QLabel("Smart Business Recommendations")
        r_title.setStyleSheet("font-weight: bold; font-size: 15px; color: #111827;")

        r1 = QLabel("1. <b>Vendor Payment Planning</b>: Negotiate 45-day credit terms with primary suppliers to optimize working capital cash flow.")
        r2 = QLabel("2. <b>Input Tax Credit (ITC)</b>: 3 recent business expenses have valid GSTINs. Claiming ITC will save ₹4,850 on your GSTR-3B tax payment.")
        
        for r in (r1, r2):
            r.setStyleSheet("color: #111827; font-size: 13px;")
            r.setWordWrap(True)

        r_layout.addWidget(r_title)
        r_layout.addWidget(r1)
        r_layout.addWidget(r2)
        layout.addWidget(rec_card)

        layout.addStretch()
