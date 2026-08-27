"""
Document Ingestion Utility for FinAI RAG System
Parses text files, statutory seed documents, and PDFs into SQLite FTS5 Full-Text Search index.
"""

import sys
from finai.data.db import DatabaseManager
from finai.data.legal_corpus.legal_corpus_seed import SEED_LEGAL_CORPUS
from finai.data.legal_corpus.hsn_sac_directory import HSN_SAC_MASTER


def ingest_all_corpus_into_fts(db_path: str = "finai.db"):
    db_manager = DatabaseManager(db_path)
    conn = db_manager.get_connection()
    cursor = conn.cursor()

    # Clear old knowledge records in search_index
    cursor.execute("DELETE FROM search_index WHERE source_type = 'knowledge'")

    count = 0
    # 1. Ingest Statutory Legal Corpus & Book Chapters
    for chunk in SEED_LEGAL_CORPUS:
        blob = f"{chunk.statute_name} {chunk.section_no} {chunk.title} {chunk.content} {' '.join(chunk.topic_tags)}"
        cursor.execute(
            """
            INSERT INTO search_index (source_type, source_id, title, content)
            VALUES ('knowledge', ?, ?, ?)
            """,
            (chunk.doc_id, f"{chunk.statute_name} - {chunk.section_no}", blob)
        )
        count += 1

    # 2. Ingest HSN / SAC Directory
    for item in HSN_SAC_MASTER:
        hsn_blob = f"{item.code_type} {item.code} {item.category} {item.description} GST Rate: {item.gst_rate}% {' '.join(item.keywords or [])}"
        cursor.execute(
            """
            INSERT INTO search_index (source_type, source_id, title, content)
            VALUES ('knowledge', ?, ?, ?)
            """,
            (f"HSN_{item.code}", f"{item.code_type} {item.code} - {item.category}", hsn_blob)
        )
        count += 1

    conn.commit()
    conn.close()
    print(f"Successfully ingested {count} statutory knowledge documents into SQLite FTS5 search index!")


if __name__ == "__main__":
    ingest_all_corpus_into_fts()
