from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QWidget
from finai.presentation.theme.styles import INVESTMENT_ACCENT, PRIMARY, SUCCESS, TEXT_PRIMARY, WARNING


class CategoryBarChartWidget(QWidget):
    """
    Custom QPainter widget rendering a horizontal category spend bar chart.
    Uses exact design tokens (PRIMARY, SUCCESS, INVESTMENT_ACCENT, WARNING) and light neutral #E2E8F0 tracks.
    """

    def __init__(self, data: dict = None, parent=None):
        super().__init__(parent)
        self.data = data or {
            "Shopping & Groceries": 18500.0,
            "Rent & Utilities": 32000.0,
            "Dining & Outing": 14200.0,
            "Business Supplies": 8400.0,
        }
        self.setMinimumHeight(160)

    def set_data(self, data: dict):
        self.data = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if not self.data:
            return

        items = list(self.data.items())
        max_val = max(list(self.data.values()) + [1.0])
        bar_height = 18
        spacing = 14
        start_y = 10
        label_width = 150

        colors = [
            QColor(PRIMARY),
            QColor(SUCCESS),
            QColor(INVESTMENT_ACCENT),
            QColor(WARNING),
        ]

        for i, (cat, val) in enumerate(items[:4]):
            y = start_y + i * (bar_height + spacing)

            # Category Label
            painter.setPen(QColor(TEXT_PRIMARY))
            painter.setFont(QFont("Segoe UI Variable", 10, QFont.DemiBold))
            painter.drawText(QRectF(0, y, label_width, bar_height), Qt.AlignLeft | Qt.AlignVCenter, cat)

            # Track Bar Background (#E2E8F0 light neutral track)
            track_width = max(50, self.width() - label_width - 90)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#E2E8F0"))
            painter.drawRoundedRect(QRectF(label_width, y, track_width, bar_height), 4, 4)

            # Fill Bar
            fill_width = max(10, (val / max_val) * track_width)
            painter.setBrush(colors[i % len(colors)])
            painter.drawRoundedRect(QRectF(label_width, y, fill_width, bar_height), 4, 4)

            # Value Label
            painter.setPen(QColor(PRIMARY))
            painter.setFont(QFont("Consolas", 10, QFont.Bold))
            val_text = f"₹{val:,.0f}"
            painter.drawText(
                QRectF(label_width + track_width + 10, y, 80, bar_height),
                Qt.AlignLeft | Qt.AlignVCenter,
                val_text,
            )
