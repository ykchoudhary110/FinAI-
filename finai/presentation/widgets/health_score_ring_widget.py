from PySide6.QtCore import QEasingCurve, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget
from finai.presentation.theme.styles import SUCCESS, TEXT_MUTED, TEXT_PRIMARY


class HealthScoreRingWidget(QWidget):
    """
    Custom QPainter widget rendering the Financial Health Score ring.
    Phase 9 Spec (Section 2):
    - Compact 145x145 ring size to guarantee >16px clear gap above 'Focus Area' label.
    - Track: #E2E8F0, Progress: SUCCESS (#16A34A), Stroke: 12px round cap.
    - Score number baseline at ~42% height, 'out of 100' at ~58% height (zero text overlap).
    """

    def __init__(self, score: int = 85, focus_area: str = "Savings Rate", parent=None):
        super().__init__(parent)
        self.target_score = max(0, min(100, score))
        self.current_score = 0
        self.focus_area = focus_area
        self.setFixedSize(145, 145)

        # Setup 700ms Count-Up & Fill Animation
        self.anim = QVariantAnimation(self)
        self.anim.setStartValue(0)
        self.anim.setEndValue(self.target_score)
        self.anim.setDuration(700)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.valueChanged.connect(self.on_anim_value_changed)
        self.anim.start()

    def set_score(self, score: int, focus_area: str = ""):
        self.target_score = max(0, min(100, score))
        if focus_area:
            self.focus_area = focus_area
        self.anim.stop()
        self.anim.setStartValue(self.current_score)
        self.anim.setEndValue(self.target_score)
        self.anim.start()

    def on_anim_value_changed(self, value):
        self.current_score = int(value)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        side = min(width, height) - 20
        rect = QRectF((width - side) / 2.0, (height - side) / 2.0, side, side)

        # Track Arc (#E2E8F0, 12px stroke, round caps)
        track_pen = QPen(QColor("#E2E8F0"), 12, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(rect, 225 * 16, -270 * 16)

        # Progress Arc (SUCCESS #16A34A, 12px stroke, round caps)
        score_angle = int((-270.0 * (self.current_score / 100.0)) * 16)
        score_pen = QPen(QColor(SUCCESS), 12, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(score_pen)
        painter.drawArc(rect, 225 * 16, score_angle)

        # Score Number Text
        painter.setPen(QColor(TEXT_PRIMARY))
        font_score = QFont("Segoe UI Variable", 32, QFont.Bold)
        font_score.setStyleStrategy(QFont.PreferAntialias)
        painter.setFont(font_score)

        score_rect = QRectF(
            (width - side) / 2.0,
            (height - side) / 2.0 + (side * 0.16),
            side,
            38,
        )
        painter.drawText(score_rect, Qt.AlignCenter, str(self.current_score))

        # "out of 100" Label
        painter.setPen(QColor(TEXT_MUTED))
        font_sub = QFont("Segoe UI Variable", 11, QFont.Medium)
        painter.setFont(font_sub)

        sub_rect = QRectF(
            (width - side) / 2.0,
            (height - side) / 2.0 + (side * 0.54),
            side,
            20,
        )
        painter.drawText(sub_rect, Qt.AlignCenter, "out of 100")
