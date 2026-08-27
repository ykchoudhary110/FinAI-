import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import QMessageBox


def setup_global_crash_handler():
    """
    Sets sys.excepthook to capture unhandled exceptions, write local crash logs,
    and present a friendly recovery dialog.
    """
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        crash_dir = Path(local_appdata) / "FinAI" / "crash_logs"
        crash_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = crash_dir / f"crash_{timestamp}.log"

        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        try:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"FinAI Unhandled Crash Log - {datetime.now().isoformat()}\n")
                f.write("=" * 60 + "\n")
                f.write(error_msg)
        except Exception:
            pass

        # User-facing Friendly Recovery Dialog
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("FinAI Application Notice")
        msg_box.setText("An unexpected error occurred.")
        msg_box.setInformativeText(
            f"FinAI saved a local crash log to:\n{log_file}\n\n"
            "Your database and offline data remain completely safe."
        )
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    sys.excepthook = handle_exception
