"""
LifeOS - Category Model
"""
from dataclasses import dataclass
from typing import Optional
from app.core.constants import TX_EXPENSE
from app.utils.date_utils import now_iso


@dataclass
class Category:
    id: Optional[int] = None
    name: str = ""
    type: str = TX_EXPENSE  # 'income' ou 'expense'
    icon: str = "tag"
    color: str = "#42A5F5"
    is_default: bool = False
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = now_iso()

    @classmethod
    def from_row(cls, row) -> "Category":
        return cls(
            id=row["id"],
            name=row["name"],
            type=row["type"],
            icon=row["icon"],
            color=row["color"],
            is_default=bool(row["is_default"]),
            created_at=row["created_at"]
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "icon": self.icon,
            "color": self.color,
            "is_default": int(self.is_default),
            "created_at": self.created_at
        }
