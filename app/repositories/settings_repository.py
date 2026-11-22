"""
LifeOS - Settings Repository
"""
from typing import Dict, Optional
from app.database.connection import db, DatabaseManager


class SettingsRepository:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager

    def get_all(self) -> Dict[str, str]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT key, value FROM settings")
            return {row["key"]: row["value"] for row in cursor.fetchall()}

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    def set(self, key: str, value: str):
        with self.db.session() as conn:
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value)
            )
