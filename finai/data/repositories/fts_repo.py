from typing import Dict, List
from finai.data.db import DatabaseManager


class SearchRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def search_all(self, query: str, limit: int = 50) -> List[Dict]:
        if not query or not query.strip():
            return []
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # SQLite FTS5 Match Query
        clean_query = query.replace("'", "''").strip() + "*"
        cursor.execute(
            """
            SELECT source_type, source_id, title, content
            FROM search_index
            WHERE search_index MATCH ?
            LIMIT ?
            """,
            (clean_query, limit),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
