"""
LifeOS - Calendar Service
Gestion des événements, rendez-vous, rappels et vue agenda unifiée
"""
from typing import List, Optional, Dict
from datetime import datetime, date
from app.database.connection import db, DatabaseManager
from app.repositories.calendar_repository import CalendarRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.habit_repository import HabitRepository
from app.models.calendar_event import CalendarEvent
from app.core.constants import EVENT_TYPE_EVENT
from app.core.exceptions import ValidationError, EntityNotFoundError
from app.utils.date_utils import today_str


class CalendarService:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager
        self.repo = CalendarRepository(db_manager)
        self.task_repo = TaskRepository(db_manager)
        self.habit_repo = HabitRepository(db_manager)

    def get_events(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[CalendarEvent]:
        return self.repo.get_all(start_date, end_date)

    def get_event(self, event_id: int) -> CalendarEvent:
        ev = self.repo.get_by_id(event_id)
        if not ev:
            raise EntityNotFoundError("Événement", event_id)
        return ev

    def create_event(
        self,
        title: str,
        start_datetime: str,
        end_datetime: str,
        description: str = "",
        event_type: str = EVENT_TYPE_EVENT,
        is_all_day: bool = False,
        reminder_minutes: int = 15,
        location: str = ""
    ) -> CalendarEvent:
        if not title or not title.strip():
            raise ValidationError("Le titre de l'événement est obligatoire.", "title")
        if not start_datetime or not end_datetime:
            raise ValidationError("Les dates et heures de début et fin sont obligatoires.")
        if end_datetime < start_datetime:
            raise ValidationError("L'heure de fin ne peut pas précéder l'heure de début.")

        event = CalendarEvent(
            title=title.strip(),
            description=description,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            event_type=event_type,
            is_all_day=is_all_day,
            reminder_minutes=reminder_minutes,
            location=location
        )
        return self.repo.create(event)

    def delete_event(self, event_id: int) -> bool:
        return self.repo.delete(event_id)

    def get_daily_agenda(self, target_date: str = None) -> Dict:
        """
        Génère une vue unifiée de la journée :
        - Événements du calendrier
        - Tâches dues pour cette date
        - Habitudes à valider
        """
        day = target_date or today_str()
        start_bound = f"{day}T00:00:00"
        end_bound = f"{day}T23:59:59"

        events = self.repo.get_all(start_date=start_bound, end_date=end_bound)
        tasks = self.task_repo.get_all(due_date=day, include_completed=True)
        habits = self.habit_repo.get_all()

        habit_items = []
        for h in habits:
            habit_items.append({
                "habit": h,
                "completed": self.habit_repo.is_completed_today(h.id, day)
            })

        return {
            "date": day,
            "events": events,
            "tasks": tasks,
            "habits": habit_items
        }
