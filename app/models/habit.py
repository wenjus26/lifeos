"""
LifeOS - Habit and HabitRecord Models
"""
from dataclasses import dataclass
from typing import Optional
from app.core.constants import FREQ_DAILY
from app.utils.date_utils import now_iso, today_str


@dataclass
class Habit:
    id: Optional[int] = None
    title: str = ""
    description: Optional[str] = ""
    frequency: str = FREQ_DAILY  # 'daily', 'weekdays', 'weekends'
    target_time: str = "anytime"  # 'morning', 'afternoon', 'evening', 'anytime'
    icon: str = "check-circle-outline"
    color: str = "#42A5F5"
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = now_iso()

    @classmethod
    def from_row(cls, row) -> "Habit":
        return cls(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            frequency=row["frequency"],
            target_time=row["target_time"],
            icon=row["icon"],
            color=row["color"],
            created_at=row["created_at"]
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "frequency": self.frequency,
            "target_time": self.target_time,
            "icon": self.icon,
            "color": self.color,
            "created_at": self.created_at
        }


@dataclass
class HabitRecord:
    id: Optional[int] = None
    habit_id: int = 0
    date: str = ""
    completed: bool = True
    created_at: str = ""

    def __post_init__(self):
        if not self.date:
            self.date = today_str()
        if not self.created_at:
            self.created_at = now_iso()

    @classmethod
    def from_row(cls, row) -> "HabitRecord":
        return cls(
            id=row["id"],
            habit_id=row["habit_id"],
            date=row["date"],
            completed=bool(row["completed"]),
            created_at=row["created_at"]
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "date": self.date,
            "completed": int(self.completed),
            "created_at": self.created_at
        }
