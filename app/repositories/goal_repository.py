"""
LifeOS - Personal Goal Repository
"""
from typing import List, Optional
import sqlite3
from app.database.connection import db, DatabaseManager
from app.models.goal import PersonalGoal, GoalMilestone


class GoalRepository:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager

    def get_all(self, category: Optional[str] = None, include_completed: bool = True) -> List[PersonalGoal]:
        with self.db.session() as conn:
            query = "SELECT * FROM personal_goals WHERE 1=1"
            params = []
            if category:
                query += " AND category = ?"
                params.append(category)
            if not include_completed:
                query += " AND is_completed = 0"

            query += " ORDER BY is_completed ASC, target_date ASC, id DESC"
            cursor = conn.execute(query, tuple(params))
            goals = [PersonalGoal.from_row(row) for row in cursor.fetchall()]

            for goal in goals:
                goal.milestones = self.get_milestones(goal.id, conn)

            return goals

    def get_by_id(self, goal_id: int) -> Optional[PersonalGoal]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM personal_goals WHERE id = ?", (goal_id,))
            row = cursor.fetchone()
            if not row:
                return None
            goal = PersonalGoal.from_row(row)
            goal.milestones = self.get_milestones(goal.id, conn)
            return goal

    def create(self, goal: PersonalGoal) -> PersonalGoal:
        with self.db.session() as conn:
            cursor = conn.execute(
                """
                INSERT INTO personal_goals (title, description, category, target_date, progress_percent, is_completed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    goal.title, goal.description, goal.category, goal.target_date,
                    goal.progress_percent, int(goal.is_completed), goal.created_at
                )
            )
            goal.id = cursor.lastrowid

            for ms in goal.milestones:
                ms.goal_id = goal.id
                c_ms = conn.execute(
                    "INSERT INTO goal_milestones (goal_id, title, is_completed, target_date, created_at) VALUES (?, ?, ?, ?, ?)",
                    (ms.goal_id, ms.title, int(ms.is_completed), ms.target_date, ms.created_at)
                )
                ms.id = c_ms.lastrowid

            return goal

    def update(self, goal: PersonalGoal) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute(
                """
                UPDATE personal_goals
                SET title = ?, description = ?, category = ?, target_date = ?,
                    progress_percent = ?, is_completed = ?
                WHERE id = ?
                """,
                (
                    goal.title, goal.description, goal.category, goal.target_date,
                    goal.progress_percent, int(goal.is_completed), goal.id
                )
            )
            return cursor.rowcount > 0

    def delete(self, goal_id: int) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute("DELETE FROM personal_goals WHERE id = ?", (goal_id,))
            return cursor.rowcount > 0

    def get_milestones(self, goal_id: int, conn: Optional[sqlite3.Connection] = None) -> List[GoalMilestone]:
        sql = "SELECT * FROM goal_milestones WHERE goal_id = ? ORDER BY id ASC"
        if conn is not None:
            cursor = conn.execute(sql, (goal_id,))
            return [GoalMilestone.from_row(row) for row in cursor.fetchall()]
        else:
            with self.db.session() as local_conn:
                cursor = local_conn.execute(sql, (goal_id,))
                return [GoalMilestone.from_row(row) for row in cursor.fetchall()]

    def add_milestone(self, ms: GoalMilestone) -> GoalMilestone:
        with self.db.session() as conn:
            cursor = conn.execute(
                "INSERT INTO goal_milestones (goal_id, title, is_completed, target_date, created_at) VALUES (?, ?, ?, ?, ?)",
                (ms.goal_id, ms.title, int(ms.is_completed), ms.target_date, ms.created_at)
            )
            ms.id = cursor.lastrowid
            return ms

    def toggle_milestone(self, milestone_id: int, is_completed: bool) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute(
                "UPDATE goal_milestones SET is_completed = ? WHERE id = ?",
                (int(is_completed), milestone_id)
            )
            return cursor.rowcount > 0
