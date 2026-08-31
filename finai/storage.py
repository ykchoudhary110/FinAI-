from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "finai.db"


def connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, kind TEXT NOT NULL,
        input_json TEXT NOT NULL, result_json TEXT NOT NULL, previous_hash TEXT NOT NULL, audit_hash TEXT NOT NULL
    )""")
    return conn


def save(kind: str, user_input: dict, result: dict) -> dict:
    with connection() as conn:
        previous = conn.execute("SELECT audit_hash FROM transactions ORDER BY id DESC LIMIT 1").fetchone()
        previous_hash = previous["audit_hash"] if previous else "GENESIS"
        created_at = datetime.now(timezone.utc).isoformat()
        canonical = json.dumps({"created_at": created_at, "kind": kind, "input": user_input, "result": result, "previous": previous_hash}, sort_keys=True, separators=(",", ":"))
        audit_hash = hashlib.sha256(canonical.encode()).hexdigest()
        cursor = conn.execute("INSERT INTO transactions (created_at, kind, input_json, result_json, previous_hash, audit_hash) VALUES (?, ?, ?, ?, ?, ?)", (created_at, kind, json.dumps(user_input), json.dumps(result), previous_hash, audit_hash))
        return {"id": cursor.lastrowid, "created_at": created_at, "hash": audit_hash, "previous_hash": previous_hash}


def history(limit: int = 100) -> list[dict]:
    with connection() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT ?", (limit,))]
