"""
LifeOS - Habit Service
Suivi des habitudes, calcul de séries (streaks) et historique quotidien
"""
from typing import List, Dict, Optional
from datetime import date, timedelta
from app.database.connection import db, DatabaseManager
from app.repositories.habit_repository import HabitRepository
from app.models.habit import Habit
from app.core.constants import FREQ_DAILY
from app.core.exceptions import ValidationError, EntityNotFoundError
from app.utils.date_utils import today_str, calculate_streaks
from app.utils.android_native import android_bridge


class HabitService:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager
        self.repo = HabitRepository(db_manager)

    def get_habits(self) -> List[Habit]:
        return self.repo.get_all()

    def get_habit(self, habit_id: int) -> Habit:
        h = self.repo.get_by_id(habit_id)
        if not h:
            raise EntityNotFoundError("Habitude", habit_id)
        return h

    def create_habit(
        self,
        title: str,
        description: str = "",
        frequency: str = FREQ_DAILY,
        target_time: str = "anytime",
        icon: str = "check-circle-outline",
        color: str = "#42A5F5"
    ) -> Habit:
        if not title or not title.strip():
            raise ValidationError("Le titre de l'habitude est obligatoire.", "title")

        habit = Habit(
            title=title.strip(),
            description=description,
            frequency=frequency,
            target_time=target_time,
            icon=icon,
            color=color
        )
        return self.repo.create(habit)

    def toggle_today(self, habit_id: int) -> bool:
        """Valide ou annule l'habitude pour la date d'aujourd'hui."""
        h = self.get_habit(habit_id)
        new_state = self.repo.toggle_record(habit_id, today_str())
        android_bridge.vibrate(40)
        return new_state

    def get_habit_stats(self, habit_id: int) -> Dict:
        """Retourne les séries (streak actuel, max streak), complétions et matrice 30 jours."""
        h = self.get_habit(habit_id)
        dates = self.repo.get_completed_dates(habit_id)
        current_streak, longest_streak = calculate_streaks(dates)

        # Matrice des 30 derniers jours
        today = date.today()
        date_set = set(dates)
        last_30_days = []
        for i in range(29, -1, -1):
            d = today - timedelta(days=i)
            iso_d = d.isoformat()
            last_30_days.append({
                "date": iso_d,
                "day_num": d.day,
                "completed": iso_d in date_set
            })

        total_completions = len(dates)
        rate_30 = int((sum(1 for x in last_30_days if x["completed"]) / 30) * 100)

        return {
            "habit_id": habit_id,
            "title": h.title,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_completions": total_completions,
            "rate_last_30_days": rate_30,
            "is_completed_today": self.repo.is_completed_today(habit_id),
            "history_30_days": last_30_days
        }

    def get_all_habits_with_today_status(self) -> List[Dict]:
        """Retourne la liste complète des habitudes avec indicateur du jour et streaks."""
        habits = self.get_habits()
        result = []
        for h in habits:
            dates = self.repo.get_completed_dates(h.id)
            current_streak, longest_streak = calculate_streaks(dates)
            result.append({
                "habit": h,
                "completed_today": self.repo.is_completed_today(h.id),
                "current_streak": current_streak,
                "longest_streak": longest_streak
            })
        return result

    def delete_habit(self, habit_id: int) -> bool:
        return self.repo.delete(habit_id)
