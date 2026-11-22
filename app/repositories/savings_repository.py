"""
LifeOS - Savings Goal Repository
"""
from typing import List, Optional
import sqlite3
from app.database.connection import db, DatabaseManager
from app.models.savings_goal import SavingsGoal


class SavingsRepository:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager

    def get_all(self, include_completed: bool = True) -> List[SavingsGoal]:
        with self.db.session() as conn:
            query = "SELECT * FROM savings_goals"
            if not include_completed:
                query += " WHERE is_completed = 0"
            query += " ORDER BY is_completed ASC, target_date ASC, id DESC"
            cursor = conn.execute(query)
            return [SavingsGoal.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, goal_id: int) -> Optional[SavingsGoal]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM savings_goals WHERE id = ?", (goal_id,))
            row = cursor.fetchone()
            return SavingsGoal.from_row(row) if row else None

    def create(self, goal: SavingsGoal) -> SavingsGoal:
        with self.db.session() as conn:
            cursor = conn.execute(
                """
                INSERT INTO savings_goals (title, target_cents, current_cents, target_date, icon, color, is_completed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    goal.title, goal.target_cents, goal.current_cents, goal.target_date,
                    goal.icon, goal.color, int(goal.is_completed), goal.created_at
                )
            )
            goal.id = cursor.lastrowid
            return goal

    def update(self, goal: SavingsGoal, conn: Optional[sqlite3.Connection] = None) -> bool:
        sql = """
            UPDATE savings_goals
            SET title = ?, target_cents = ?, current_cents = ?, target_date = ?,
                icon = ?, color = ?, is_completed = ?
            WHERE id = ?
        """
        params = (
            goal.title, goal.target_cents, goal.current_cents, goal.target_date,
            goal.icon, goal.color, int(goal.is_completed), goal.id
        )
        if conn is not None:
            cursor = conn.execute(sql, params)
            return cursor.rowcount > 0
        else:
            with self.db.session() as local_conn:
                cursor = local_conn.execute(sql, params)
                return cursor.rowcount > 0

    def delete(self, goal_id: int) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute("DELETE FROM savings_goals WHERE id = ?", (goal_id,))
            return cursor.rowcount > 0
