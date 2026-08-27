import base64
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def derive_key_from_passphrase(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode("utf-8")))


def create_encrypted_backup(
    db_path: Path,
    receipts_dir: Path,
    output_backup_file: Path,
    passphrase: str,
):
    """
    Exports SQLite database + receipts directory into an encrypted zip archive.
    Uses PBKDF2HMAC + Fernet AES encryption per Section 9 of FinAI Specification.
    """
    if not passphrase or len(passphrase) < 4:
        raise ValueError("Passphrase must be at least 4 characters long.")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_zip_path = Path(tmp_dir) / "data.zip"
        
        with zipfile.ZipFile(tmp_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            if db_path.exists():
                zipf.write(db_path, arcname="finai.db")
            if receipts_dir.exists():
                for root, _, files in os.walk(receipts_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = Path("receipts") / file_path.relative_to(receipts_dir)
                        zipf.write(file_path, arcname=arcname)

        with open(tmp_zip_path, "rb") as f:
            unencrypted_data = f.read()

        salt = os.urandom(16)
        key = derive_key_from_passphrase(passphrase, salt)
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(unencrypted_data)

        output_backup_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_backup_file, "wb") as f:
            f.write(salt + encrypted_data)


def restore_encrypted_backup(
    backup_file: Path,
    target_db_path: Path,
    target_receipts_dir: Path,
    passphrase: str,
):
    """
    Decrypts and restores backup file.
    """
    if not backup_file.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_file}")

    with open(backup_file, "rb") as f:
        content = f.read()

    if len(content) < 16:
        raise ValueError("Invalid backup file format.")

    salt = content[:16]
    encrypted_data = content[16:]

    key = derive_key_from_passphrase(passphrase, salt)
    fernet = Fernet(key)

    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except Exception as e:
        raise ValueError("Decryption failed. Incorrect passphrase or corrupted backup file.") from e

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_zip_path = Path(tmp_dir) / "data.zip"
        with open(tmp_zip_path, "wb") as f:
            f.write(decrypted_data)

        with zipfile.ZipFile(tmp_zip_path, "r") as zipf:
            zipf.extractall(tmp_dir)

        restored_db = Path(tmp_dir) / "finai.db"
        if restored_db.exists():
            target_db_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(restored_db, target_db_path)

        restored_receipts = Path(tmp_dir) / "receipts"
        if restored_receipts.exists():
            target_receipts_dir.mkdir(parents=True, exist_ok=True)
            for file in restored_receipts.glob("*"):
                if file.is_file():
                    shutil.copy2(file, target_receipts_dir / file.name)
