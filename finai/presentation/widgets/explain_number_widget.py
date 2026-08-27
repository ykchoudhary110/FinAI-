from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QWidget


class ExplainableNumberLabel(QLabel):
    """
    Clickable component wrapping any calculated figure in the UI.
    Emits explain_requested signal packaging {figure_id, computed_value, formula_name, raw_inputs, formula_version}.
    """
    explain_requested = Signal(dict)

    def __init__(
        self,
        figure_id: str,
        computed_value: float,
        formula_name: str,
        raw_inputs: dict,
        formula_version: str = "v1.0",
        parent=None,
    ):
        super().__init__(parent)
        self.context = {
            "figure_id": figure_id,
            "computed_value": computed_value,
            "formula_name": formula_name,
            "raw_inputs": raw_inputs,
            "formula_version": formula_version,
        }
        self.setText(f"₹{computed_value:,.2f} [?]")
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            "font-family: 'Consolas', monospace; font-weight: bold; color: #005FB8; border-bottom: 1px dashed #005FB8; padding: 2px;"
        )
        self.setToolTip("Click to ask FinAI to explain this calculated figure in detail.")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.explain_requested.emit(self.context)
        super().mousePressEvent(event)
