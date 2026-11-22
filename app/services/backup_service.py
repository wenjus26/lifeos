"""
LifeOS - Backup & Restore Service
Sauvegarde et restauration intégrale des données 100% hors connexion
"""
import os
import json
import shutil
import sqlite3
from typing import Dict, Any, Optional
from app.database.connection import db, DatabaseManager
from app.config.settings import settings
from app.utils.date_utils import now_iso, today_str


class BackupService:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager

    def create_json_backup(self, output_path: Optional[str] = None) -> str:
        """Exporte l'intégralité des données en format JSON portable."""
        if not output_path:
            filename = f"lifeos_backup_{today_str()}.json"
            output_path = os.path.join(settings.backups_directory, filename)

        tables = [
            "wallets", "categories", "transactions", "budgets", "debts",
            "debt_payments", "savings_goals", "tasks", "subtasks",
            "habits", "habit_records", "personal_goals", "goal_milestones",
            "calendar_events", "notes", "settings"
        ]

        backup_data: Dict[str, Any] = {
            "app": "LifeOS",
            "version": settings.version,
            "backup_created_at": now_iso(),
            "data": {}
        }

        with self.db.session() as conn:
            for table in tables:
                cursor = conn.execute(f"SELECT * FROM {table}")
                rows = [dict(row) for row in cursor.fetchall()]
                backup_data["data"][table] = rows

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)

        return output_path

    def restore_from_json(self, backup_filepath: str) -> bool:
        """Restaure les données depuis une sauvegarde JSON après validation."""
        if not os.path.exists(backup_filepath):
            raise FileNotFoundError(f"Fichier de sauvegarde introuvable : {backup_filepath}")

        with open(backup_filepath, "r", encoding="utf-8") as f:
            backup_data = json.load(f)

        if backup_data.get("app") != "LifeOS" or "data" not in backup_data:
            raise ValueError("Format de sauvegarde LifeOS invalide.")

        data = backup_data["data"]

        with self.db.session() as conn:
            # Désactiver temporairement les contraintes de clés étrangères pour la réinsertion
            conn.execute("PRAGMA foreign_keys = OFF;")

            for table, rows in data.items():
                conn.execute(f"DELETE FROM {table}")
                if not rows:
                    continue
                cols = list(rows[0].keys())
                placeholders = ", ".join(["?"] * len(cols))
                col_names = ", ".join(cols)
                sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"

                for r in rows:
                    values = [r[col] for col in cols]
                    conn.execute(sql, values)

            conn.execute("PRAGMA foreign_keys = ON;")

        return True

    def create_sqlite_file_backup(self, output_dir: Optional[str] = None) -> str:
        """Copie brute du fichier .db avec VACUUM INTO pour consistance."""
        target_dir = output_dir or settings.backups_directory
        filename = f"lifeos_db_raw_{today_str()}.db"
        dest_path = os.path.join(target_dir, filename)

        with self.db.session() as conn:
            # VACUUM INTO effectue une sauvegarde transactionnelle garantie
            try:
                conn.execute(f"VACUUM INTO '{dest_path}'")
            except sqlite3.OperationalError:
                # Fallback standard si VACUUM INTO non supporté
                shutil.copy2(self.db.db_path, dest_path)

        return dest_path
