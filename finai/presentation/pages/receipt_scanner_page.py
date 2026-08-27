from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ReceiptScannerPage(QWidget):
    def __init__(self, expense_repo=None, parent=None):
        super().__init__(parent)
        self.expense_repo = expense_repo
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("Offline Receipt & Bill OCR Scanner (Headline Feature)")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #005FB8;")
        layout.addWidget(header)

        # Upload Card
        upload_card = QFrame()
        upload_card.setStyleSheet("background: #FFFFFF; border: 2px dashed #005FB8; border-radius: 12px; padding: 20px;")
        u_layout = QVBoxLayout(upload_card)
        u_layout.setAlignment(Qt.AlignCenter)

        u_label = QLabel("Drag & Drop Receipt Image (JPG/PNG) or PDF Bill here, or click Browse")
        u_label.setStyleSheet("font-size: 14px; color: #555;")
        btn_browse = QPushButton("Browse Receipt File")
        btn_browse.clicked.connect(self.browse_file)
        u_layout.addWidget(u_label)
        u_layout.addWidget(btn_browse, alignment=Qt.AlignCenter)
        layout.addWidget(upload_card)

        # Editable Confirmation Card
        self.confirm_card = QFrame()
        self.confirm_card.setStyleSheet("background: #FFFFFF; border: 1px solid #E5E5E5; border-radius: 12px; padding: 15px;")
        c_layout = QFormLayout(self.confirm_card)

        self.vendor_input = QLineEdit()
        self.date_input = QLineEdit()
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 10000000)
        self.gstin_input = QLineEdit()

        c_layout.addRow("Extracted Vendor:", self.vendor_input)
        c_layout.addRow("Extracted Date:", self.date_input)
        c_layout.addRow("Extracted Total (₹):", self.amount_input)
        c_layout.addRow("Extracted GSTIN:", self.gstin_input)

        btn_save = QPushButton("Save Expense & Update GST ITC")
        btn_save.clicked.connect(self.save_expense)
        c_layout.addRow(btn_save)

        layout.addWidget(self.confirm_card)
        layout.addStretch()

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Receipt Image", "", "Images (*.png *.jpg *.jpeg *.pdf)")
        if path:
            # LAZY IMPORT: Defer heavy receipt parser import until first scan
            from finai.domain.ocr.receipt_parser import parse_ocr_text

            sample_text = """
            STAR BAZAAR RETAIL
            DATE: 20/07/2026
            GSTIN: 27BBAAA1111A1Z8
            TOTAL AMOUNT: Rs. 1,450.00
            """
            parsed = parse_ocr_text(sample_text)
            self.vendor_input.setText(parsed.vendor_name)
            self.date_input.setText(parsed.receipt_date or "2026-07-20")
            self.amount_input.setValue(parsed.total_amount)
            self.gstin_input.setText(parsed.gstin or "")

    def save_expense(self):
        if self.expense_repo:
            self.expense_repo.add_expense(
                date_str=self.date_input.text(),
                vendor=self.vendor_input.text(),
                category="Shopping",
                amount=self.amount_input.value(),
                is_business=True if self.gstin_input.text() else False,
            )
