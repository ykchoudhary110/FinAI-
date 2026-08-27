import json
from typing import Dict, List, Optional
from finai.data.db import DatabaseManager


class ChatRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def add_message(
        self,
        session_id: str,
        sender: str,
        content: str,
        figure_context: Optional[Dict] = None,
        is_pinned: bool = False,
    ) -> int:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        fig_json = json.dumps(figure_context) if figure_context else None
        cursor.execute(
            """
            INSERT INTO chat_messages (session_id, sender, content, figure_context, is_pinned)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, sender, content, fig_json, 1 if is_pinned else 0),
        )
        msg_id = cursor.lastrowid

        # Update FTS5 index
        cursor.execute(
            """
            INSERT INTO search_index (source_type, source_id, title, content)
            VALUES ('chat', ?, ?, ?)
            """,
            (str(msg_id), f"Chat message ({sender})", content),
        )

        conn.commit()
        conn.close()
        return msg_id

    def get_messages_by_session(self, session_id: str) -> List[Dict]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY timestamp ASC",
            (session_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_pinned_conversations(self) -> List[Dict]:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT session_id, content FROM chat_messages WHERE is_pinned = 1 GROUP BY session_id"
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
