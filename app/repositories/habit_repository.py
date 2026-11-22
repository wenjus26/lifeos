"""
LifeOS - Habit Repository
"""
from typing import List, Optional, Set
import sqlite3
from app.database.connection import db, DatabaseManager
from app.models.habit import Habit, HabitRecord
from app.utils.date_utils import now_iso, today_str


class HabitRepository:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager

    def get_all(self) -> List[Habit]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM habits ORDER BY id ASC")
            return [Habit.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, habit_id: int) -> Optional[Habit]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
            row = cursor.fetchone()
            return Habit.from_row(row) if row else None

    def create(self, habit: Habit) -> Habit:
        with self.db.session() as conn:
            cursor = conn.execute(
                """
                INSERT INTO habits (title, description, frequency, target_time, icon, color, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (habit.title, habit.description, habit.frequency, habit.target_time, habit.icon, habit.color, habit.created_at)
            )
            habit.id = cursor.lastrowid
            return habit

    def update(self, habit: Habit) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute(
                """
                UPDATE habits
                SET title = ?, description = ?, frequency = ?, target_time = ?, icon = ?, color = ?
                WHERE id = ?
                """,
                (habit.title, habit.description, habit.frequency, habit.target_time, habit.icon, habit.color, habit.id)
            )
            return cursor.rowcount > 0

    def delete(self, habit_id: int) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
            return cursor.rowcount > 0

    def get_completed_dates(self, habit_id: int) -> List[str]:
        """Retourne la liste des dates YYYY-MM-DD où l'habitude a été validée."""
        with self.db.session() as conn:
            cursor = conn.execute(
                "SELECT date FROM habit_records WHERE habit_id = ? AND completed = 1 ORDER BY date ASC",
                (habit_id,)
            )
            return [row["date"] for row in cursor.fetchall()]

    def is_completed_today(self, habit_id: int, target_date: str = None) -> bool:
        check_date = target_date or today_str()
        with self.db.session() as conn:
            cursor = conn.execute(
                "SELECT id FROM habit_records WHERE habit_id = ? AND date = ? AND completed = 1",
                (habit_id, check_date)
            )
            return cursor.fetchone() is not None

    def toggle_record(self, habit_id: int, target_date: str = None) -> bool:
        """Bascule l'état de complétion pour une date donnée."""
        check_date = target_date or today_str()
        with self.db.session() as conn:
            cursor = conn.execute(
                "SELECT id, completed FROM habit_records WHERE habit_id = ? AND date = ?",
                (habit_id, check_date)
            )
            row = cursor.fetchone()
            if row:
                new_state = 0 if row["completed"] else 1
                conn.execute(
                    "UPDATE habit_records SET completed = ? WHERE id = ?",
                    (new_state, row["id"])
                )
                return bool(new_state)
            else:
                conn.execute(
                    "INSERT INTO habit_records (habit_id, date, completed, created_at) VALUES (?, ?, 1, ?)",
                    (habit_id, check_date, now_iso())
                )
                return True
