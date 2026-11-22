"""
LifeOS - Calendar Event Model
"""
from dataclasses import dataclass
from typing import Optional
from app.core.constants import EVENT_TYPE_EVENT
from app.utils.date_utils import now_iso


@dataclass
class CalendarEvent:
    id: Optional[int] = None
    title: str = ""
    description: Optional[str] = ""
    start_datetime: str = ""  # YYYY-MM-DDTHH:MM:SS
    end_datetime: str = ""    # YYYY-MM-DDTHH:MM:SS
    event_type: str = EVENT_TYPE_EVENT  # 'appointment', 'event', 'reminder', 'deadline'
    is_all_day: bool = False
    reminder_minutes: int = 15
    location: Optional[str] = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = now_iso()

    @classmethod
    def from_row(cls, row) -> "CalendarEvent":
        return cls(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            start_datetime=row["start_datetime"],
            end_datetime=row["end_datetime"],
            event_type=row["event_type"],
            is_all_day=bool(row["is_all_day"]),
            reminder_minutes=row["reminder_minutes"],
            location=row["location"],
            created_at=row["created_at"]
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "start_datetime": self.start_datetime,
            "end_datetime": self.end_datetime,
            "event_type": self.event_type,
            "is_all_day": int(self.is_all_day),
            "reminder_minutes": self.reminder_minutes,
            "location": self.location,
            "created_at": self.created_at
        }
