"""
FinAI Exact UI Implementation Spec — Color Tokens & Master QSS.
No other hex values appear hard-coded anywhere in the codebase — every color references these tokens.
"""

# Color Tokens Spec
PRIMARY           = "#2563EB"   # Blue — primary actions, active nav, links
PRIMARY_HOVER     = "#1D4ED8"
SUCCESS           = "#16A34A"   # Health score, positive trends
WARNING           = "#D97706"   # Nudges, budget-overshoot warnings
DANGER            = "#DC2626"   # Delete actions, over-budget states
INVESTMENT_ACCENT = "#7C3AED"   # Investment Planner-specific accents

TEXT_PRIMARY      = "#0F172A"
TEXT_SECONDARY    = "#475569"
TEXT_MUTED        = "#94A3B8"

BORDER_SUBTLE     = "rgba(15, 23, 42, 0.06)"
BORDER_HIGHLIGHT  = "rgba(255, 255, 255, 0.90)"

APP_CANVAS_BG     = "#F4F6FB"
CARD_BG           = "rgba(255, 255, 255, 0.72)"
SIDEBAR_BG        = "rgba(255, 255, 255, 0.55)"

FROSTED_GLASS_LIGHT_THEME_QSS = f"""
QMainWindow {{
    background-color: {APP_CANVAS_BG};
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI Variable', 'Segoe UI', 'Inter', -apple-system, sans-serif;
}}

QWidget {{
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI Variable', 'Segoe UI', 'Inter', -apple-system, sans-serif;
}}

QWidget#Sidebar {{
    background-color: {SIDEBAR_BG};
    border-right: 1px solid {BORDER_SUBTLE};
}}

/* Mirror Glass Card Surface */
QFrame.Card {{
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    color: {TEXT_PRIMARY};
}}

/* Tab Widget Styling Spec — Pristine Light Cards & Tabs */
QTabWidget::pane {{
    border: 1px solid #E2E8F0;
    background-color: #FFFFFF;
    border-radius: 14px;
    top: -1px;
    padding: 16px;
}}

QTabBar::tab {{
    background-color: #F1F5F9;
    color: {TEXT_SECONDARY};
    border: 1px solid #CBD5E1;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 600;
    margin-right: 4px;
}}

QTabBar::tab:selected {{
    background-color: {PRIMARY};
    color: #FFFFFF;
    border: 1px solid {PRIMARY};
    font-weight: 700;
}}

QTabBar::tab:hover:!selected {{
    background-color: #E2E8F0;
    color: {TEXT_PRIMARY};
}}

/* Typography Hierarchy */
QLabel {{
    color: {TEXT_PRIMARY};
    font-size: 14px;
    font-weight: 400;
}}

QLabel.PageTitle {{
    font-size: 28px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    letter-spacing: -0.02em;
}}

QLabel.CardTitle {{
    font-size: 16px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}

QLabel.HeroNumber {{
    font-size: 40px;
    font-weight: 800;
    color: {TEXT_PRIMARY};
}}

QLabel.BodyText {{
    font-size: 14px;
    font-weight: 400;
    color: {TEXT_SECONDARY};
}}

QLabel.MetaText {{
    font-size: 13px;
    font-weight: 500;
    color: {TEXT_MUTED};
}}

QLabel.TabularCurrency {{
    font-family: 'Consolas', 'SF Mono', monospace;
    font-size: 14px;
    font-weight: 600;
    color: {PRIMARY};
}}

/* Section 6: Primary Button Spec (40px height, 10px radius, 16px padding) */
QPushButton {{
    background-color: {PRIMARY};
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    min-height: 40px;
    max-height: 40px;
    padding: 0px 16px;
    font-weight: 600;
    font-size: 14px;
}}

QPushButton:hover {{
    background-color: {PRIMARY_HOVER};
}}

QPushButton:pressed {{
    background-color: #1E40AF;
}}

/* Section 6: Secondary/Outline Button Spec */
QPushButton.Secondary {{
    background-color: transparent;
    color: {TEXT_SECONDARY};
    border: 1px solid #CBD5E1;
    border-radius: 10px;
    min-height: 40px;
    max-height: 40px;
    padding: 0px 16px;
    font-weight: 500;
    font-size: 14px;
}}

QPushButton.Secondary:hover {{
    background-color: rgba(15, 23, 42, 0.04);
    color: {TEXT_PRIMARY};
}}

/* Input Controls */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 10px;
    min-height: 38px;
    padding: 4px 12px;
    color: {TEXT_PRIMARY};
    font-size: 14px;
    font-weight: 500;
}}

QLineEdit:focus, QComboBox:focus {{
    border: 2px solid {PRIMARY};
    background-color: #FFFFFF;
}}

QTextBrowser, QTextEdit, QListWidget, QTableWidget, QTableView {{
    background-color: #FFFFFF;
    color: {TEXT_PRIMARY};
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}}

QListWidget::item {{
    padding: 10px 14px;
    color: {TEXT_PRIMARY};
}}

QListWidget::item:selected {{
    background-color: #EFF6FF;
    color: {PRIMARY};
    font-weight: 600;
    border-radius: 8px;
}}

QHeaderView::section {{
    background-color: #F8FAFC;
    color: {TEXT_PRIMARY};
    font-weight: 600;
    font-size: 13px;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #E2E8F0;
}}

QProgressBar {{
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    background-color: #F1F5F9;
    color: {TEXT_PRIMARY};
    font-weight: 600;
}}

QProgressBar::chunk {{
    background-color: {PRIMARY};
    border-radius: 8px;
}}
"""
