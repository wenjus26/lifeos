"""
LifeOS - Debt Repository
"""
from typing import List, Optional
import sqlite3
from app.database.connection import db, DatabaseManager
from app.models.debt import Debt, DebtPayment


class DebtRepository:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager

    def get_all(self, debt_type: Optional[str] = None, status: Optional[str] = None) -> List[Debt]:
        with self.db.session() as conn:
            query = "SELECT * FROM debts WHERE 1=1"
            params = []
            if debt_type:
                query += " AND type = ?"
                params.append(debt_type)
            if status:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY due_date ASC, id DESC"
            cursor = conn.execute(query, tuple(params))
            return [Debt.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, debt_id: int) -> Optional[Debt]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM debts WHERE id = ?", (debt_id,))
            row = cursor.fetchone()
            return Debt.from_row(row) if row else None

    def create(self, debt: Debt) -> Debt:
        with self.db.session() as conn:
            cursor = conn.execute(
                """
                INSERT INTO debts (party_name, amount_cents, paid_cents, type, due_date, status, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    debt.party_name, debt.amount_cents, debt.paid_cents, debt.type,
                    debt.due_date, debt.status, debt.notes, debt.created_at
                )
            )
            debt.id = cursor.lastrowid
            return debt

    def update(self, debt: Debt, conn: Optional[sqlite3.Connection] = None) -> bool:
        sql = """
            UPDATE debts
            SET party_name = ?, amount_cents = ?, paid_cents = ?, type = ?,
                due_date = ?, status = ?, notes = ?
            WHERE id = ?
        """
        params = (
            debt.party_name, debt.amount_cents, debt.paid_cents, debt.type,
            debt.due_date, debt.status, debt.notes, debt.id
        )
        if conn is not None:
            cursor = conn.execute(sql, params)
            return cursor.rowcount > 0
        else:
            with self.db.session() as local_conn:
                cursor = local_conn.execute(sql, params)
                return cursor.rowcount > 0

    def delete(self, debt_id: int) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute("DELETE FROM debts WHERE id = ?", (debt_id,))
            return cursor.rowcount > 0

    def add_payment(self, payment: DebtPayment, conn: Optional[sqlite3.Connection] = None) -> DebtPayment:
        sql = """
            INSERT INTO debt_payments (debt_id, amount_cents, payment_date, wallet_id, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            payment.debt_id, payment.amount_cents, payment.payment_date,
            payment.wallet_id, payment.notes, payment.created_at
        )
        if conn is not None:
            cursor = conn.execute(sql, params)
            payment.id = cursor.lastrowid
            return payment
        else:
            with self.db.session() as local_conn:
                cursor = local_conn.execute(sql, params)
                payment.id = cursor.lastrowid
                return payment

    def get_payments(self, debt_id: int) -> List[DebtPayment]:
        with self.db.session() as conn:
            cursor = conn.execute(
                "SELECT * FROM debt_payments WHERE debt_id = ? ORDER BY payment_date DESC, id DESC",
                (debt_id,)
            )
            return [DebtPayment.from_row(row) for row in cursor.fetchall()]
