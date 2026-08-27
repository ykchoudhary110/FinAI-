from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class FirstRunWizardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FinAI First-Run Setup Wizard")
        self.resize(480, 320)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("Welcome to FinAI")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #005FB8;")
        sub = QLabel("Select your persona and baseline financial configuration:")
        sub.setStyleSheet("font-size: 13px; color: #4B5563;")

        layout.addWidget(header)
        layout.addWidget(sub)

        form = QFormLayout()
        self.persona_combo = QComboBox()
        self.persona_combo.addItems([
            "Individual / Salaried Professional",
            "Freelancer / Gig Economy",
            "Small Business Owner / MSME Trader",
        ])

        self.income_input = QLineEdit("1200000")
        self.regime_combo = QComboBox()
        self.regime_combo.addItems(["New Tax Regime (Default)", "Old Tax Regime"])

        form.addRow("Financial Persona:", self.persona_combo)
        form.addRow("Annual Income (₹):", self.income_input)
        form.addRow("Preferred Tax Regime:", self.regime_combo)

        layout.addLayout(form)

        btn_finish = QPushButton("Finish Setup & Open Dashboard")
        btn_finish.clicked.connect(self.accept)
        layout.addWidget(btn_finish)
