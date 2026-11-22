"""
LifeOS - Savings Goal Model
"""
from dataclasses import dataclass
from typing import Optional
from app.utils.date_utils import now_iso


@dataclass
class SavingsGoal:
    id: Optional[int] = None
    title: str = ""
    target_cents: int = 0
    current_cents: int = 0
    target_date: Optional[str] = None
    icon: str = "piggy-bank"
    color: str = "#66BB6A"
    is_completed: bool = False
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = now_iso()

    @property
    def progress_percent(self) -> int:
        if self.target_cents <= 0:
            return 100 if self.current_cents > 0 else 0
        return min(100, int((self.current_cents / self.target_cents) * 100))

    @classmethod
    def from_row(cls, row) -> "SavingsGoal":
        return cls(
            id=row["id"],
            title=row["title"],
            target_cents=row["target_cents"],
            current_cents=row["current_cents"],
            target_date=row["target_date"],
            icon=row["icon"],
            color=row["color"],
            is_completed=bool(row["is_completed"]),
            created_at=row["created_at"]
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "target_cents": self.target_cents,
            "current_cents": self.current_cents,
            "target_date": self.target_date,
            "icon": self.icon,
            "color": self.color,
            "is_completed": int(self.is_completed),
            "created_at": self.created_at
        }
