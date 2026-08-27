from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)


class NotificationTrayWidget(QToolButton):
    def __init__(self, nudge_engine=None, parent=None):
        super().__init__(parent)
        self.nudge_engine = nudge_engine
        self.setText("Nudges (0)")
        self.setStyleSheet("background: #F3F4F6; color: #1F2937; border-radius: 6px; padding: 4px 8px;")
        self.setPopupMode(QToolButton.InstantPopup)

        self.menu = QMenu(self)
        self.setMenu(self.menu)
        self.refresh_nudges()

    def refresh_nudges(self):
        self.menu.clear()

        nudges = self.nudge_engine.get_active_nudges() if self.nudge_engine else []
        self.setText(f"Nudges ({len(nudges)})")

        if not nudges:
            action = self.menu.addAction("No pending financial nudges")
            action.setEnabled(False)
            return

        for n in nudges:
            card = QFrame()
            card.setStyleSheet("background: #FFFFFF; border: 1px solid #E5E5E5; border-radius: 8px; padding: 10px; margin: 4px;")
            l = QVBoxLayout(card)

            t_lbl = QLabel(f"<b>{n['title']}</b>")
            m_lbl = QLabel(n['message'])
            m_lbl.setWordWrap(True)

            btn_dismiss = QPushButton("Dismiss")
            btn_dismiss.setStyleSheet("padding: 4px 8px; font-size: 11px;")
            n_id = n["id"]
            btn_dismiss.clicked.connect(lambda _, nid=n_id: self.dismiss_nudge(nid))

            l.addWidget(t_lbl)
            l.addWidget(m_lbl)
            l.addWidget(btn_dismiss, alignment=Qt.AlignRight)

            wa = QWidgetAction(self.menu)
            wa.setDefaultWidget(card)
            self.menu.addAction(wa)

    def dismiss_nudge(self, nudge_id: int):
        if self.nudge_engine:
            self.nudge_engine.dismiss_nudge(nudge_id)
            self.refresh_nudges()
