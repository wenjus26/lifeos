"""
LifeOS - Personal Goal and GoalMilestone Models
"""
from dataclasses import dataclass, field
from typing import Optional, List
from app.core.constants import GOAL_CAT_PERSONAL
from app.utils.date_utils import now_iso


@dataclass
class GoalMilestone:
    id: Optional[int] = None
    goal_id: int = 0
    title: str = ""
    is_completed: bool = False
    target_date: Optional[str] = None
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = now_iso()

    @classmethod
    def from_row(cls, row) -> "GoalMilestone":
        return cls(
            id=row["id"],
            goal_id=row["goal_id"],
            title=row["title"],
            is_completed=bool(row["is_completed"]),
            target_date=row["target_date"],
            created_at=row["created_at"]
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "goal_id": self.goal_id,
            "title": self.title,
            "is_completed": int(self.is_completed),
            "target_date": self.target_date,
            "created_at": self.created_at
        }


@dataclass
class PersonalGoal:
    id: Optional[int] = None
    title: str = ""
    description: Optional[str] = ""
    category: str = GOAL_CAT_PERSONAL  # 'personal', 'professional', 'financial'
    target_date: Optional[str] = None
    progress_percent: int = 0
    is_completed: bool = False
    created_at: str = ""
    milestones: List[GoalMilestone] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = now_iso()

    @classmethod
    def from_row(cls, row) -> "PersonalGoal":
        return cls(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            category=row["category"],
            target_date=row["target_date"],
            progress_percent=row["progress_percent"],
            is_completed=bool(row["is_completed"]),
            created_at=row["created_at"]
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "target_date": self.target_date,
            "progress_percent": self.progress_percent,
            "is_completed": int(self.is_completed),
            "created_at": self.created_at
        }
