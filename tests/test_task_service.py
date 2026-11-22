"""
Tests pour le service de tâches (TaskService)
"""
import pytest
from app.services.task_service import TaskService
from app.core.constants import PRIORITY_URGENT, PRIORITY_LOW, FREQ_DAILY, TASK_STATUS_COMPLETED


def test_task_creation_with_subtasks(temp_db):
    tasks_svc = TaskService(temp_db)
    task = tasks_svc.create_task(
        title="Préparer le rapport mensuel",
        description="Inclure les graphiques",
        priority=PRIORITY_URGENT,
        due_date="2026-11-25",
        subtask_titles=["Collecter les données", "Rédiger l'introduction", "Relire"]
    )
    assert task.id is not None
    assert len(task.subtasks) == 3

    fetched = tasks_svc.get_task(task.id)
    assert len(fetched.subtasks) == 3
    assert fetched.subtasks[0].title == "Collecter les données"
    assert not fetched.subtasks[0].is_completed


def test_toggle_task_and_daily_recurrence(temp_db):
    tasks_svc = TaskService(temp_db)
    task = tasks_svc.create_task(
        title="Méditation matinale",
        priority=PRIORITY_LOW,
        due_date="2026-11-22",
        recurrence=FREQ_DAILY
    )

    # Complète la tâche récurrente
    updated = tasks_svc.toggle_task(task.id)
    assert updated.is_completed
    assert updated.status == TASK_STATUS_COMPLETED

    # Vérifie qu'une nouvelle tâche a été planifiée pour le lendemain (2026-11-23)
    all_tasks = tasks_svc.get_tasks(include_completed=False)
    next_task = [t for t in all_tasks if t.title == "Méditation matinale" and t.due_date == "2026-11-23"]
    assert len(next_task) == 1
    assert next_task[0].recurrence == FREQ_DAILY


def test_task_completion_stats(temp_db):
    tasks_svc = TaskService(temp_db)
    t1 = tasks_svc.create_task("Tâche 1")
    t2 = tasks_svc.create_task("Tâche 2")
    t3 = tasks_svc.create_task("Tâche 3")

    tasks_svc.toggle_task(t1.id)

    stats = tasks_svc.get_task_stats()
    assert stats["total"] == 3
    assert stats["completed"] == 1
    assert stats["pending"] == 2
    assert stats["completion_rate_percent"] == 33
