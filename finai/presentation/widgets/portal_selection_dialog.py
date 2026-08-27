"""
Portal Selection Gateway Dialog
Renders large, high-visibility interactive square cards for [GST & Business Tax] vs [Personal Income Tax].
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class PortalCardFrame(QFrame):
    clicked = Signal()

    def __init__(self, title: str, subtitle: str, icon_str: str, badge_text: str, accent_color: str, features: list, parent=None):
        super().__init__(parent)
        self.accent_color = accent_color
        self.setFixedSize(430, 370)
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet(f"""
            QFrame#PortalCard {{
                background-color: #FFFFFF;
                border: 2px solid #E2E8F0;
                border-radius: 18px;
            }}
            QFrame#PortalCard:hover {{
                border: 2px solid {accent_color};
                background-color: #FAFCFF;
            }}
        """)
        self.setObjectName("PortalCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # Header Row: Icon & Tag
        top_row = QHBoxLayout()
        lbl_icon = QLabel(icon_str)
        lbl_icon.setStyleSheet("font-size: 38px; background: transparent;")

        lbl_badge = QLabel(f" {badge_text} ")
        lbl_badge.setStyleSheet(f"""
            background-color: #EFF6FF;
            color: {accent_color};
            font-size: 12px;
            font-weight: 800;
            padding: 6px 12px;
            border-radius: 8px;
            border: 1px solid #BFDBFE;
        """)

        top_row.addWidget(lbl_icon)
        top_row.addStretch()
        top_row.addWidget(lbl_badge)
        layout.addLayout(top_row)

        # Main Title
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #0F172A; background: transparent; margin-top: 4px;")
        layout.addWidget(lbl_title)

        # Short description
        lbl_sub = QLabel(subtitle)
        lbl_sub.setWordWrap(True)
        lbl_sub.setStyleSheet("font-size: 13px; font-weight: 600; color: #475569; background: transparent;")
        layout.addWidget(lbl_sub)

        # Bullet features
        feat_box = QVBoxLayout()
        feat_box.setSpacing(6)
        for feat in features:
            f_lbl = QLabel(f"• {feat}")
            f_lbl.setStyleSheet("font-size: 13px; color: #334155; background: transparent; font-weight: 500;")
            feat_box.addWidget(f_lbl)
        layout.addLayout(feat_box)

        layout.addStretch()

        # Action Button
        btn_enter = QPushButton(f"Enter {title} →")
        btn_enter.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 700;
                border-radius: 10px;
                padding: 10px 16px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #1D4ED8;
            }}
        """)
        btn_enter.clicked.connect(self.clicked.emit)
        layout.addWidget(btn_enter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class PortalSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_portal = "GST"
        self.setWindowTitle("FinAI Workstation — Select Compliance Portal")
        self.setFixedSize(980, 580)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setStyleSheet("background-color: #F8FAFC;")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 36, 40, 36)
        layout.setSpacing(24)

        # Header Title
        title_box = QVBoxLayout()
        title_box.setSpacing(6)

        main_title = QLabel("Select Your FinAI Compliance Portal")
        main_title.setAlignment(Qt.AlignCenter)
        main_title.setStyleSheet("font-size: 28px; font-weight: 900; color: #1E3A8A; letter-spacing: -0.02em;")

        sub_title = QLabel("Choose your primary compliance domain to tailor the dashboard, tools, and AI Co-Pilot.")
        sub_title.setAlignment(Qt.AlignCenter)
        sub_title.setStyleSheet("font-size: 15px; color: #64748B; font-weight: 500;")

        title_box.addWidget(main_title)
        title_box.addWidget(sub_title)
        layout.addLayout(title_box)

        # Dual Large Square Cards
        cards_row = QHBoxLayout()
        cards_row.setSpacing(28)

        # Card 1: GST & Business
        card_gst = PortalCardFrame(
            title="[ 🏢 GST & Business ]",
            subtitle="Indirect Tax, Invoicing & Corporate Compliance",
            icon_str="🏢",
            badge_text="INDIRECT TAX & AUDIT",
            accent_color="#2563EB",
            features=[
                "Natural Language HSN/SAC Code Resolver",
                "GSTR-2B ITC Automated Reconciliation",
                "Invoice OCR Scanner & Rule 86B 1% Cash Check",
                "1-Click Official GSTR-3B JSON Exporter"
            ],
            parent=self
        )
        card_gst.clicked.connect(lambda: self.choose_portal("GST"))

        # Card 2: Personal Income Tax
        card_personal = PortalCardFrame(
            title="[ 👤 Personal Tax ]",
            subtitle="Direct Tax, Salary Planning & Max Refunds",
            icon_str="👤",
            badge_text="DIRECT TAX & REFUNDS",
            accent_color="#0D9488",
            features=[
                "Old vs New Regime Auto-Optimizer (Sec 115BAC)",
                "₹60,000 Section 87A Rebate & Section 10(13A) HRA",
                "Section 80C, 80D, 80CCD & Capital Gains (Budget 2024)",
                "1-Click Official ITR-1 / ITR-4 JSON Exporter"
            ],
            parent=self
        )
        card_personal.clicked.connect(lambda: self.choose_portal("PERSONAL_TAX"))

        cards_row.addWidget(card_gst)
        cards_row.addWidget(card_personal)
        layout.addLayout(cards_row)

    def choose_portal(self, portal_name: str):
        self.selected_portal = portal_name
        self.accept()
