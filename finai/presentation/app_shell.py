import sys
from pathlib import Path

# Ensure project root is in sys.path for PyInstaller bundled execution
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from PySide6.QtCore import QCoreApplication, QEasingCurve, QPointF, QTimer, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QKeySequence, QPainter, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from finai.application.orchestration.pipeline import OrchestrationPipeline
from finai.application.scheduler.nudge_engine import NudgeEngine
from finai.data.db import DatabaseManager
from finai.data.repositories.expense_repo import ExpenseRepository
from finai.presentation.crash_handler import setup_global_crash_handler
from finai.presentation.pages.about_page import AboutPage
from finai.presentation.pages.ai_chat_page import AIChatPage
from finai.presentation.pages.budget_planner_page import BudgetPlannerPage
from finai.presentation.pages.business_advisor_page import BusinessAdvisorPage
from finai.presentation.pages.dashboard_page import DashboardPage
from finai.presentation.pages.expense_tracker_page import ExpenseTrackerPage
from finai.presentation.pages.financial_reports_page import FinancialReportsPage
from finai.presentation.pages.financial_tools_page import FinancialToolsPage
from finai.presentation.pages.history_page import HistoryPage
from finai.presentation.pages.investment_planner_page import InvestmentPlannerPage
from finai.presentation.pages.knowledge_base_page import KnowledgeBasePage
from finai.presentation.pages.receipt_scanner_page import ReceiptScannerPage
from finai.presentation.pages.search_page import SearchPage
from finai.presentation.pages.settings_page import SettingsPage
from finai.presentation.strings import STRINGS
from finai.presentation.theme.styles import (
    BORDER_SUBTLE,
    FROSTED_GLASS_LIGHT_THEME_QSS,
    PRIMARY,
    SIDEBAR_BG,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from finai.presentation.widgets.app_guide_dialog import AppGuideDialog
from finai.presentation.widgets.command_palette import CommandPaletteDialog
from finai.presentation.widgets.notification_tray import NotificationTrayWidget
from finai.presentation.widgets.portal_selection_dialog import PortalSelectionDialog
from finai.presentation.widgets.toast_notification import ToastNotificationWidget


class MagneticButton(QPushButton):
    """
    Sidebar Navigation Button with Magnetic Mouse Hover per Section 4 Spec:
    - Translates button contents up to 3-4px toward cursor on mouse move.
    - Animates back to (0,0) resting position on leaveEvent using QEasingCurve.OutBack (springy overshoot).
    """

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setMouseTracking(True)
        self._offset_x = 0.0
        self._offset_y = 0.0

        self.reset_anim = QVariantAnimation(self)
        self.reset_anim.setDuration(220)
        self.reset_anim.setEasingCurve(QEasingCurve.OutBack)
        self.reset_anim.valueChanged.connect(self.on_reset_step)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        pos = event.position() if hasattr(event, "position") else QPointF(event.pos())
        center = QPointF(self.width() / 2.0, self.height() / 2.0)
        delta = pos - center

        # Clamp translation to max 3.5px
        self._offset_x = max(-3.5, min(3.5, delta.x() * 0.08))
        self._offset_y = max(-3.5, min(3.5, delta.y() * 0.08))
        self.update()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.reset_anim.stop()
        self.reset_anim.setStartValue(QPointF(self._offset_x, self._offset_y))
        self.reset_anim.setEndValue(QPointF(0.0, 0.0))
        self.reset_anim.start()

    def on_reset_step(self, val):
        if isinstance(val, QPointF):
            self._offset_x = val.x()
            self._offset_y = val.y()
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self._offset_x, self._offset_y)
        super().paintEvent(event)


class FinAIAppShell(QMainWindow):
    """
    Main PySide6 App Shell adhering strictly to Section 2 Sidebar Spec:
    - Width: 260px expanded, 64px collapsed.
    - Floating pill items: 44px tall with Magnetic Hover translation.
    - Active item: Solid PRIMARY (#2563EB) background, white text, 0px 2px 6px rgba(37, 99, 235, 0.35) shadow.
    - Interactive App Guide for step-by-step feature walkthrough with Next/Previous controls.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle(STRINGS["app_name"])
        self.resize(1280, 850)
        self.setMinimumSize(1024, 700)

        # Global Crash Handler
        setup_global_crash_handler()

        # Database & Repositories
        self.db_manager = DatabaseManager()
        self.expense_repo = ExpenseRepository(self.db_manager)
        self.pipeline = OrchestrationPipeline(ollama_client=None)

        # Background Nudge Engine
        self.nudge_engine = NudgeEngine(db_manager=self.db_manager)
        self.nudge_engine.start()

        self.is_sidebar_collapsed = False
        self.recent_pages = []
        self.page_titles = [
            "Dashboard", "AI Chat", "Financial Tools", "Receipt Scanner",
            "Budget Planner", "Expense Tracker", "Investment Planner",
            "Business Advisor", "Financial Reports", "Search", "Knowledge Base",
            "History", "Settings", "About"
        ]

        self.init_ui()
        self.setup_shortcuts()

        # Toast Notification Overlay
        self.toast = ToastNotificationWidget(self)

        # Entrance Modal: Prompt user to choose between [GST] and [Personal Tax]
        if "pytest" not in sys.modules:
            QTimer.singleShot(250, self.open_portal_dialog)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar per Section 2 Spec
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(260)
        self.s_layout = QVBoxLayout(self.sidebar)
        self.s_layout.setContentsMargins(12, 16, 12, 16)
        self.s_layout.setSpacing(4)

        # App Brand Title & Collapse Toggle
        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(12, 0, 12, 8)

        self.logo_lbl = QLabel("FinAI")
        self.logo_lbl.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {PRIMARY}; letter-spacing: -0.02em;")

        self.toggle_btn = QPushButton("≡")
        self.toggle_btn.setFixedWidth(32)
        self.toggle_btn.setToolTip("Toggle Sidebar (Ctrl+B)")
        self.toggle_btn.setStyleSheet(f"background: transparent; color: {TEXT_SECONDARY}; font-size: 16px; font-weight: bold; border: none; min-height: 32px; max-height: 32px;")
        self.toggle_btn.clicked.connect(self.toggle_sidebar)

        brand_row.addWidget(self.logo_lbl)
        brand_row.addStretch()
        brand_row.addWidget(self.toggle_btn)
        self.s_layout.addLayout(brand_row)
        self.s_layout.addSpacing(6)

        # Simplified Core Navigation Items (Clean, uncluttered CA Pro UI)
        self.nav_buttons = []
        nav_items = [
            ("Dashboard", 0),
            ("AI Co-Pilot", 1),
            ("Financial Tools", 2),
            ("Receipt & Invoice OCR", 3),
            ("Audit Reports & Filing", 8),
            ("Settings & Knowledge", 12),
        ]

        for title, idx in nav_items:
            btn = MagneticButton(title)
            btn.setCheckable(True)
            btn.setFixedHeight(44)
            btn.clicked.connect(lambda _, i=idx: self.navigate_to_page(i))
            self.s_layout.addWidget(btn)
            self.nav_buttons.append((btn, title, idx))

        self.s_layout.addStretch()

        # Interactive App Guide Button
        btn_guide = MagneticButton("App Guide")
        btn_guide.setStyleSheet("background-color: #2563EB; color: #FFFFFF; font-weight: 600; font-size: 14px; border-radius: 10px; min-height: 40px; max-height: 40px;")
        btn_guide.clicked.connect(self.open_app_guide)
        self.s_layout.addWidget(btn_guide)

        main_layout.addWidget(self.sidebar)

        # 2. Main Content Area
        content_area = QWidget()
        c_layout = QVBoxLayout(content_area)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(0)

        # Header Frame
        header = QFrame()
        header.setStyleSheet(f"background: rgba(255, 255, 255, 0.80); border-bottom: 1px solid {BORDER_SUBTLE}; padding: 8px 20px;")
        h_layout = QHBoxLayout(header)

        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search data (Ctrl+K)...")
        search_bar.returnPressed.connect(lambda: self.navigate_to_page(9))

        self.btn_portal_switch = MagneticButton("🏢 Active: GST Portal (Switch)")
        self.btn_portal_switch.setStyleSheet("background: #EFF6FF; color: #1D4ED8; border: 1px solid #93C5FD; padding: 0px 16px; font-weight: 800; font-size: 13px; min-height: 36px; max-height: 36px; border-radius: 8px;")
        self.btn_portal_switch.clicked.connect(self.open_portal_dialog)

        btn_palette = MagneticButton("Commands (Ctrl+Shift+P)")
        btn_palette.setStyleSheet(f"background: #EFF6FF; color: {PRIMARY}; border: 1px solid {PRIMARY}; padding: 0px 14px; font-weight: 600; font-size: 13px; min-height: 36px; max-height: 36px; border-radius: 8px;")
        btn_palette.clicked.connect(self.open_command_palette)

        self.notif_tray = NotificationTrayWidget(nudge_engine=self.nudge_engine)

        h_layout.addWidget(search_bar)
        h_layout.addWidget(self.btn_portal_switch)
        h_layout.addWidget(btn_palette)
        h_layout.addWidget(self.notif_tray)
        c_layout.addWidget(header)

        # Top Progress Line
        self.top_progress = QProgressBar()
        self.top_progress.setFixedHeight(3)
        self.top_progress.setTextVisible(False)
        self.top_progress.setStyleSheet(f"QProgressBar {{ background: transparent; border: none; }} QProgressBar::chunk {{ background: {PRIMARY}; }}")
        self.top_progress.setValue(0)
        c_layout.addWidget(self.top_progress)

        # Breadcrumbs Bar
        breadcrumb_bar = QFrame()
        breadcrumb_bar.setStyleSheet(f"background: #F8FAFC; border-bottom: 1px solid {BORDER_SUBTLE}; padding: 4px 20px;")
        b_layout = QHBoxLayout(breadcrumb_bar)
        b_layout.setContentsMargins(20, 4, 20, 4)

        self.breadcrumb_lbl = QLabel("FinAI > Dashboard")
        self.breadcrumb_lbl.setStyleSheet(f"font-size: 13px; color: {TEXT_MUTED}; font-weight: 500;")

        b_layout.addWidget(self.breadcrumb_lbl)
        b_layout.addStretch()
        c_layout.addWidget(breadcrumb_bar)

        # Stacked Pages Widget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(DashboardPage(pipeline=self.pipeline))
        self.stacked_widget.addWidget(AIChatPage(pipeline=self.pipeline))
        self.stacked_widget.addWidget(FinancialToolsPage())
        self.stacked_widget.addWidget(ReceiptScannerPage(expense_repo=self.expense_repo))
        self.stacked_widget.addWidget(BudgetPlannerPage())
        self.stacked_widget.addWidget(ExpenseTrackerPage(expense_repo=self.expense_repo))
        self.stacked_widget.addWidget(InvestmentPlannerPage())
        self.stacked_widget.addWidget(BusinessAdvisorPage())
        self.stacked_widget.addWidget(FinancialReportsPage())
        self.stacked_widget.addWidget(SearchPage(db_manager=self.db_manager))
        self.stacked_widget.addWidget(KnowledgeBasePage())
        self.stacked_widget.addWidget(HistoryPage(db_manager=self.db_manager))
        self.stacked_widget.addWidget(SettingsPage(db_manager=self.db_manager))
        self.stacked_widget.addWidget(AboutPage(on_start_tour=self.open_app_guide))

        self.stacked_widget.currentChanged.connect(self.on_page_changed)
        c_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(content_area)

        # Apply Premium Light Theme
        self.setStyleSheet(FROSTED_GLASS_LIGHT_THEME_QSS)

        # Set initial active sidebar styling
        self.update_sidebar_styles(0)

    def open_app_guide(self):
        """Launches the interactive step-by-step App Guide with Next/Previous page controls."""
        dialog = AppGuideDialog(on_navigate=self.navigate_to_page, parent=self)
        p_geom = self.geometry()
        x = p_geom.x() + (p_geom.width() - dialog.width()) // 2
        y = p_geom.y() + p_geom.height() - dialog.height() - 40
        dialog.move(x, y)
        dialog.exec_()

    def navigate_to_page(self, index: int):
        self.stacked_widget.setCurrentIndex(index)

    def on_page_changed(self, index: int):
        title = self.page_titles[index] if index < len(self.page_titles) else "Page"
        if title not in self.recent_pages:
            self.recent_pages.append(title)
            if len(self.recent_pages) > 4:
                self.recent_pages.pop(0)

        crumb_text = " > ".join(["FinAI"] + self.recent_pages[-3:])
        self.breadcrumb_lbl.setText(crumb_text)
        self.update_sidebar_styles(index)

    def update_sidebar_styles(self, active_index: int):
        for btn, title, idx in self.nav_buttons:
            if idx == active_index:
                btn.setChecked(True)
                btn.setStyleSheet(
                    f"QPushButton {{ background-color: {PRIMARY}; color: #FFFFFF; font-weight: 600; font-size: 14px; border-radius: 10px; padding: 0px 16px; text-align: left; border: none; }}"
                )
                shadow = QGraphicsDropShadowEffect(btn)
                shadow.setBlurRadius(6)
                shadow.setOffset(0, 2)
                shadow.setColor(QColor(37, 99, 235, 90))
                btn.setGraphicsEffect(shadow)
            else:
                btn.setChecked(False)
                btn.setGraphicsEffect(None)
                btn.setStyleSheet(
                    f"QPushButton {{ background-color: transparent; color: {TEXT_SECONDARY}; font-weight: 500; font-size: 14px; border-radius: 10px; padding: 0px 16px; text-align: left; border: none; }} "
                    f"QPushButton:hover {{ background-color: rgba(37, 99, 235, 0.08); color: {PRIMARY}; }}"
                )

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+K"), self, lambda: self.navigate_to_page(9))
        QShortcut(QKeySequence("Ctrl+N"), self, lambda: self.navigate_to_page(1))
        QShortcut(QKeySequence("Ctrl+Shift+P"), self, self.open_command_palette)
        QShortcut(QKeySequence("Ctrl+B"), self, self.toggle_sidebar)
        QShortcut(QKeySequence("Esc"), self, lambda: self.navigate_to_page(0))

    def open_command_palette(self):
        dialog = CommandPaletteDialog(self)
        dialog.action_selected.connect(self.navigate_to_page)
        p_geom = self.geometry()
        dialog.move(p_geom.x() + (p_geom.width() - dialog.width()) // 2, p_geom.y() + 100)
        dialog.exec_()

    def toggle_sidebar(self):
        self.is_sidebar_collapsed = not self.is_sidebar_collapsed
        if self.is_sidebar_collapsed:
            self.sidebar.setFixedWidth(64)
            self.logo_lbl.setText("F")
            for btn, title, idx in self.nav_buttons:
                btn.setText(title[0])
                btn.setToolTip(title)
        else:
            self.sidebar.setFixedWidth(260)
            self.logo_lbl.setText("FinAI")
            for btn, title, idx in self.nav_buttons:
                btn.setText(title)

    def open_portal_dialog(self):
        dlg = PortalSelectionDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            dash_page = self.stacked_widget.widget(0)
            if hasattr(dash_page, "set_portal_mode"):
                dash_page.set_portal_mode(dlg.selected_portal)

            self.navigate_to_page(0)  # Navigate to adapted Dashboard

            if dlg.selected_portal == "GST":
                self.btn_portal_switch.setText("🏢 Active: GST Portal (Switch)")
                self.btn_portal_switch.setStyleSheet("background: #EFF6FF; color: #1D4ED8; border: 1px solid #93C5FD; padding: 0px 16px; font-weight: 800; font-size: 13px; min-height: 36px; max-height: 36px; border-radius: 8px;")
                self.breadcrumb_lbl.setText("FinAI > 🏢 GST & Business Compliance Portal")
                self.toast.show_toast("🏢 GST & Business Portal", "Switched compliance mode to GST and Indirect Taxes.", "🏢", 3500)
            else:
                self.btn_portal_switch.setText("👤 Active: Personal Tax (Switch)")
                self.btn_portal_switch.setStyleSheet("background: #F0FDF4; color: #15803D; border: 1px solid #86EFAC; padding: 0px 16px; font-weight: 800; font-size: 13px; min-height: 36px; max-height: 36px; border-radius: 8px;")
                self.breadcrumb_lbl.setText("FinAI > 👤 Personal Tax & Salary Optimizer")
                self.toast.show_toast("👤 Personal Tax Portal", "Switched compliance mode to Personal Income Tax & Salary.", "👤", 3500)

    def closeEvent(self, event):
        self.nudge_engine.stop()
        super().closeEvent(event)


def main():
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    shell = FinAIAppShell()
    shell.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
