import tempfile
from pathlib import Path
import qrcode
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from finai.domain.models.financial_models import TaxRegime, TaxpayerCategory
from finai.domain.rules.emi_rules import calculate_emi
from finai.domain.rules.gst_rules import (
    calculate_gst_forward,
    calculate_gst_reverse,
    check_blocked_credit_sec17_5,
    check_itc_eligibility_sec16,
    check_rule_86b_compliance,
    reconcile_gstr2b_purchase_register,
)
from finai.domain.rules.tax_rules import (
    calculate_capital_gains_tax,
    calculate_hra_exemption,
    calculate_income_tax,
    calculate_presumptive_tax_44ad,
    calculate_presumptive_tax_44ada,
    compare_tax_regimes,
)
from finai.presentation.theme.styles import (
    BORDER_SUBTLE,
    PRIMARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


def create_label_with_tooltip(text: str, tooltip_text: str) -> QWidget:
    """Helper creating a label with a hoverable badge for financial jargon explanations."""
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)

    lbl_title = QLabel(text)
    lbl_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; font-size: 13px;")

    lbl_help = QLabel("[?]")
    lbl_help.setToolTip(tooltip_text)
    lbl_help.setStyleSheet(f"color: {PRIMARY}; font-weight: 700; font-size: 12px; cursor: pointer;")

    layout.addWidget(lbl_title)
    layout.addWidget(lbl_help)
    layout.addStretch()
    return container


class FinancialToolsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Header Frame
        header_row = QHBoxLayout()
        header_title = QLabel("Pro CA Financial & Tax Controller Suite")
        header_title.setStyleSheet(f"font-size: 26px; font-weight: 800; color: {PRIMARY}; letter-spacing: -0.02em;")
        
        ca_badge = QLabel("CA AUDIT WORKSTATION (AY 2026-27 / FY 2025-26)")
        ca_badge.setStyleSheet("background-color: #DBEAFE; color: #1E40AF; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 6px;")
        
        header_row.addWidget(header_title)
        header_row.addStretch()
        header_row.addWidget(ca_badge)
        main_layout.addLayout(header_row)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #E2E8F0; background: #FFFFFF; border-radius: 10px; }
            QTabBar::tab { background: #F8FAFC; color: #475569; font-weight: 600; font-size: 13px; padding: 10px 20px; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 4px; }
            QTabBar::tab:selected { background: #FFFFFF; color: #2563EB; border-bottom: 2px solid #2563EB; }
        """)

        self.tabs.addTab(self.create_regime_optimizer_tab(), "Regime Auto-Optimizer (Old vs New)")
        self.tabs.addTab(self.create_presumptive_tab(), "Presumptive Tax (44ADA / 44AD)")
        self.tabs.addTab(self.create_capital_gains_tab(), "Capital Gains (Budget 2024/25)")
        self.tabs.addTab(self.create_gst_audit_tab(), "GST & ITC Reconciliation Suite")
        self.tabs.addTab(self.create_emi_tab(), "EMI & Amortization")

        main_layout.addWidget(self.tabs)

    # ---------------- TAB 1: REGIME AUTO-OPTIMIZER ----------------
    def create_regime_optimizer_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Form Inputs Grid
        grid_frame = QFrame()
        grid_frame.setStyleSheet("background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px;")
        grid = QGridLayout(grid_frame)
        grid.setSpacing(12)

        # Gross Income
        self.opt_gross_income = QDoubleSpinBox()
        self.opt_gross_income.setRange(0, 500000000)
        self.opt_gross_income.setValue(1275000.0)
        self.opt_gross_income.setPrefix("₹ ")
        self.opt_gross_income.setSingleStep(25000)
        grid.addWidget(create_label_with_tooltip("Gross Annual Salary / Income:", "Total earnings before any deductions."), 0, 0)
        grid.addWidget(self.opt_gross_income, 0, 1)

        # 80C Deductions
        self.opt_80c = QDoubleSpinBox()
        self.opt_80c.setRange(0, 150000)
        self.opt_80c.setValue(150000.0)
        self.opt_80c.setPrefix("₹ ")
        grid.addWidget(create_label_with_tooltip("Section 80C (PPF, ELSS, EPF, LIC) [Max ₹1.5L]:", "Deductions for tax-saving investments in Old Regime."), 0, 2)
        grid.addWidget(self.opt_80c, 0, 3)

        # 80D Health Insurance
        self.opt_80d = QDoubleSpinBox()
        self.opt_80d.setRange(0, 100000)
        self.opt_80d.setValue(25000.0)
        self.opt_80d.setPrefix("₹ ")
        grid.addWidget(create_label_with_tooltip("Section 80D (Health Insurance Premia):", "Self (₹25k) + Senior Citizen Parents (up to ₹50k)."), 1, 0)
        grid.addWidget(self.opt_80d, 1, 1)

        # 80CCD(1B) NPS
        self.opt_80ccd = QDoubleSpinBox()
        self.opt_80ccd.setRange(0, 50000)
        self.opt_80ccd.setValue(50000.0)
        self.opt_80ccd.setPrefix("₹ ")
        grid.addWidget(create_label_with_tooltip("Section 80CCD(1B) (National Pension System):", "Exclusive ₹50,000 deduction for NPS Tier-I."), 1, 2)
        grid.addWidget(self.opt_80ccd, 1, 3)

        # HRA Exemption Inputs
        self.opt_hra_basic = QDoubleSpinBox()
        self.opt_hra_basic.setRange(0, 50000000)
        self.opt_hra_basic.setValue(600000.0)
        self.opt_hra_basic.setPrefix("₹ ")

        self.opt_hra_rec = QDoubleSpinBox()
        self.opt_hra_rec.setRange(0, 50000000)
        self.opt_hra_rec.setValue(240000.0)
        self.opt_hra_rec.setPrefix("₹ ")

        self.opt_rent_paid = QDoubleSpinBox()
        self.opt_rent_paid.setRange(0, 50000000)
        self.opt_rent_paid.setValue(240000.0)
        self.opt_rent_paid.setPrefix("₹ ")

        self.opt_is_metro = QCheckBox("Metro City (50% Basic)")
        self.opt_is_metro.setChecked(True)

        grid.addWidget(create_label_with_tooltip("Basic Salary (for HRA):", "Basic salary component used to compute 10% rent limit."), 2, 0)
        grid.addWidget(self.opt_hra_basic, 2, 1)
        grid.addWidget(create_label_with_tooltip("Actual HRA Received:", "HRA allowance shown on monthly payslip."), 2, 2)
        grid.addWidget(self.opt_hra_rec, 2, 3)

        grid.addWidget(create_label_with_tooltip("Annual Rent Paid:", "Total rent paid to landlord with receipts."), 3, 0)
        grid.addWidget(self.opt_rent_paid, 3, 1)
        grid.addWidget(self.opt_is_metro, 3, 2)

        # Home Loan Interest
        self.opt_home_loan = QDoubleSpinBox()
        self.opt_home_loan.setRange(0, 200000)
        self.opt_home_loan.setValue(0.0)
        self.opt_home_loan.setPrefix("₹ ")
        grid.addWidget(create_label_with_tooltip("Section 24(b) (Home Loan Interest) [Max ₹2L]:", "Interest deduction on self-occupied residential property loan."), 4, 0)
        grid.addWidget(self.opt_home_loan, 4, 1)

        layout.addWidget(grid_frame)

        btn_calc_opt = QPushButton("⚡ Execute Pro CA Regime Auto-Optimization")
        btn_calc_opt.setStyleSheet("background-color: #2563EB; color: #FFFFFF; font-weight: 700; font-size: 14px; padding: 12px; border-radius: 8px;")
        btn_calc_opt.clicked.connect(self.run_regime_optimization)
        layout.addWidget(btn_calc_opt)

        # Recommendation Banner
        self.opt_recommend_banner = QLabel("Click 'Execute Pro CA Regime Auto-Optimization' to compare both tax regimes.")
        self.opt_recommend_banner.setStyleSheet("background-color: #EFF6FF; color: #1E3A8A; font-size: 14px; font-weight: 700; padding: 14px; border-radius: 8px; border: 1px solid #BFDBFE;")
        layout.addWidget(self.opt_recommend_banner)

        # Comparison Result Table
        self.opt_table = QTableWidget(7, 3)
        self.opt_table.setHorizontalHeaderLabels(["Tax Parameter", "New Tax Regime (Sec 115BAC)", "Old Tax Regime (With Deductions)"])
        self.opt_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.opt_table.verticalHeader().setVisible(False)
        self.opt_table.setStyleSheet("background: #FFFFFF; gridline-color: #E2E8F0; font-size: 13px;")
        layout.addWidget(self.opt_table)

        scroll.setWidget(container)
        return scroll

    def run_regime_optimization(self):
        gross = self.opt_gross_income.value()
        basic = self.opt_hra_basic.value()
        hra_rec = self.opt_hra_rec.value()
        rent = self.opt_rent_paid.value()
        is_metro = self.opt_is_metro.isChecked()

        hra_res = calculate_hra_exemption(basic, hra_rec, rent, is_metro)
        exempt_hra = hra_res["exempt_hra"]

        res = compare_tax_regimes(
            gross_income=gross,
            is_salaried=True,
            deductions_80c=self.opt_80c.value(),
            deductions_80d=self.opt_80d.value(),
            deductions_80ccd=self.opt_80ccd.value(),
            hra_exemption=exempt_hra,
            home_loan_interest_24b=self.opt_home_loan.value(),
        )

        # Update Banner
        rec = res["recommended_regime"]
        sav = res["tax_savings"]
        if rec == "NEW":
            self.opt_recommend_banner.setText(f"🏆 RECOMMENDED: New Tax Regime (Section 115BAC) — Saves ₹{sav:,.2f} in Net Tax!")
            self.opt_recommend_banner.setStyleSheet("background-color: #DCFCE7; color: #14532D; font-size: 15px; font-weight: 800; padding: 14px; border-radius: 8px; border: 1px solid #86EFAC;")
        elif rec == "OLD":
            self.opt_recommend_banner.setText(f"🏆 RECOMMENDED: Old Tax Regime (With Exemptions) — Saves ₹{sav:,.2f} in Net Tax!")
            self.opt_recommend_banner.setStyleSheet("background-color: #FEF3C7; color: #78350F; font-size: 15px; font-weight: 800; padding: 14px; border-radius: 8px; border: 1px solid #FDE68A;")
        else:
            self.opt_recommend_banner.setText("🤝 Both Tax Regimes produce identical tax liability of ₹0.00!")
            self.opt_recommend_banner.setStyleSheet("background-color: #EFF6FF; color: #1E3A8A; font-size: 15px; font-weight: 800; padding: 14px; border-radius: 8px; border: 1px solid #BFDBFE;")

        # Populate Comparison Table
        nr = res["new_regime"]
        or_ = res["old_regime"]

        rows = [
            ("Gross Income", f"₹ {gross:,.2f}", f"₹ {gross:,.2f}"),
            ("Standard Deduction", f"₹ {nr['standard_deduction']:,.2f}", f"₹ {or_['standard_deduction']:,.2f}"),
            ("Chapter VI-A Deductions & HRA", "₹ 0.00 (Not Allowed)", f"₹ {or_['chapter_via_deductions']:,.2f}"),
            ("Taxable Income", f"₹ {nr['taxable_income']:,.2f}", f"₹ {or_['taxable_income']:,.2f}"),
            ("Slab Tax (Before Rebate)", f"₹ {nr['slab_tax']:,.2f}", f"₹ {or_['slab_tax']:,.2f}"),
            ("Section 87A Rebate", f"₹ {nr['rebate_87a']:,.2f}", f"₹ {or_['rebate_87a']:,.2f}"),
            ("Total Tax Payable (With 4% Cess)", f"₹ {nr['total_tax']:,.2f}", f"₹ {or_['total_tax']:,.2f}"),
        ]

        for idx, (param, new_val, old_val) in enumerate(rows):
            item_p = QTableWidgetItem(param)
            item_n = QTableWidgetItem(new_val)
            item_o = QTableWidgetItem(old_val)

            if idx == 6:  # Total Tax row highlight
                item_p.setBackground(QColor("#F1F5F9"))
                item_n.setBackground(QColor("#DCFCE7") if rec == "NEW" else QColor("#FFFFFF"))
                item_o.setBackground(QColor("#FEF3C7") if rec == "OLD" else QColor("#FFFFFF"))

            self.opt_table.setItem(idx, 0, item_p)
            self.opt_table.setItem(idx, 1, item_n)
            self.opt_table.setItem(idx, 2, item_o)

    # ---------------- TAB 2: PRESUMPTIVE TAXATION ----------------
    def create_presumptive_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 44ADA Section (Freelancers / Professionals)
        grp_ada = QGroupBox("Section 44ADA: Professionals & Freelancers (50% Deemed Profit)")
        grp_ada.setStyleSheet("font-weight: bold; color: #1E3A8A;")
        l_ada = QFormLayout(grp_ada)
        l_ada.setSpacing(10)

        self.ada_receipts = QDoubleSpinBox()
        self.ada_receipts.setRange(0, 7500000)
        self.ada_receipts.setValue(3500000.0)
        self.ada_receipts.setPrefix("₹ ")
        l_ada.addRow(create_label_with_tooltip("Gross Professional Receipts (Max ₹75L):", "Total fee receipts from clients during the FY."), self.ada_receipts)

        btn_calc_ada = QPushButton("Compute Section 44ADA Presumptive Income")
        btn_calc_ada.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; padding: 8px;")
        btn_calc_ada.clicked.connect(self.run_44ada)
        l_ada.addRow(btn_calc_ada)

        self.ada_result_lbl = QLabel("Deemed Taxable Profit (50%): ₹ 17,50,000.00 (No books of account required)")
        self.ada_result_lbl.setStyleSheet("color: #0F172A; font-weight: bold; font-size: 13px;")
        l_ada.addRow(self.ada_result_lbl)

        layout.addWidget(grp_ada)

        # 44AD Section (Small Business MSME)
        grp_ad = QGroupBox("Section 44AD: Small Businesses & Traders (6% Digital / 8% Cash Profit)")
        grp_ad.setStyleSheet("font-weight: bold; color: #78350F;")
        l_ad = QFormLayout(grp_ad)
        l_ad.setSpacing(10)

        self.ad_digital = QDoubleSpinBox()
        self.ad_digital.setRange(0, 30000000)
        self.ad_digital.setValue(8000000.0)
        self.ad_digital.setPrefix("₹ ")

        self.ad_cash = QDoubleSpinBox()
        self.ad_cash.setRange(0, 30000000)
        self.ad_cash.setValue(1000000.0)
        self.ad_cash.setPrefix("₹ ")

        l_ad.addRow(create_label_with_tooltip("Digital / Banking Turnover (6% Deemed Profit):", "Turnover received via UPI, RTGS, NEFT, Cheque."), self.ad_digital)
        l_ad.addRow(create_label_with_tooltip("Cash Turnover (8% Deemed Profit):", "Turnover received in cash (must be <= 5% of total)."), self.ad_cash)

        btn_calc_ad = QPushButton("Compute Section 44AD Business Profit")
        btn_calc_ad.setStyleSheet("background-color: #D97706; color: white; font-weight: bold; padding: 8px;")
        btn_calc_ad.clicked.connect(self.run_44ad)
        l_ad.addRow(btn_calc_ad)

        self.ad_result_lbl = QLabel("Total Deemed Business Profit: ₹ 5,60,000.00 (₹4.8L digital + ₹80k cash)")
        self.ad_result_lbl.setStyleSheet("color: #0F172A; font-weight: bold; font-size: 13px;")
        l_ad.addRow(self.ad_result_lbl)

        layout.addWidget(grp_ad)
        layout.addStretch()
        return widget

    def run_44ada(self):
        res = calculate_presumptive_tax_44ada(self.ada_receipts.value())
        self.ada_result_lbl.setText(f"Deemed Taxable Profit (50%): ₹ {res['taxable_presumptive_income']:,.2f} | Status: {res['message']}")

    def run_44ad(self):
        res = calculate_presumptive_tax_44ad(self.ad_digital.value(), self.ad_cash.value())
        self.ad_result_lbl.setText(f"Total Deemed Profit: ₹ {res['total_presumptive_profit']:,.2f} (Digital: ₹{res['deemed_digital_profit_6pct']:,.2f} + Cash: ₹{res['deemed_cash_profit_8pct']:,.2f})")

    # ---------------- TAB 3: CAPITAL GAINS ----------------
    def create_capital_gains_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        form = QFormLayout()
        form.setSpacing(12)

        self.cg_stcg = QDoubleSpinBox()
        self.cg_stcg.setRange(0, 100000000)
        self.cg_stcg.setValue(200000.0)
        self.cg_stcg.setPrefix("₹ ")

        self.cg_ltcg_eq = QDoubleSpinBox()
        self.cg_ltcg_eq.setRange(0, 100000000)
        self.cg_ltcg_eq.setValue(325000.0)
        self.cg_ltcg_eq.setPrefix("₹ ")

        self.cg_ltcg_prop = QDoubleSpinBox()
        self.cg_ltcg_prop.setRange(0, 100000000)
        self.cg_ltcg_prop.setValue(500000.0)
        self.cg_ltcg_prop.setPrefix("₹ ")

        form.addRow(create_label_with_tooltip("STCG on Equity / MF (Sec 111A) [@ 20%]:", "Revised Budget 2024 tax rate for short-term equity gains."), self.cg_stcg)
        form.addRow(create_label_with_tooltip("LTCG on Equity / MF (Sec 112A) [@ 12.5%]:", "Taxed at 12.5% on gains exceeding ₹1.25 Lakh annual exemption."), self.cg_ltcg_eq)
        form.addRow(create_label_with_tooltip("LTCG on Property / Gold (Sec 112) [@ 12.5%]:", "Long-term gains on immovable property / gold without indexation."), self.cg_ltcg_prop)

        btn_calc_cg = QPushButton("Compute Budget 2024/25 Capital Gains Tax")
        btn_calc_cg.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; padding: 10px; border-radius: 6px;")
        btn_calc_cg.clicked.connect(self.run_capital_gains)
        form.addRow(btn_calc_cg)

        layout.addLayout(form)

        self.cg_result_banner = QLabel("Click to calculate revised capital gains tax liabilities.")
        self.cg_result_banner.setStyleSheet("background-color: #F8FAFC; color: #0F172A; font-weight: 700; padding: 16px; border-radius: 8px; border: 1px solid #E2E8F0;")
        layout.addWidget(self.cg_result_banner)

        layout.addStretch()
        return widget

    def run_capital_gains(self):
        res = calculate_capital_gains_tax(
            stcg_equity=self.cg_stcg.value(),
            ltcg_equity=self.cg_ltcg_eq.value(),
            ltcg_property_gold=self.cg_ltcg_prop.value()
        )
        self.cg_result_banner.setText(
            f"📊 Capital Gains Tax Summary (Budget 2024/25):\n\n"
            f"• STCG Sec 111A (20%): ₹ {res['stcg_equity_tax_20pct']:,.2f}\n"
            f"• LTCG Sec 112A (12.5% over ₹1.25L): ₹ {res['ltcg_equity_tax_12_5pct']:,.2f} (Exemption applied: ₹1,25,000)\n"
            f"• LTCG Sec 112 Property/Gold (12.5%): ₹ {res['ltcg_property_tax_12_5pct']:,.2f}\n"
            f"• Health & Education Cess (4%): ₹ {res['cess_4pct']:,.2f}\n"
            f"👉 Total Final Capital Gains Tax Payable: ₹ {res['final_capital_gains_tax_payable']:,.2f}"
        )

    # ---------------- TAB 4: GST & ITC RECONCILIATION ----------------
    def create_gst_audit_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Standard GST Forward/Reverse
        row1 = QHBoxLayout()
        self.gst_calc_base = QDoubleSpinBox()
        self.gst_calc_base.setRange(0, 100000000)
        self.gst_calc_base.setValue(100000.0)
        self.gst_calc_base.setPrefix("₹ ")

        self.gst_calc_rate = QComboBox()
        self.gst_calc_rate.addItems(["5%", "12%", "18%", "28%"])
        self.gst_calc_rate.setCurrentText("18%")

        self.gst_is_interstate = QCheckBox("Interstate (IGST)")

        row1.addWidget(QLabel("Base Amount:"))
        row1.addWidget(self.gst_calc_base)
        row1.addWidget(QLabel("GST Rate:"))
        row1.addWidget(self.gst_calc_rate)
        row1.addWidget(self.gst_is_interstate)

        btn_calc_gst = QPushButton("Calculate GST Split")
        btn_calc_gst.clicked.connect(self.run_gst_calc)
        row1.addWidget(btn_calc_gst)
        layout.addLayout(row1)

        self.gst_split_result = QLabel("Base: ₹1,00,000.00 | CGST (9%): ₹9,000.00 | SGST (9%): ₹9,000.00 | Total Payable / Invoice: ₹1,18,000.00")
        self.gst_split_result.setStyleSheet("color: #2563EB; font-weight: bold; padding: 6px;")
        self.gst_result_label = self.gst_split_result
        layout.addWidget(self.gst_split_result)

        # Section 17(5) Blocked Credit Checker
        grp_blocked = QGroupBox("Section 17(5) Blocked ITC Inspector")
        l_bl = QHBoxLayout(grp_blocked)
        self.blocked_combo = QComboBox()
        self.blocked_combo.addItems([
            "Office Laptops & Hardware",
            "Executive Motor Car (5 Seater)",
            "Client Dinner & Outdoor Catering",
            "Commercial Truck (Cargo transport)",
            "Employee Gym & Fitness Membership"
        ])
        btn_check_blocked = QPushButton("Check Blocked Status")
        btn_check_blocked.clicked.connect(self.run_blocked_check)

        l_bl.addWidget(QLabel("Expense Category:"))
        l_bl.addWidget(self.blocked_combo)
        l_bl.addWidget(btn_check_blocked)
        layout.addWidget(grp_blocked)

        self.blocked_result_lbl = QLabel("Eligible for ITC.")
        self.blocked_result_lbl.setStyleSheet("font-weight: 700; color: #16A34A; padding: 4px;")
        layout.addWidget(self.blocked_result_lbl)

        # GSTR-2B Reconciliation Demo
        btn_run_2b = QPushButton("⚡ Run Automated GSTR-2B vs Purchase Register Audit (Sample Batch)")
        btn_run_2b.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; padding: 10px;")
        btn_run_2b.clicked.connect(self.run_2b_reconciliation)
        layout.addWidget(btn_run_2b)

        self.audit_2b_summary = QLabel("Click to run GSTR-2B purchase reconciliation.")
        self.audit_2b_summary.setStyleSheet("background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px; border-radius: 6px; font-size: 13px;")
        layout.addWidget(self.audit_2b_summary)

        layout.addStretch()
        return widget

    def update_gst(self):
        self.run_gst_calc()

    def run_gst_calc(self):
        rate = float(self.gst_calc_rate.currentText().replace("%", ""))
        is_inter = self.gst_is_interstate.isChecked()
        res = calculate_gst_forward(self.gst_calc_base.value(), rate, is_inter)
        if is_inter:
            self.gst_split_result.setText(f"Base: ₹{res.base_amount:,.2f} | IGST ({res.igst_rate}%): ₹{res.igst_amount:,.2f} | Total Payable: ₹{res.total_amount:,.2f}")
        else:
            self.gst_split_result.setText(f"Base: ₹{res.base_amount:,.2f} | CGST ({res.cgst_rate}%): ₹{res.cgst_amount:,.2f} | SGST ({res.sgst_rate}%): ₹{res.sgst_amount:,.2f} | Total Payable: ₹{res.total_amount:,.2f}")

    def run_blocked_check(self):
        cat = self.blocked_combo.currentText()
        res = check_blocked_credit_sec17_5(cat)
        if res["is_blocked"]:
            self.blocked_result_lbl.setText(f"❌ INELIGIBLE: {res['audit_note']}")
            self.blocked_result_lbl.setStyleSheet("font-weight: 700; color: #DC2626; padding: 4px;")
        else:
            self.blocked_result_lbl.setText(f"✅ ELIGIBLE: {res['audit_note']}")
            self.blocked_result_lbl.setStyleSheet("font-weight: 700; color: #16A34A; padding: 4px;")

    def run_2b_reconciliation(self):
        sample_purchase = [
            {"invoice_no": "INV-101", "supplier": "Dell India", "tax_amount": 18000.0, "category": "Office Laptops"},
            {"invoice_no": "INV-102", "supplier": "Taj Hotels", "tax_amount": 3600.0, "category": "Client Dinner"},
            {"invoice_no": "INV-103", "supplier": "Airtel Broadband", "tax_amount": 180.0, "category": "Internet"},
            {"invoice_no": "INV-104", "supplier": "Local Stationery", "tax_amount": 540.0, "category": "Office Supplies"},
        ]
        sample_2b = [
            {"invoice_no": "INV-101", "tax_amount": 18000.0},
            {"invoice_no": "INV-103", "tax_amount": 180.0},
        ]
        res = reconcile_gstr2b_purchase_register(sample_purchase, sample_2b)
        self.audit_2b_summary.setText(
            f"📋 GSTR-2B Audit Results:\n"
            f"• Invoices Audited: {res['total_invoices_audited']} | Matched in 2B: {res['matched_count']} (₹ {res['total_eligible_itc_to_claim']:,.2f} Claimable)\n"
            f"• Missing in 2B: {res['missing_in_2b_count']} (Pending supplier filing - INV-104)\n"
            f"• Ineligible / Blocked under Sec 17(5): {res['blocked_itc_count']} (Taj Hotels Dining - ₹ {res['total_blocked_itc']:,.2f})\n"
            f"👉 100% Audit Safety: Only matched & non-blocked ITC will be claimed in GSTR-3B."
        )

    # ---------------- TAB 5: EMI ----------------
    def create_emi_tab(self) -> QWidget:
        widget = QWidget()
        l = QVBoxLayout(widget)
        l.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        self.emi_principal = QDoubleSpinBox()
        self.emi_principal.setRange(0, 100000000)
        self.emi_principal.setValue(2500000.0)
        self.emi_principal.setPrefix("₹ ")

        self.emi_rate = QDoubleSpinBox()
        self.emi_rate.setRange(0, 50)
        self.emi_rate.setValue(8.5)
        self.emi_rate.setSuffix(" %")

        self.emi_tenure = QSpinBox()
        self.emi_tenure.setRange(1, 480)
        self.emi_tenure.setValue(120)
        self.emi_tenure.setSuffix(" Months")

        form.addRow("Loan Principal (₹):", self.emi_principal)
        form.addRow("Annual Interest Rate (%):", self.emi_rate)
        form.addRow("Tenure (Months):", self.emi_tenure)

        btn_calc_emi = QPushButton("Calculate Loan EMI & Amortization")
        btn_calc_emi.clicked.connect(self.run_emi_calc)
        form.addRow(btn_calc_emi)
        l.addLayout(form)

        self.emi_result_lbl = QLabel("Monthly EMI: ₹ 31,003.54 | Total Interest: ₹ 12,20,424.80 | Total Payment: ₹ 37,20,424.80")
        self.emi_result_lbl.setStyleSheet("color: #0F172A; font-weight: bold; font-size: 14px; padding: 10px;")
        l.addWidget(self.emi_result_lbl)

        l.addStretch()
        return widget

    def run_emi_calc(self):
        res = calculate_emi(
            principal=self.emi_principal.value(),
            annual_rate=self.emi_rate.value(),
            tenure_months=self.emi_tenure.value()
        )
        self.emi_result_lbl.setText(
            f"Monthly EMI: ₹ {res.monthly_emi:,.2f} | "
            f"Total Interest: ₹ {res.total_interest:,.2f} | "
            f"Total Payment: ₹ {res.total_payment:,.2f}"
        )
