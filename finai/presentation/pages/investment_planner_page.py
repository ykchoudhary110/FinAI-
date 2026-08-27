from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from finai.domain.rules.interest_rules import calculate_investment_sip


class InvestmentPlannerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("Educational Investment Planner (SIP, FD, RD, PPF, NPS)")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #005FB8;")
        layout.addWidget(header)

        disclaimer = QLabel("⚠️ Educational & Illustrative Projections Only — Not Licensed Financial / Investment Advice.")
        disclaimer.setStyleSheet("background: #FFF3CD; color: #856404; padding: 8px 12px; border-radius: 6px; font-size: 12px;")
        layout.addWidget(disclaimer)

        card = QFrame()
        card.setStyleSheet("background: #FFFFFF; border: 1px solid #E5E5E5; border-radius: 12px; padding: 15px;")
        c_layout = QFormLayout(card)

        self.tool_combo = QComboBox()
        self.tool_combo.addItems(["SIP (Systematic Investment Plan)", "Fixed Deposit (FD)", "PPF", "NPS"])

        self.monthly_amt = QDoubleSpinBox()
        self.monthly_amt.setRange(500, 1000000)
        self.monthly_amt.setValue(5000.0)

        self.rate_input = QDoubleSpinBox()
        self.rate_input.setRange(1.0, 30.0)
        self.rate_input.setValue(12.0)

        self.tenure_input = QSpinBox()
        self.tenure_input.setRange(1, 40)
        self.tenure_input.setValue(10)

        c_layout.addRow("Investment Vehicle:", self.tool_combo)
        c_layout.addRow("Monthly Contribution (₹):", self.monthly_amt)
        c_layout.addRow("Expected Annual Return (%):", self.rate_input)
        c_layout.addRow("Tenure (Years):", self.tenure_input)

        btn = QPushButton("Calculate Investment Projections")
        btn.clicked.connect(self.calculate)
        c_layout.addRow(btn)

        self.res_lbl = QLabel("Click calculate to view projected growth.")
        self.res_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #005FB8; margin-top: 10px;")
        c_layout.addRow(self.res_lbl)

        layout.addWidget(card)
        layout.addStretch()

    def calculate(self):
        m = self.monthly_amt.value()
        r = self.rate_input.value()
        y = self.tenure_input.value()
        res = calculate_investment_sip(m, r, y)
        self.res_lbl.setText(
            f"Total Invested: **₹{res.total_invested:,.2f}** | Estimated Wealth Gain: **₹{res.estimated_returns:,.2f}**\n"
            f"Expected Final Corpus ({y} Yrs): **₹{res.final_corpus:,.2f}**"
        )
