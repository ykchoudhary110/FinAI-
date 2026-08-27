from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget


class SplashScreen(QWidget):
    startup_finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        self.setFixedSize(500, 300)
        self.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.92); "
            "border: 1px solid rgba(0, 95, 184, 0.30); "
            "border-radius: 16px; color: #1F2937;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 40)

        title = QLabel("FinAI")
        title.setStyleSheet("font-size: 38px; font-weight: 800; color: #005FB8;")
        subtitle = QLabel("Offline Financial AI Assistant (Premium Glass Edition)")
        subtitle.setStyleSheet("font-size: 13px; color: #4B5563; font-weight: 500;")

        self.status_lbl = QLabel("Initializing system...")
        self.status_lbl.setStyleSheet("font-size: 12px; color: #6B7280; margin-top: 20px;")

        self.pbar = QProgressBar()
        self.pbar.setRange(0, 100)
        self.pbar.setValue(0)
        self.pbar.setStyleSheet(
            "QProgressBar { border: 1px solid #E5E7EB; background: #F3F4F6; border-radius: 6px; text-align: center; } "
            "QProgressBar::chunk { background: #005FB8; border-radius: 6px; }"
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        layout.addWidget(self.status_lbl)
        layout.addWidget(self.pbar)

        self.steps = [
            (25, "Checking local Ollama installation..."),
            (50, "Opening SQLite database (%LOCALAPPDATA%\\FinAI)..."),
            (75, "Executing versioned schema migrations (.sql)..."),
            (100, "Ready! Launching FinAI..."),
        ]
        self.current_step = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance_step)
        self.timer.start(400)

    def advance_step(self):
        if self.current_step < len(self.steps):
            progress, text = self.steps[self.current_step]
            self.pbar.setValue(progress)
            self.status_lbl.setText(text)
            self.current_step += 1
        else:
            self.timer.stop()
            self.startup_finished.emit()
