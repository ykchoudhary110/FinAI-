from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QSlider,
    QVBoxLayout,
    QWidget,
)
from finai.presentation.theme.styles import (
    DANGER,
    PRIMARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class BudgetPlannerPage(QWidget):
    def __init__(self, budget_repo=None, parent=None):
        super().__init__(parent)
        self.budget_repo = budget_repo
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        header = QLabel("Budget Planner & What-If Simulator")
        header.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {TEXT_PRIMARY}; letter-spacing: -0.02em;")
        layout.addWidget(header)

        # What-If Simulator Card (Pristine Light Surface)
        sim_card = QFrame()
        sim_card.setProperty("class", "Card")
        sim_card.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 20px;")
        s_layout = QVBoxLayout(sim_card)

        s_title = QLabel("What-If Budget Simulator (Live Re-computation)")
        s_title.setStyleSheet(f"font-weight: 600; font-size: 16px; color: {TEXT_PRIMARY}; margin-bottom: 12px;")
        s_layout.addWidget(s_title)

        form = QFormLayout()
        form.setSpacing(12)

        # Income Change Slider (-50% to +50%)
        self.slider_inc = QSlider(Qt.Horizontal)
        self.slider_inc.setRange(-50, 50)
        self.slider_inc.setValue(0)
        self.lbl_inc = QLabel("0%")
        self.lbl_inc.setStyleSheet(f"font-weight: 700; color: {PRIMARY}; font-size: 14px;")
        self.slider_inc.valueChanged.connect(lambda v: self.lbl_inc.setText(f"{v:+}%"))

        # Expense Change Slider (-50% to +50%)
        self.slider_exp = QSlider(Qt.Horizontal)
        self.slider_exp.setRange(-50, 50)
        self.slider_exp.setValue(0)
        self.lbl_exp = QLabel("0%")
        self.lbl_exp.setStyleSheet(f"font-weight: 700; color: {PRIMARY}; font-size: 14px;")
        self.slider_exp.valueChanged.connect(lambda v: self.lbl_exp.setText(f"{v:+}%"))

        lbl_inc_title = QLabel("Projected Income Change (%):")
        lbl_inc_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; font-size: 14px;")
        lbl_exp_title = QLabel("Projected Expense Change (%):")
        lbl_exp_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; font-size: 14px;")

        lbl_inc_delta = QLabel("Income Delta:")
        lbl_inc_delta.setStyleSheet(f"color: {TEXT_MUTED}; font-weight: 500; font-size: 13px;")
        lbl_exp_delta = QLabel("Expense Delta:")
        lbl_exp_delta.setStyleSheet(f"color: {TEXT_MUTED}; font-weight: 500; font-size: 13px;")

        form.addRow(lbl_inc_title, self.slider_inc)
        form.addRow(lbl_inc_delta, self.lbl_inc)
        form.addRow(lbl_exp_title, self.slider_exp)
        form.addRow(lbl_exp_delta, self.lbl_exp)

        s_layout.addLayout(form)

        # Debounced Timer for live re-computation (~150ms)
        self.debounce_timer = QTimer(self)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(150)
        self.debounce_timer.timeout.connect(self.recompute_simulation)

        self.slider_inc.valueChanged.connect(self.debounce_timer.start)
        self.slider_exp.valueChanged.connect(self.debounce_timer.start)

        self.sim_result_lbl = QLabel("Projected Monthly Savings: ₹35,000.00 | Time to ₹5L Goal: 10 months")
        self.sim_result_lbl.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {PRIMARY}; margin-top: 10px;")
        s_layout.addWidget(self.sim_result_lbl)

        layout.addWidget(sim_card)

        # Category Progress Bars Header
        cat_title = QLabel("Monthly Category Budgets & Caps")
        cat_title.setStyleSheet(f"font-weight: 600; font-size: 16px; color: {TEXT_PRIMARY}; margin-top: 10px;")
        layout.addWidget(cat_title)

        categories = [
            ("Shopping & Groceries", 25000, 18000),
            ("Utilities & Rent", 35000, 32000),
            ("Dining & Entertainment", 15000, 14200),
        ]

        for cat, limit, spent in categories:
            cat_card = QFrame()
            cat_card.setProperty("class", "Card")
            cat_card.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px;")
            c_box = QVBoxLayout(cat_card)
            c_box.setSpacing(8)

            pct = int((spent / limit) * 100)
            status_color = DANGER if pct >= 90 else PRIMARY

            c_lbl = QLabel(f"<b>{cat}</b>: ₹{spent:,.0f} spent of ₹{limit:,.0f} cap <span style='color: {status_color}; font-weight: bold;'>({pct}%)</span>")
            c_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 14px;")

            pbar = QProgressBar()
            pbar.setFixedHeight(12)
            pbar.setTextVisible(False)  # Prevents overlapping text over thin bar!
            pbar.setValue(pct)

            if pct >= 90:
                pbar.setStyleSheet(f"QProgressBar {{ background-color: #F1F5F9; border: 1px solid #E2E8F0; border-radius: 6px; }} QProgressBar::chunk {{ background-color: {DANGER}; border-radius: 6px; }}")
            else:
                pbar.setStyleSheet(f"QProgressBar {{ background-color: #F1F5F9; border: 1px solid #E2E8F0; border-radius: 6px; }} QProgressBar::chunk {{ background-color: {PRIMARY}; border-radius: 6px; }}")

            c_box.addWidget(c_lbl)
            c_box.addWidget(pbar)
            layout.addWidget(cat_card)

        layout.addStretch()

    def recompute_simulation(self):
        inc_change = self.slider_inc.value()
        exp_change = self.slider_exp.value()

        base_inc = 100000.0
        base_exp = 65000.0

        proj_inc = base_inc * (1.0 + (inc_change / 100.0))
        proj_exp = base_exp * (1.0 + (exp_change / 100.0))
        proj_savings = max(0.0, proj_inc - proj_exp)

        goal = 500000.0
        months_to_goal = int(goal / proj_savings) if proj_savings > 0 else 999

        self.sim_result_lbl.setText(
            f"Projected Monthly Savings: <b>₹{proj_savings:,.2f}</b> | Time to ₹5L Goal: <b>{months_to_goal} months</b>"
        )
