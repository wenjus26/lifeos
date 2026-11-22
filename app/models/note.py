"""
LifeOS - Note Model
"""
from dataclasses import dataclass
from typing import Optional
from app.utils.date_utils import now_iso


@dataclass
class Note:
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    category: str = "Général"
    is_pinned: bool = False
    is_archived: bool = False
    updated_at: str = ""
    created_at: str = ""

    def __post_init__(self):
        now = now_iso()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    @classmethod
    def from_row(cls, row) -> "Note":
        return cls(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            category=row["category"],
            is_pinned=bool(row["is_pinned"]),
            is_archived=bool(row["is_archived"]),
            updated_at=row["updated_at"],
            created_at=row["created_at"]
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "is_pinned": int(self.is_pinned),
            "is_archived": int(self.is_archived),
            "updated_at": self.updated_at,
            "created_at": self.created_at
        }
