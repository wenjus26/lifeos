"""
LifeOS - Wallet Repository
"""
from typing import List, Optional
import sqlite3
from app.database.connection import db, DatabaseManager
from app.models.wallet import Wallet


class WalletRepository:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager

    def get_all(self, include_archived: bool = False) -> List[Wallet]:
        with self.db.session() as conn:
            query = "SELECT * FROM wallets"
            if not include_archived:
                query += " WHERE is_archived = 0"
            query += " ORDER BY is_default DESC, name ASC"
            cursor = conn.execute(query)
            return [Wallet.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, wallet_id: int) -> Optional[Wallet]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM wallets WHERE id = ?", (wallet_id,))
            row = cursor.fetchone()
            return Wallet.from_row(row) if row else None

    def create(self, wallet: Wallet) -> Wallet:
        with self.db.session() as conn:
            if wallet.is_default:
                conn.execute("UPDATE wallets SET is_default = 0")
            cursor = conn.execute(
                """
                INSERT INTO wallets (name, type, balance_cents, currency, icon, color, is_default, is_archived, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    wallet.name, wallet.type, wallet.balance_cents, wallet.currency,
                    wallet.icon, wallet.color, int(wallet.is_default), int(wallet.is_archived),
                    wallet.created_at
                )
            )
            wallet.id = cursor.lastrowid
            return wallet

    def update(self, wallet: Wallet) -> bool:
        with self.db.session() as conn:
            if wallet.is_default:
                conn.execute("UPDATE wallets SET is_default = 0 WHERE id != ?", (wallet.id,))
            cursor = conn.execute(
                """
                UPDATE wallets
                SET name = ?, type = ?, balance_cents = ?, currency = ?, icon = ?, color = ?,
                    is_default = ?, is_archived = ?
                WHERE id = ?
                """,
                (
                    wallet.name, wallet.type, wallet.balance_cents, wallet.currency,
                    wallet.icon, wallet.color, int(wallet.is_default), int(wallet.is_archived),
                    wallet.id
                )
            )
            return cursor.rowcount > 0

    def update_balance(self, wallet_id: int, delta_cents: int, conn: Optional[sqlite3.Connection] = None) -> bool:
        """Met à jour le solde (peut être exécuté à l'intérieur d'une transaction externe)."""
        sql = "UPDATE wallets SET balance_cents = balance_cents + ? WHERE id = ?"
        if conn is not None:
            cursor = conn.execute(sql, (delta_cents, wallet_id))
            return cursor.rowcount > 0
        else:
            with self.db.session() as local_conn:
                cursor = local_conn.execute(sql, (delta_cents, wallet_id))
                return cursor.rowcount > 0

    def delete(self, wallet_id: int) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute("DELETE FROM wallets WHERE id = ?", (wallet_id,))
            return cursor.rowcount > 0
