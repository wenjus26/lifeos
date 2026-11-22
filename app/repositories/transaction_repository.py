"""
LifeOS - Transaction Repository
"""
from typing import List, Optional, Tuple, Dict
import sqlite3
from app.database.connection import db, DatabaseManager
from app.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager

    def get_all(
        self,
        limit: int = 50,
        offset: int = 0,
        wallet_id: Optional[int] = None,
        category_id: Optional[int] = None,
        tx_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Transaction]:
        with self.db.session() as conn:
            query = "SELECT * FROM transactions WHERE 1=1"
            params = []

            if wallet_id is not None:
                query += " AND (wallet_id = ? OR dest_wallet_id = ?)"
                params.extend([wallet_id, wallet_id])
            if category_id is not None:
                query += " AND category_id = ?"
                params.append(category_id)
            if tx_type is not None:
                query += " AND type = ?"
                params.append(tx_type)
            if start_date is not None:
                query += " AND date >= ?"
                params.append(start_date)
            if end_date is not None:
                query += " AND date <= ?"
                params.append(end_date)

            query += " ORDER BY date DESC, id DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor = conn.execute(query, tuple(params))
            return [Transaction.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, tx_id: int) -> Optional[Transaction]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
            row = cursor.fetchone()
            return Transaction.from_row(row) if row else None

    def create(self, tx: Transaction, conn: Optional[sqlite3.Connection] = None) -> Transaction:
        sql = """
            INSERT INTO transactions (wallet_id, category_id, type, amount_cents, date, note, recurrence, dest_wallet_id, fee_cents, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            tx.wallet_id, tx.category_id, tx.type, tx.amount_cents,
            tx.date, tx.note, tx.recurrence, tx.dest_wallet_id, tx.fee_cents,
            tx.created_at
        )

        if conn is not None:
            cursor = conn.execute(sql, values)
            tx.id = cursor.lastrowid
            return tx
        else:
            with self.db.session() as local_conn:
                cursor = local_conn.execute(sql, values)
                tx.id = cursor.lastrowid
                return tx

    def delete(self, tx_id: int, conn: Optional[sqlite3.Connection] = None) -> bool:
        sql = "DELETE FROM transactions WHERE id = ?"
        if conn is not None:
            cursor = conn.execute(sql, (tx_id,))
            return cursor.rowcount > 0
        else:
            with self.db.session() as local_conn:
                cursor = local_conn.execute(sql, (tx_id,))
                return cursor.rowcount > 0

    def get_monthly_totals(self, start_date: str, end_date: str) -> Dict[str, int]:
        """Retourne {'income': total_cents, 'expense': total_cents}."""
        with self.db.session() as conn:
            cursor = conn.execute(
                """
                SELECT type, SUM(amount_cents) as total
                FROM transactions
                WHERE date >= ? AND date <= ? AND type IN ('income', 'expense')
                GROUP BY type
                """,
                (start_date, end_date)
            )
            result = {"income": 0, "expense": 0}
            for row in cursor.fetchall():
                result[row["type"]] = row["total"] or 0
            return result

    def get_expenses_by_category(self, start_date: str, end_date: str) -> List[Dict]:
        """Agrège les dépenses par catégorie pour le camembert / histogramme."""
        with self.db.session() as conn:
            cursor = conn.execute(
                """
                SELECT c.id, c.name, c.icon, c.color, SUM(t.amount_cents) as total_cents
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.type = 'expense' AND t.date >= ? AND t.date <= ?
                GROUP BY c.id, c.name
                ORDER BY total_cents DESC
                """,
                (start_date, end_date)
            )
            return [
                {
                    "category_id": row["id"],
                    "name": row["name"] or "Non catégorisé",
                    "icon": row["icon"] or "help-circle",
                    "color": row["color"] or "#9E9E9E",
                    "total_cents": row["total_cents"] or 0
                }
                for row in cursor.fetchall()
            ]
