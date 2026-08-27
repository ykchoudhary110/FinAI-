from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class KnowledgeBasePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.articles = {
            "GST Fundamentals & ITC": (
                "<h1>GST Fundamentals & Input Tax Credit</h1>"
                "<p><b>Goods and Services Tax (GST)</b> is a comprehensive indirect tax on manufacture, sale, and consumption of goods and services throughout India.</p>"
                "<h3>Input Tax Credit (ITC) Rules</h3>"
                "<p>Under Section 16 of the CGST Act, business owners can claim ITC on tax paid for inputs used in business. Requirements include:</p>"
                "<ul>"
                "<li>Valid Tax Invoice issued by a registered supplier.</li>"
                "<li>Supplier must file GSTR-1 and tax reflected in GSTR-2B.</li>"
                "<li>Goods or services must actually be received.</li>"
                "</ul>"
            ),
            "Income Tax Slabs (FY 2025-26)": (
                "<h1>Income Tax Slabs (FY 2025-26 / AY 2026-27)</h1>"
                "<p>The Budget 2025 revised tax slabs under the New Tax Regime (default):</p>"
                "<ul>"
                "<li><b>₹0 – ₹4 Lakhs</b>: Nil (0%)</li>"
                "<li><b>₹4L – ₹8 Lakhs</b>: 5%</li>"
                "<li><b>₹8L – ₹12 Lakhs</b>: 10%</li>"
                "<li><b>₹12L – ₹16 Lakhs</b>: 15%</li>"
                "<li><b>₹16L – ₹20 Lakhs</b>: 20%</li>"
                "<li><b>₹20L – ₹24 Lakhs</b>: 25%</li>"
                "<li><b>Above ₹24 Lakhs</b>: 30%</li>"
                "</ul>"
                "<p><b>Section 87A Rebate</b>: Full tax rebate up to ₹60,000 for taxable income up to ₹12 Lakhs (net tax nil up to ₹12L taxable, or ₹12.75L salaried).</p>"
            ),
            "Financial Ratios for Small Business": (
                "<h1>Key Financial Ratios & KPIs</h1>"
                "<ul>"
                "<li><b>Current Ratio (Working Capital)</b> = Current Assets ÷ Current Liabilities (Target &gt; 1.5)</li>"
                "<li><b>Debt-to-Income (DTI)</b> = Total Monthly Loan EMIs ÷ Monthly Income (Target &lt; 30%)</li>"
                "<li><b>Inventory Turnover Ratio</b> = Cost of Goods Sold ÷ Average Inventory</li>"
                "<li><b>Gross Profit Margin</b> = ((Revenue - COGS) ÷ Revenue) × 100%</li>"
                "</ul>"
            ),
        }
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        splitter = QSplitter(Qt.Horizontal)

        self.list_widget = QListWidget()
        for title in self.articles.keys():
            item = QListWidgetItem(title)
            self.list_widget.addItem(item)

        # Fix signal bindings: bind currentItemChanged AND itemClicked AND currentTextChanged
        self.list_widget.currentTextChanged.connect(self.display_article)
        self.list_widget.itemClicked.connect(lambda item: self.display_article(item.text()))

        self.browser = QTextBrowser()
        self.browser.setStyleSheet(
            "background-color: #FFFFFF; color: #1F2937; border-radius: 12px; padding: 20px; font-size: 14px;"
        )

        splitter.addWidget(self.list_widget)
        splitter.addWidget(self.browser)
        splitter.setSizes([300, 700])

        layout.addWidget(splitter)

        # Select first article by default
        if self.articles:
            self.list_widget.setCurrentRow(0)

    def display_article(self, title: str):
        if not title:
            return
        content = self.articles.get(title, "<h1>Article Not Found</h1><p>Select a topic from the left sidebar to view documentation.</p>")
        self.browser.setHtml(content)
