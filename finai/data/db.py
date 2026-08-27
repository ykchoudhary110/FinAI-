import os
import sqlite3
from pathlib import Path
from typing import Optional


class DatabaseManager:
    """
    Manages SQLite connection and versioned migration runner.
    Configured with WAL mode (PRAGMA journal_mode=WAL) for high concurrency.
    Stores DB file under %LOCALAPPDATA%/FinAI/finai.db.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
            app_dir = Path(local_appdata) / "FinAI"
            app_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = app_dir / "finai.db"

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for high performance & concurrency
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def init_database(self):
        """Runs numbered .sql migration files in order."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Ensure schema_version table exists
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.commit()

        cursor.execute("SELECT MAX(version) FROM schema_version")
        row = cursor.fetchone()
        current_version = row[0] if row[0] is not None else 0

        migrations_dir = Path(__file__).parent / "migrations"
        if not migrations_dir.exists():
            conn.close()
            return

        sql_files = sorted(migrations_dir.glob("*.sql"))

        for sql_file in sql_files:
            filename = sql_file.name
            try:
                version_num = int(filename.split("_")[0])
            except ValueError:
                continue

            if version_num > current_version:
                with open(sql_file, "r", encoding="utf-8") as f:
                    sql_script = f.read()

                cursor.executescript(sql_script)
                cursor.execute(
                    "INSERT INTO schema_version (version) VALUES (?)", (version_num,)
                )
                conn.commit()

        conn.close()
