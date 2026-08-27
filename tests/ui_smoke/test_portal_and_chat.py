import pytest
from PySide6.QtCore import Qt
from finai.application.orchestration.pipeline import OrchestrationPipeline
from finai.presentation.app_shell import FinAIAppShell
from finai.presentation.pages.ai_chat_page import AIChatPage
from finai.presentation.pages.dashboard_page import DashboardPage
from finai.presentation.widgets.portal_selection_dialog import PortalSelectionDialog
from finai.presentation.widgets.toast_notification import ToastNotificationWidget


def test_portal_selection_dialog(qtbot):
    dlg = PortalSelectionDialog()
    qtbot.addWidget(dlg)
    dlg.show()
    assert dlg.isVisible()

    # Choose GST
    dlg.choose_portal("GST")
    assert dlg.selected_portal == "GST"

    # Choose Personal Tax
    dlg.choose_portal("PERSONAL_TAX")
    assert dlg.selected_portal == "PERSONAL_TAX"


def test_dashboard_adaptive_mode(qtbot):
    dash = DashboardPage()
    qtbot.addWidget(dash)
    dash.show()

    # Switch to GST
    dash.set_portal_mode("GST")
    assert "GST" in dash.header.text()
    assert "Taxable Turnover" in dash.t2_val.text()

    # Switch to Personal Tax
    dash.set_portal_mode("PERSONAL_TAX")
    assert "Personal" in dash.header.text()
    assert "Gross CTC" in dash.t2_val.text()


def test_toast_notification_overloads(qtbot):
    toast = ToastNotificationWidget()
    qtbot.addWidget(toast)

    # Standard call
    toast.show_toast("Title", "Message", "✅", 1000)
    assert toast.title_lbl.text() == "Title"

    # Overloaded 2-arg call where 2nd arg is duration
    toast.show_toast("Only Title", 2500)
    assert toast.title_lbl.text() == "Only Title"


def test_ai_chat_page_hsn_and_billing(qtbot):
    pipeline = OrchestrationPipeline()
    chat_page = AIChatPage(pipeline=pipeline)
    qtbot.addWidget(chat_page)
    chat_page.show()

    # Test HSN Query
    chat_page.input_field.setText("What is the HSN code for wireless mouse?")
    chat_page.send_message()
    assert chat_page.msg_layout.count() >= 3

    # Test Conversational Billing
    chat_page.input_field.setText("I sold 5 monitors for 75000 to Mumbai client")
    chat_page.send_message()
    assert chat_page.msg_layout.count() >= 5

    # Test Tax Optimizer Query
    chat_page.input_field.setText("My salary is 1800000. How to maximize tax refund?")
    chat_page.send_message()
    assert chat_page.msg_layout.count() >= 7
