"""
LifeOS - Task and Subtask Models
"""
from dataclasses import dataclass, field
from typing import Optional, List
from app.core.constants import PRIORITY_MEDIUM, TASK_STATUS_TODO, FREQ_NONE
from app.utils.date_utils import now_iso, today_str


@dataclass
class SubTask:
    id: Optional[int] = None
    task_id: int = 0
    title: str = ""
    is_completed: bool = False
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = now_iso()

    @classmethod
    def from_row(cls, row) -> "SubTask":
        return cls(
            id=row["id"],
            task_id=row["task_id"],
            title=row["title"],
            is_completed=bool(row["is_completed"]),
            created_at=row["created_at"]
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "title": self.title,
            "is_completed": int(self.is_completed),
            "created_at": self.created_at
        }


@dataclass
class Task:
    id: Optional[int] = None
    title: str = ""
    description: Optional[str] = ""
    priority: str = PRIORITY_MEDIUM  # 'low', 'medium', 'high', 'urgent'
    due_date: Optional[str] = None  # YYYY-MM-DD
    due_time: Optional[str] = None  # HH:MM
    status: str = TASK_STATUS_TODO  # 'todo', 'in_progress', 'completed', 'archived'
    recurrence: str = FREQ_NONE  # 'none', 'daily', 'weekly', 'monthly'
    is_completed: bool = False
    completed_at: Optional[str] = None
    created_at: str = ""
    subtasks: List[SubTask] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = now_iso()

    @classmethod
    def from_row(cls, row) -> "Task":
        return cls(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            priority=row["priority"],
            due_date=row["due_date"],
            due_time=row["due_time"],
            status=row["status"],
            recurrence=row["recurrence"],
            is_completed=bool(row["is_completed"]),
            completed_at=row["completed_at"],
            created_at=row["created_at"]
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date,
            "due_time": self.due_time,
            "status": self.status,
            "recurrence": self.recurrence,
            "is_completed": int(self.is_completed),
            "completed_at": self.completed_at,
            "created_at": self.created_at
        }
