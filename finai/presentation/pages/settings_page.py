from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from finai.data.backup.backup_service import create_encrypted_backup, restore_encrypted_backup
from finai.domain.rules.audit_trail import GLOBAL_AUDIT_LEDGER
from finai.presentation.theme.styles import PRIMARY, SUCCESS, TEXT_PRIMARY, TEXT_SECONDARY


class SettingsPage(QWidget):
    """
    Application Settings & Cryptographic Audit Security Page.
    Features: Scoped QFrame.Card styles preventing QSS label inheritance issues,
    high-contrast dark typography (#0F172A), interactive SHA-256 audit verification,
    AES-256 encrypted local backup & restore.
    """

    def __init__(self, db_manager=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        header = QLabel("Application Settings & Audit Security")
        header.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {TEXT_PRIMARY}; letter-spacing: -0.02em;")
        layout.addWidget(header)

        combo_qss = (
            "QComboBox { background-color: #F8FAFC; color: #0F172A; font-weight: 600; font-size: 13px; "
            "border: 1px solid #CBD5E1; border-radius: 8px; padding: 6px 12px; } "
            "QComboBox QAbstractItemView { background-color: #FFFFFF; color: #0F172A; selection-background-color: #2563EB; selection-color: #FFFFFF; }"
        )
        input_qss = (
            "QLineEdit { background-color: #F8FAFC; color: #0F172A; font-weight: 500; font-size: 13px; "
            "border: 1px solid #CBD5E1; border-radius: 8px; padding: 6px 12px; }"
        )
        btn_primary_qss = (
            "QPushButton { background-color: #2563EB; color: #FFFFFF; font-weight: 600; font-size: 13px; "
            "border-radius: 8px; padding: 8px 16px; border: none; } "
            "QPushButton:hover { background-color: #1D4ED8; }"
        )

        # 1. Audit Trail Security Card (SHA-256 Hash-Chain)
        audit_card = QFrame()
        audit_card.setProperty("class", "Card")
        audit_card.setStyleSheet("QFrame.Card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; }")
        a_layout = QVBoxLayout(audit_card)
        a_layout.setContentsMargins(20, 20, 20, 20)
        a_layout.setSpacing(10)

        a_title = QLabel("Cryptographic Calculation Audit Trail (SHA-256 Hash Chain)")
        a_title.setStyleSheet("font-weight: 700; font-size: 16px; color: #0F172A;")

        a_desc = QLabel("Every rule engine calculation is logged into an append-only cryptographic hash chain. Recomputing the chain verifies 100% data integrity against local tampering.")
        a_desc.setStyleSheet("font-size: 13px; color: #475569;")

        btn_verify_audit = QPushButton("Verify Audit Trail Integrity")
        btn_verify_audit.setFixedWidth(240)
        btn_verify_audit.setStyleSheet(btn_primary_qss)
        btn_verify_audit.clicked.connect(self.verify_audit_trail)

        self.audit_status_lbl = QLabel("Ledger Status: Ready for verification")
        self.audit_status_lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {PRIMARY};")

        a_layout.addWidget(a_title)
        a_layout.addWidget(a_desc)
        a_layout.addWidget(btn_verify_audit)
        a_layout.addWidget(self.audit_status_lbl)
        layout.addWidget(audit_card)

        # 2. Performance & AI Mode Card
        perf_card = QFrame()
        perf_card.setProperty("class", "Card")
        perf_card.setStyleSheet("QFrame.Card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; }")
        p_layout = QFormLayout(perf_card)
        p_layout.setContentsMargins(20, 20, 20, 20)
        p_layout.setSpacing(14)

        p_title = QLabel("AI Model & Performance Configuration")
        p_title.setStyleSheet("font-weight: 700; font-size: 16px; color: #0F172A; margin-bottom: 4px;")

        lbl_perf = QLabel("AI Performance Mode:")
        lbl_perf.setStyleSheet("color: #0F172A; font-weight: 600; font-size: 14px;")
        self.perf_combo = QComboBox()
        self.perf_combo.setStyleSheet(combo_qss)
        self.perf_combo.addItems(["Balanced Mode (Default - Qwen 2.5 3B)", "Lite Mode (Shorter prompts for low RAM)"])

        lbl_model = QLabel("Local Ollama Model:")
        lbl_model.setStyleSheet("color: #0F172A; font-weight: 600; font-size: 14px;")
        self.model_combo = QComboBox()
        self.model_combo.setStyleSheet(combo_qss)
        self.model_combo.addItems(["qwen2.5:3b (Recommended)", "qwen2.5:1.5b", "llama3.2:3b"])

        p_layout.addRow(p_title)
        p_layout.addRow(lbl_perf, self.perf_combo)
        p_layout.addRow(lbl_model, self.model_combo)

        layout.addWidget(perf_card)

        # 3. Encrypted Backup Card
        backup_card = QFrame()
        backup_card.setProperty("class", "Card")
        backup_card.setStyleSheet("QFrame.Card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; }")
        b_layout = QFormLayout(backup_card)
        b_layout.setContentsMargins(20, 20, 20, 20)
        b_layout.setSpacing(14)

        b_title = QLabel("Encrypted Local Backup & Restore (Fernet AES + PBKDF2)")
        b_title.setStyleSheet("font-weight: 700; font-size: 16px; color: #0F172A; margin-bottom: 2px;")

        b_sub = QLabel("Export an encrypted ZIP archive containing all SQLite DB records and OCR documents, secured with PBKDF2 key derivation.")
        b_sub.setStyleSheet("font-size: 13px; color: #475569; margin-bottom: 6px;")

        lbl_pwd = QLabel("Backup Passphrase:")
        lbl_pwd.setStyleSheet("color: #0F172A; font-weight: 600; font-size: 14px;")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("Enter passphrase for backup encryption")
        self.pass_input.setStyleSheet(input_qss)

        btn_export = QPushButton("Export Encrypted Backup")
        btn_export.setStyleSheet(btn_primary_qss)
        btn_export.setFixedWidth(200)
        btn_export.clicked.connect(self.export_backup)

        btn_import = QPushButton("Restore Backup")
        btn_import.setStyleSheet("QPushButton { background-color: #F1F5F9; color: #0F172A; font-weight: 600; font-size: 13px; border-radius: 8px; padding: 8px 16px; border: 1px solid #CBD5E1; } QPushButton:hover { background-color: #E2E8F0; }")
        btn_import.setFixedWidth(200)
        btn_import.clicked.connect(self.import_backup)

        btn_row = QHBoxLayout()
        btn_row.addWidget(btn_export)
        btn_row.addWidget(btn_import)
        btn_row.addStretch()

        b_layout.addRow(b_title)
        b_layout.addRow(b_sub)
        b_layout.addRow(lbl_pwd, self.pass_input)
        b_layout.addRow(btn_row)

        layout.addWidget(backup_card)
        layout.addStretch()

    def verify_audit_trail(self):
        GLOBAL_AUDIT_LEDGER.log_calculation(
            "AUDIT_INTEGRITY_CHECK",
            {"initiator": "SettingsPage"},
            {"status": "Verification Executed"}
        )
        is_valid, checked_count, latest_hash = GLOBAL_AUDIT_LEDGER.verify_integrity()

        if is_valid:
            msg = (
                f"Calculation Audit Trail Verified!\n\n"
                f"Status: Intact & Valid (SHA-256 Hash Chain)\n"
                f"Total Checked Blocks: {checked_count}\n"
                f"Genesis Hash: {'0'*64}\n"
                f"Latest Block Hash: {latest_hash[:32]}..."
            )
            self.audit_status_lbl.setText(f"Ledger Status: Intact ({checked_count} blocks verified)")
            self.audit_status_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {SUCCESS};")
            QMessageBox.information(self, "Audit Trail Verified", msg)
        else:
            self.audit_status_lbl.setText("Ledger Status: TAMPER DETECTED!")
            self.audit_status_lbl.setStyleSheet("font-size: 13px; font-weight: 700; color: #DC2626;")
            QMessageBox.critical(self, "Tamper Detected", "Warning: Calculation log hash chain has been altered!")

    def export_backup(self):
        pwd = self.pass_input.text().strip()
        if len(pwd) < 4:
            QMessageBox.warning(self, "Invalid Passphrase", "Passphrase must be at least 4 characters long.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save Backup File", "finai_backup.finai", "FinAI Backup (*.finai)")
        if path and self.db_manager:
            create_encrypted_backup(
                db_path=self.db_manager.db_path,
                receipts_dir=self.db_manager.db_path.parent / "receipts",
                output_backup_file=Path(path),
                passphrase=pwd,
            )
            QMessageBox.information(self, "Backup Success", f"Encrypted backup saved to:\n{path}")

    def import_backup(self):
        pwd = self.pass_input.text().strip()
        if len(pwd) < 4:
            QMessageBox.warning(self, "Invalid Passphrase", "Passphrase must be at least 4 characters long.")
            return

        path, _ = QFileDialog.getOpenFileName(self, "Select Backup File", "", "FinAI Backup (*.finai)")
        if path and self.db_manager:
            try:
                restore_encrypted_backup(
                    backup_file=Path(path),
                    target_db_path=self.db_manager.db_path,
                    target_receipts_dir=self.db_manager.db_path.parent / "receipts",
                    passphrase=pwd,
                )
                QMessageBox.information(self, "Restore Success", "Database restored successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Restore Failed", str(e))
