"""
LifeOS - Budget Repository
"""
from typing import List, Optional, Dict
from app.database.connection import db, DatabaseManager
from app.models.budget import Budget


class BudgetRepository:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager

    def get_all(self, month: Optional[str] = None) -> List[Budget]:
        with self.db.session() as conn:
            if month:
                cursor = conn.execute("SELECT * FROM budgets WHERE month = ? ORDER BY id ASC", (month,))
            else:
                cursor = conn.execute("SELECT * FROM budgets ORDER BY month DESC, id ASC")
            return [Budget.from_row(row) for row in cursor.fetchall()]

    def get_by_category_and_month(self, category_id: Optional[int], month: str) -> Optional[Budget]:
        with self.db.session() as conn:
            if category_id is None:
                cursor = conn.execute("SELECT * FROM budgets WHERE category_id IS NULL AND month = ?", (month,))
            else:
                cursor = conn.execute("SELECT * FROM budgets WHERE category_id = ? AND month = ?", (category_id, month))
            row = cursor.fetchone()
            return Budget.from_row(row) if row else None

    def upsert(self, budget: Budget) -> Budget:
        existing = self.get_by_category_and_month(budget.category_id, budget.month)
        with self.db.session() as conn:
            if existing:
                conn.execute(
                    """
                    UPDATE budgets
                    SET limit_cents = ?, alert_threshold_percent = ?
                    WHERE id = ?
                    """,
                    (budget.limit_cents, budget.alert_threshold_percent, existing.id)
                )
                budget.id = existing.id
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO budgets (category_id, month, limit_cents, alert_threshold_percent, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (budget.category_id, budget.month, budget.limit_cents, budget.alert_threshold_percent, budget.created_at)
                )
                budget.id = cursor.lastrowid
            return budget

    def delete(self, budget_id: int) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute("DELETE FROM budgets WHERE id = ?", (budget_id,))
            return cursor.rowcount > 0
