"""
LifeOS - Calendar Event Repository
"""
from typing import List, Optional
from app.database.connection import db, DatabaseManager
from app.models.calendar_event import CalendarEvent


class CalendarRepository:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager

    def get_all(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[CalendarEvent]:
        with self.db.session() as conn:
            query = "SELECT * FROM calendar_events WHERE 1=1"
            params = []
            if start_date:
                query += " AND start_datetime >= ?"
                params.append(start_date)
            if end_date:
                query += " AND start_datetime <= ?"
                params.append(end_date)
            query += " ORDER BY start_datetime ASC"
            cursor = conn.execute(query, tuple(params))
            return [CalendarEvent.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, event_id: int) -> Optional[CalendarEvent]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM calendar_events WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            return CalendarEvent.from_row(row) if row else None

    def create(self, event: CalendarEvent) -> CalendarEvent:
        with self.db.session() as conn:
            cursor = conn.execute(
                """
                INSERT INTO calendar_events (title, description, start_datetime, end_datetime, event_type, is_all_day, reminder_minutes, location, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.title, event.description, event.start_datetime, event.end_datetime,
                    event.event_type, int(event.is_all_day), event.reminder_minutes, event.location,
                    event.created_at
                )
            )
            event.id = cursor.lastrowid
            return event

    def update(self, event: CalendarEvent) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute(
                """
                UPDATE calendar_events
                SET title = ?, description = ?, start_datetime = ?, end_datetime = ?,
                    event_type = ?, is_all_day = ?, reminder_minutes = ?, location = ?
                WHERE id = ?
                """,
                (
                    event.title, event.description, event.start_datetime, event.end_datetime,
                    event.event_type, int(event.is_all_day), event.reminder_minutes, event.location,
                    event.id
                )
            )
            return cursor.rowcount > 0

    def delete(self, event_id: int) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
            return cursor.rowcount > 0
