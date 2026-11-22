"""
Tests pour le service d'habitudes (HabitService)
"""
import pytest
from app.services.habit_service import HabitService
from app.utils.date_utils import today_str


def test_habit_creation_and_today_toggle(temp_db):
    habit_svc = HabitService(temp_db)
    habit = habit_svc.create_habit(
        title="Lire 20 pages",
        description="Livres de développement personnel et technique",
        target_time="evening"
    )
    assert habit.id is not None

    # Initialement non complétée aujourd'hui
    assert not habit_svc.repo.is_completed_today(habit.id)

    # Validation aujourd'hui
    res = habit_svc.toggle_today(habit.id)
    assert res is True
    assert habit_svc.repo.is_completed_today(habit.id)

    # Re-toggle annule
    res2 = habit_svc.toggle_today(habit.id)
    assert res2 is False
    assert not habit_svc.repo.is_completed_today(habit.id)


def test_habit_streaks_calculation(temp_db):
    habit_svc = HabitService(temp_db)
    habit = habit_svc.create_habit("Boire 2L d'eau")

    # Simulation de complétions sur 3 jours consécutifs
    from datetime import date, timedelta
    today = date.today()
    for i in range(3):
        d_str = (today - timedelta(days=i)).isoformat()
        habit_svc.repo.toggle_record(habit.id, d_str)

    stats = habit_svc.get_habit_stats(habit.id)
    assert stats["current_streak"] == 3
    assert stats["longest_streak"] >= 3
    assert stats["total_completions"] == 3
    assert stats["is_completed_today"] is True
