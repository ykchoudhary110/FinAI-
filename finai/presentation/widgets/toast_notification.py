from PySide6.QtCore import QPoint, QPropertyAnimation, QTimer, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class ToastNotificationWidget(QFrame):
    """
    Pro-App Floating Glass Toast Notification Widget.
    Displays in the bottom-right corner of the window with auto-dismiss.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(
            """
            QFrame {
                background-color: rgba(255, 255, 255, 0.98);
                border: 1px solid #2563EB;
                border-left: 5px solid #2563EB;
                border-radius: 10px;
                padding: 8px;
            }
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 16, 10)
        layout.setSpacing(10)

        self.icon_lbl = QLabel("ℹ️")
        self.icon_lbl.setStyleSheet("font-size: 18px;")

        text_box = QVBoxLayout()
        self.title_lbl = QLabel("Notification")
        self.title_lbl.setStyleSheet("font-weight: bold; font-size: 13px; color: #2563EB;")

        self.msg_lbl = QLabel("Action completed successfully.")
        self.msg_lbl.setStyleSheet("font-size: 12px; color: #111827;")

        text_box.addWidget(self.title_lbl)
        text_box.addWidget(self.msg_lbl)

        layout.addWidget(self.icon_lbl)
        layout.addLayout(text_box)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

    def show_toast(self, title: str, message: str = "", icon: str = "✅", duration_ms: int = 3000):
        # Handle overloaded calls e.g. show_toast("Message text", 3500)
        if isinstance(message, (int, float)):
            duration_ms = int(message)
            message = ""

        self.title_lbl.setText(str(title))
        if message:
            self.msg_lbl.setText(str(message))
            self.msg_lbl.setVisible(True)
        else:
            self.msg_lbl.setText("")
            self.msg_lbl.setVisible(False)

        self.icon_lbl.setText(str(icon))
        self.adjustSize()

        if self.parentWidget():
            p_geom = self.parentWidget().geometry()
            x = p_geom.width() - self.width() - 25
            y = p_geom.height() - self.height() - 35
            self.move(x, y)

        self.show()
        self.raise_()
        self.timer.start(duration_ms)
