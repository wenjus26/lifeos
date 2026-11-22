"""
LifeOS - Task Repository
"""
from typing import List, Optional
import sqlite3
from app.database.connection import db, DatabaseManager
from app.models.task import Task, SubTask
from app.core.constants import TASK_STATUS_COMPLETED


class TaskRepository:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager

    def get_all(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        include_completed: bool = False
    ) -> List[Task]:
        with self.db.session() as conn:
            query = "SELECT * FROM tasks WHERE 1=1"
            params = []

            if status:
                query += " AND status = ?"
                params.append(status)
            elif not include_completed:
                query += " AND is_completed = 0"

            if priority:
                query += " AND priority = ?"
                params.append(priority)
            if due_date:
                query += " AND due_date = ?"
                params.append(due_date)

            query += """
                ORDER BY
                    is_completed ASC,
                    CASE priority
                        WHEN 'urgent' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                        ELSE 5
                    END ASC,
                    due_date ASC,
                    id DESC
            """
            cursor = conn.execute(query, tuple(params))
            tasks = [Task.from_row(row) for row in cursor.fetchall()]

            # Charger les sous-tâches pour chaque tâche
            for task in tasks:
                task.subtasks = self.get_subtasks(task.id, conn)

            return tasks

    def get_by_id(self, task_id: int) -> Optional[Task]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if not row:
                return None
            task = Task.from_row(row)
            task.subtasks = self.get_subtasks(task.id, conn)
            return task

    def create(self, task: Task) -> Task:
        with self.db.session() as conn:
            cursor = conn.execute(
                """
                INSERT INTO tasks (title, description, priority, due_date, due_time, status, recurrence, is_completed, completed_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.title, task.description, task.priority, task.due_date,
                    task.due_time, task.status, task.recurrence, int(task.is_completed),
                    task.completed_at, task.created_at
                )
            )
            task.id = cursor.lastrowid

            for subtask in task.subtasks:
                subtask.task_id = task.id
                c_sub = conn.execute(
                    "INSERT INTO subtasks (task_id, title, is_completed, created_at) VALUES (?, ?, ?, ?)",
                    (subtask.task_id, subtask.title, int(subtask.is_completed), subtask.created_at)
                )
                subtask.id = c_sub.lastrowid

            return task

    def update(self, task: Task) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, priority = ?, due_date = ?, due_time = ?,
                    status = ?, recurrence = ?, is_completed = ?, completed_at = ?
                WHERE id = ?
                """,
                (
                    task.title, task.description, task.priority, task.due_date,
                    task.due_time, task.status, task.recurrence, int(task.is_completed),
                    task.completed_at, task.id
                )
            )
            return cursor.rowcount > 0

    def delete(self, task_id: int) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0

    def get_subtasks(self, task_id: int, conn: Optional[sqlite3.Connection] = None) -> List[SubTask]:
        sql = "SELECT * FROM subtasks WHERE task_id = ? ORDER BY id ASC"
        if conn is not None:
            cursor = conn.execute(sql, (task_id,))
            return [SubTask.from_row(row) for row in cursor.fetchall()]
        else:
            with self.db.session() as local_conn:
                cursor = local_conn.execute(sql, (task_id,))
                return [SubTask.from_row(row) for row in cursor.fetchall()]

    def add_subtask(self, subtask: SubTask) -> SubTask:
        with self.db.session() as conn:
            cursor = conn.execute(
                "INSERT INTO subtasks (task_id, title, is_completed, created_at) VALUES (?, ?, ?, ?)",
                (subtask.task_id, subtask.title, int(subtask.is_completed), subtask.created_at)
            )
            subtask.id = cursor.lastrowid
            return subtask

    def toggle_subtask(self, subtask_id: int, is_completed: bool) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute(
                "UPDATE subtasks SET is_completed = ? WHERE id = ?",
                (int(is_completed), subtask_id)
            )
            return cursor.rowcount > 0
