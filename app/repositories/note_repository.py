"""
LifeOS - Note Repository
"""
from typing import List, Optional
from app.database.connection import db, DatabaseManager
from app.models.note import Note


class NoteRepository:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager

    def get_all(
        self,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
        include_archived: bool = False
    ) -> List[Note]:
        with self.db.session() as conn:
            query = "SELECT * FROM notes WHERE 1=1"
            params = []

            if not include_archived:
                query += " AND is_archived = 0"
            if category:
                query += " AND category = ?"
                params.append(category)
            if search_query:
                query += " AND (title LIKE ? OR content LIKE ?)"
                like_term = f"%{search_query}%"
                params.extend([like_term, like_term])

            query += " ORDER BY is_pinned DESC, updated_at DESC, id DESC"
            cursor = conn.execute(query, tuple(params))
            return [Note.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, note_id: int) -> Optional[Note]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
            row = cursor.fetchone()
            return Note.from_row(row) if row else None

    def create(self, note: Note) -> Note:
        with self.db.session() as conn:
            cursor = conn.execute(
                """
                INSERT INTO notes (title, content, category, is_pinned, is_archived, updated_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    note.title, note.content, note.category, int(note.is_pinned),
                    int(note.is_archived), note.updated_at, note.created_at
                )
            )
            note.id = cursor.lastrowid
            return note

    def update(self, note: Note) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute(
                """
                UPDATE notes
                SET title = ?, content = ?, category = ?, is_pinned = ?, is_archived = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    note.title, note.content, note.category, int(note.is_pinned),
                    int(note.is_archived), note.updated_at, note.id
                )
            )
            return cursor.rowcount > 0

    def delete(self, note_id: int) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            return cursor.rowcount > 0

    def get_categories(self) -> List[str]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT DISTINCT category FROM notes WHERE category IS NOT NULL ORDER BY category ASC")
            return [row["category"] for row in cursor.fetchall()]
