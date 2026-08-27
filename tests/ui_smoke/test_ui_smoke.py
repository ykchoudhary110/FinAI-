import pytest
from PySide6.QtCore import Qt
from finai.presentation.app_shell import FinAIAppShell


def test_ui_app_launch_and_all_14_pages(qtbot):
    window = FinAIAppShell()
    qtbot.addWidget(window)
    window.show()

    assert window.isVisible()
    assert window.stacked_widget.count() == 14

    # Test navigating through all 14 pages
    for i in range(14):
        window.stacked_widget.setCurrentIndex(i)
        assert window.stacked_widget.currentIndex() == i
        page = window.stacked_widget.currentWidget()
        assert page is not None


def test_ui_calculator_and_search_pages(qtbot):
    window = FinAIAppShell()
    qtbot.addWidget(window)

    # Test GST calculation on Financial Tools page (Index 2)
    window.stacked_widget.setCurrentIndex(2)
    tools_page = window.stacked_widget.currentWidget()
    tools_page.update_gst()
    assert "Total Payable" in tools_page.gst_result_label.text()

    # Test Search Page (Index 9)
    window.stacked_widget.setCurrentIndex(9)
    search_page = window.stacked_widget.currentWidget()
    search_page.query_input.setText("GST")
    search_page.perform_search()
    assert search_page.table.rowCount() > 0
