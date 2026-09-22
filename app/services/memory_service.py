import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict


class MemoryService:

    def __init__(self):

        # Project root directory
        self.base_dir = (
            Path(__file__)
            .resolve()
            .parents[2]
        )

        # Data directory
        self.data_dir = (
            self.base_dir / "data"
        )

        self.data_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # SQLite database
        self.db_path = (
            self.data_dir / "chat.db"
        )

        # Create database/table
        self._initialize_database()


    # =====================================================
    # DATABASE CONNECTION
    # =====================================================

    def _get_connection(self):

        connection = sqlite3.connect(
            self.db_path
        )

        connection.row_factory = (
            sqlite3.Row
        )

        return connection


    # =====================================================
    # INITIALIZE DATABASE
    # =====================================================

    def _initialize_database(self):

        with self._get_connection() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    session_id TEXT NOT NULL,

                    role TEXT NOT NULL,

                    content TEXT NOT NULL,

                    created_at TEXT NOT NULL

                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_messages_session_id
                ON messages(session_id)
                """
            )

            connection.commit()


    # =====================================================
    # GET CHAT HISTORY
    # =====================================================

    def get_history(
        self,
        session_id: str
    ) -> List[Dict]:

        with self._get_connection() as connection:

            rows = connection.execute(
                """
                SELECT
                    role,
                    content
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,)
            ).fetchall()


        history = []

        for row in rows:

            history.append(
                {
                    "role": row["role"],
                    "content": row["content"]
                }
            )


        return history


    # =====================================================
    # ADD MESSAGE
    # =====================================================

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):

        created_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )


        with self._get_connection() as connection:

            connection.execute(
                """
                INSERT INTO messages (
                    session_id,
                    role,
                    content,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    session_id,
                    role,
                    content,
                    created_at
                )
            )

            connection.commit()


    # =====================================================
    # CLEAR SESSION
    # =====================================================

    def clear_session(
        self,
        session_id: str
    ):

        with self._get_connection() as connection:

            connection.execute(
                """
                DELETE FROM messages
                WHERE session_id = ?
                """,
                (session_id,)
            )

            connection.commit()


    # =====================================================
    # DELETE ALL HISTORY
    # =====================================================

    def clear_all(self):

        with self._get_connection() as connection:

            connection.execute(
                """
                DELETE FROM messages
                """
            )

            connection.commit()


# =========================================================
# SINGLE SERVICE INSTANCE
# =========================================================

memory_service = MemoryService()
