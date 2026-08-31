"""Official-source registry for the local legal knowledge base.

Internet access is only required when refreshing this registry. Search works offline
against the locally stored snippets after a refresh.
"""
from __future__ import annotations

import html
import re
import sqlite3
import urllib.request
from datetime import datetime, timezone

from finai.storage import DB_PATH

SOURCES = [
    {"title": "Income Tax Department — Current e-filing updates", "url": "https://www.incometax.gov.in/iec/foportal/latest-news", "topic": "income tax, forms, transition"},
    {"title": "Income Tax Department — Income tax returns guidance", "url": "https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/income-tax-returns", "topic": "income tax return filing"},
    {"title": "CBIC — CGST Act, 2017", "url": "https://cbic-gst.gov.in/hindi/CGST-bill-e.html", "topic": "GST act, ITC, CGST"},
    {"title": "CBIC — Central Tax notifications", "url": "https://cbic-gst.gov.in/hindi/central-tax-notifications.html", "topic": "GST notifications"},
    {"title": "GST Portal — GSTR-2B advisory", "url": "https://tutorial.gst.gov.in/offlineutilities/returns/GSTR2B/GSTR-2B_Advisory.pdf", "topic": "GSTR-2B, ITC, GSTR-3B"},
]


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS legal_chunks USING fts5(title, topic, url, content, fetched_at)")
    return conn


def refresh() -> tuple[int, list[str]]:
    saved, errors = 0, []
    with _conn() as conn:
        conn.execute("DELETE FROM legal_chunks")
        for source in SOURCES:
            try:
                request = urllib.request.Request(source["url"], headers={"User-Agent": "FinAI-Offline-Demo/1.0"})
                with urllib.request.urlopen(request, timeout=20) as response:
                    raw = response.read(350_000).decode("utf-8", errors="ignore")
                clean = re.sub(r"<[^>]+>", " ", raw)
                clean = html.unescape(re.sub(r"\s+", " ", clean)).strip()[:10000]
                if len(clean) < 100:
                    raise ValueError("No readable text returned")
                conn.execute("INSERT INTO legal_chunks VALUES (?, ?, ?, ?, ?)", (source["title"], source["topic"], source["url"], clean, datetime.now(timezone.utc).isoformat()))
                saved += 1
            except Exception as exc:
                errors.append(f"{source['title']}: {exc}")
    return saved, errors


def search(query: str) -> list[dict]:
    with _conn() as conn:
        try:
            rows = conn.execute("SELECT title, topic, url, snippet(legal_chunks, 3, '[[', ']]', '…', 28) AS snippet, fetched_at FROM legal_chunks WHERE legal_chunks MATCH ? LIMIT 5", (query,)).fetchall()
        except sqlite3.OperationalError:
            return []
    return [{"title": row[0], "topic": row[1], "url": row[2], "snippet": row[3], "fetched_at": row[4]} for row in rows]
