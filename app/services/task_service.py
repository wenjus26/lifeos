"""
LifeOS - Task Service
Gestion complète des tâches, sous-tâches et récurrences
"""
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from app.database.connection import db, DatabaseManager
from app.repositories.task_repository import TaskRepository
from app.models.task import Task, SubTask
from app.core.constants import (
    TASK_STATUS_TODO, TASK_STATUS_COMPLETED,
    FREQ_NONE, FREQ_DAILY, FREQ_WEEKLY, FREQ_MONTHLY,
    PRIORITY_MEDIUM
)
from app.core.exceptions import ValidationError, EntityNotFoundError
from app.utils.date_utils import today_str, now_iso
from app.utils.android_native import android_bridge


class TaskService:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager
        self.repo = TaskRepository(db_manager)

    def get_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        include_completed: bool = False
    ) -> List[Task]:
        return self.repo.get_all(status, priority, due_date, include_completed)

    def get_today_tasks(self) -> List[Task]:
        """Toutes les tâches prévues pour aujourd'hui ou en retard."""
        today = today_str()
        all_pending = self.repo.get_all(include_completed=False)
        return [t for t in all_pending if t.due_date is None or t.due_date <= today]

    def get_task(self, task_id: int) -> Task:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise EntityNotFoundError("Tâche", task_id)
        return task

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: str = PRIORITY_MEDIUM,
        due_date: Optional[str] = None,
        due_time: Optional[str] = None,
        recurrence: str = FREQ_NONE,
        subtask_titles: List[str] = None
    ) -> Task:
        if not title or not title.strip():
            raise ValidationError("Le titre de la tâche est obligatoire.", "title")

        task = Task(
            title=title.strip(),
            description=description,
            priority=priority,
            due_date=due_date,
            due_time=due_time,
            recurrence=recurrence,
            status=TASK_STATUS_TODO
        )

        if subtask_titles:
            for st_title in subtask_titles:
                if st_title.strip():
                    task.subtasks.append(SubTask(title=st_title.strip()))

        created_task = self.repo.create(task)
        android_bridge.vibrate(30)
        return created_task

    def toggle_task(self, task_id: int) -> Task:
        """Bascule l'état d'une tâche. Si récurrente et complétée, génère la prochaine occurrence."""
        task = self.get_task(task_id)
        task.is_completed = not task.is_completed

        if task.is_completed:
            task.status = TASK_STATUS_COMPLETED
            task.completed_at = now_iso()
            android_bridge.vibrate(50)

            # Gestion de la récurrence
            if task.recurrence != FREQ_NONE and task.due_date:
                self._schedule_next_recurrence(task)
        else:
            task.status = TASK_STATUS_TODO
            task.completed_at = None

        self.repo.update(task)
        return task

    def _schedule_next_recurrence(self, task: Task):
        try:
            curr_due = datetime.strptime(task.due_date, "%Y-%m-%d").date()
            if task.recurrence == FREQ_DAILY:
                next_due = curr_due + timedelta(days=1)
            elif task.recurrence == FREQ_WEEKLY:
                next_due = curr_due + timedelta(weeks=1)
            elif task.recurrence == FREQ_MONTHLY:
                # Ajout de 30 jours pour simplification sûre
                next_due = curr_due + timedelta(days=30)
            else:
                return

            subtitles = [st.title for st in task.subtasks]
            self.create_task(
                title=task.title,
                description=task.description,
                priority=task.priority,
                due_date=next_due.isoformat(),
                due_time=task.due_time,
                recurrence=task.recurrence,
                subtask_titles=subtitles
            )
        except Exception:
            pass

    def add_subtask(self, task_id: int, title: str) -> SubTask:
        if not title or not title.strip():
            raise ValidationError("Le titre de la sous-tâche est obligatoire.")
        task = self.get_task(task_id)
        subtask = SubTask(task_id=task_id, title=title.strip())
        return self.repo.add_subtask(subtask)

    def toggle_subtask(self, subtask_id: int, is_completed: bool) -> bool:
        res = self.repo.toggle_subtask(subtask_id, is_completed)
        android_bridge.vibrate(25)
        return res

    def delete_task(self, task_id: int) -> bool:
        return self.repo.delete(task_id)

    def get_task_stats(self) -> Dict:
        """Statistiques d'accomplissement des tâches."""
        all_tasks = self.repo.get_all(include_completed=True)
        total = len(all_tasks)
        completed = sum(1 for t in all_tasks if t.is_completed)
        pending = total - completed
        rate = int((completed / total) * 100) if total > 0 else 0
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "completion_rate_percent": rate
        }
