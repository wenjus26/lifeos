"""
LifeOS - Note Service
Gestion des notes, recherche plein texte, favoris et archivage
"""
from typing import List, Optional
from app.database.connection import db, DatabaseManager
from app.repositories.note_repository import NoteRepository
from app.models.note import Note
from app.core.exceptions import ValidationError, EntityNotFoundError
from app.utils.date_utils import now_iso


class NoteService:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager
        self.repo = NoteRepository(db_manager)

    def get_notes(
        self,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
        include_archived: bool = False
    ) -> List[Note]:
        return self.repo.get_all(category, search_query, include_archived)

    def get_note(self, note_id: int) -> Note:
        note = self.repo.get_by_id(note_id)
        if not note:
            raise EntityNotFoundError("Note", note_id)
        return note

    def create_note(self, title: str, content: str, category: str = "Général", is_pinned: bool = False) -> Note:
        if not title or not title.strip():
            raise ValidationError("Le titre de la note est obligatoire.", "title")

        note = Note(
            title=title.strip(),
            content=content,
            category=category or "Général",
            is_pinned=is_pinned
        )
        return self.repo.create(note)

    def update_note(self, note_id: int, title: str, content: str, category: str = None, is_pinned: bool = None) -> Note:
        note = self.get_note(note_id)
        note.title = title.strip()
        note.content = content
        if category is not None:
            note.category = category
        if is_pinned is not None:
            note.is_pinned = is_pinned
        note.updated_at = now_iso()
        self.repo.update(note)
        return note

    def toggle_pin(self, note_id: int) -> bool:
        note = self.get_note(note_id)
        note.is_pinned = not note.is_pinned
        note.updated_at = now_iso()
        self.repo.update(note)
        return note.is_pinned

    def toggle_archive(self, note_id: int) -> bool:
        note = self.get_note(note_id)
        note.is_archived = not note.is_archived
        note.updated_at = now_iso()
        self.repo.update(note)
        return note.is_archived

    def delete_note(self, note_id: int) -> bool:
        return self.repo.delete(note_id)

    def get_categories(self) -> List[str]:
        return self.repo.get_categories()
