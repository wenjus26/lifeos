"""
LifeOS - Database Connection & Schema Management
Gestion centralisée de SQLite avec WAL mode, clés étrangères et transactions atomiques.
"""
import sqlite3
import logging
from typing import Generator
from contextlib import contextmanager

from app.config.settings import settings
from app.core.constants import DEFAULT_CATEGORIES, WALLET_CASH, DEFAULT_CURRENCY
from app.utils.date_utils import now_iso

logger = logging.getLogger("LifeOS.Database")

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

-- Table des Portefeuilles (Wallets)
CREATE TABLE IF NOT EXISTS wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'cash',
    balance_cents INTEGER NOT NULL DEFAULT 0,
    currency TEXT NOT NULL DEFAULT 'XOF',
    icon TEXT NOT NULL DEFAULT 'wallet',
    color TEXT NOT NULL DEFAULT '#26A69A',
    is_default INTEGER NOT NULL DEFAULT 0,
    is_archived INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

-- Table des Catégories de transactions
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- 'income' ou 'expense'
    icon TEXT NOT NULL DEFAULT 'tag',
    color TEXT NOT NULL DEFAULT '#42A5F5',
    is_default INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

-- Table des Transactions financières (Revenus, Dépenses, Transferts)
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id INTEGER NOT NULL,
    category_id INTEGER,
    type TEXT NOT NULL, -- 'income', 'expense', 'transfer'
    amount_cents INTEGER NOT NULL,
    date TEXT NOT NULL, -- YYYY-MM-DD
    note TEXT,
    recurrence TEXT DEFAULT 'none',
    dest_wallet_id INTEGER, -- Rempli si type == 'transfer'
    fee_cents INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (wallet_id) REFERENCES wallets (id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL,
    FOREIGN KEY (dest_wallet_id) REFERENCES wallets (id) ON DELETE SET NULL
);

-- Table des Budgets mensuels
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER, -- NULL = budget mensuel global
    month TEXT NOT NULL, -- YYYY-MM
    limit_cents INTEGER NOT NULL,
    alert_threshold_percent INTEGER NOT NULL DEFAULT 80,
    created_at TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
);

-- Table des Dettes et Créances
CREATE TABLE IF NOT EXISTS debts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    party_name TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    paid_cents INTEGER NOT NULL DEFAULT 0,
    type TEXT NOT NULL, -- 'debt' (je dois) ou 'receivable' (on me doit)
    due_date TEXT,
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'partial', 'paid'
    notes TEXT,
    created_at TEXT NOT NULL
);

-- Table des Paiements / Remboursements de dettes
CREATE TABLE IF NOT EXISTS debt_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    debt_id INTEGER NOT NULL,
    amount_cents INTEGER NOT NULL,
    payment_date TEXT NOT NULL,
    wallet_id INTEGER,
    notes TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (debt_id) REFERENCES debts (id) ON DELETE CASCADE,
    FOREIGN KEY (wallet_id) REFERENCES wallets (id) ON DELETE SET NULL
);

-- Table des Objectifs d'Épargne
CREATE TABLE IF NOT EXISTS savings_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    target_cents INTEGER NOT NULL,
    current_cents INTEGER NOT NULL DEFAULT 0,
    target_date TEXT,
    icon TEXT NOT NULL DEFAULT 'piggy-bank',
    color TEXT NOT NULL DEFAULT '#66BB6A',
    is_completed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

-- Table des Tâches
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT NOT NULL DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    due_date TEXT, -- YYYY-MM-DD
    due_time TEXT, -- HH:MM
    status TEXT NOT NULL DEFAULT 'todo', -- 'todo', 'in_progress', 'completed', 'archived'
    recurrence TEXT DEFAULT 'none',
    is_completed INTEGER NOT NULL DEFAULT 0,
    completed_at TEXT,
    created_at TEXT NOT NULL
);

-- Table des Sous-tâches (Checklist)
CREATE TABLE IF NOT EXISTS subtasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    is_completed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
);

-- Table des Habitudes
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    frequency TEXT NOT NULL DEFAULT 'daily', -- 'daily', 'weekdays', 'weekends'
    target_time TEXT DEFAULT 'anytime',
    icon TEXT NOT NULL DEFAULT 'check-circle-outline',
    color TEXT NOT NULL DEFAULT '#42A5F5',
    created_at TEXT NOT NULL
);

-- Table des Enregistrements d'habitudes (Check-in quotidien)
CREATE TABLE IF NOT EXISTS habit_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    date TEXT NOT NULL, -- YYYY-MM-DD
    completed INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    UNIQUE(habit_id, date),
    FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
);

-- Table des Objectifs personnels & professionnels
CREATE TABLE IF NOT EXISTS personal_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL DEFAULT 'personal', -- 'personal', 'professional', 'financial'
    target_date TEXT,
    progress_percent INTEGER NOT NULL DEFAULT 0,
    is_completed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

-- Table des Jalons d'objectifs (Milestones)
CREATE TABLE IF NOT EXISTS goal_milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    is_completed INTEGER NOT NULL DEFAULT 0,
    target_date TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (goal_id) REFERENCES personal_goals (id) ON DELETE CASCADE
);

-- Table des Événements Calendrier
CREATE TABLE IF NOT EXISTS calendar_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    start_datetime TEXT NOT NULL, -- YYYY-MM-DDTHH:MM:SS
    end_datetime TEXT NOT NULL,
    event_type TEXT NOT NULL DEFAULT 'event', -- 'appointment', 'event', 'reminder', 'deadline'
    is_all_day INTEGER NOT NULL DEFAULT 0,
    reminder_minutes INTEGER DEFAULT 15,
    location TEXT,
    created_at TEXT NOT NULL
);

-- Table des Notes
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT DEFAULT 'Général',
    is_pinned INTEGER NOT NULL DEFAULT 0,
    is_archived INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Table des Paramètres généraux (Paires Clé-Valeur)
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Index pour performances mobiles élevées
CREATE INDEX IF NOT EXISTS idx_tx_date ON transactions (date);
CREATE INDEX IF NOT EXISTS idx_tx_wallet ON transactions (wallet_id);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks (due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);
CREATE INDEX IF NOT EXISTS idx_habit_records_date ON habit_records (date);
CREATE INDEX IF NOT EXISTS idx_cal_start ON calendar_events (start_datetime);
CREATE INDEX IF NOT EXISTS idx_notes_updated ON notes (updated_at);
"""


class DatabaseManager:
    """Gestionnaire de connexion SQLite avec pool sécurisé."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.database_path

    def get_connection(self) -> sqlite3.Connection:
        """Ouvre une connexion SQLite configurée."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    @contextmanager
    def session(self) -> Generator[sqlite3.Connection, None, None]:
        """Gestionnaire de contexte pour les transactions sécurisées."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Erreur SQL avec rollback : {e}")
            raise
        finally:
            conn.close()

    def initialize_database(self):
        """Crée toutes les tables et insère les données par défaut si nécessaire."""
        with self.session() as conn:
            conn.executescript(SCHEMA_SQL)
            self._seed_default_data(conn)
        logger.info(f"Base de données SQLite initialisée : {self.db_path}")

    def _seed_default_data(self, conn: sqlite3.Connection):
        """Injecte le portefeuille principal et les catégories par défaut."""
        # 1. Vérification du portefeuille par défaut
        cursor = conn.execute("SELECT COUNT(*) AS count FROM wallets")
        if cursor.fetchone()["count"] == 0:
            conn.execute(
                """
                INSERT INTO wallets (name, type, balance_cents, currency, icon, color, is_default, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                """,
                ("Portefeuille Principal", WALLET_CASH, 0, DEFAULT_CURRENCY, "wallet", "#26A69A", now_iso())
            )

        # 2. Vérification des catégories par défaut
        cursor = conn.execute("SELECT COUNT(*) AS count FROM categories")
        if cursor.fetchone()["count"] == 0:
            for cat in DEFAULT_CATEGORIES:
                conn.execute(
                    """
                    INSERT INTO categories (name, type, icon, color, is_default, created_at)
                    VALUES (?, ?, ?, ?, 1, ?)
                    """,
                    (cat["name"], cat["type"], cat["icon"], cat["color"], now_iso())
                )

        # 3. Paramètres initiaux
        cursor = conn.execute("SELECT COUNT(*) AS count FROM settings")
        if cursor.fetchone()["count"] == 0:
            default_settings = [
                ("default_currency", DEFAULT_CURRENCY),
                ("theme_style", "dark"),
                ("pin_enabled", "0"),
                ("pin_hash", ""),
                ("biometrics_enabled", "0"),
                ("auto_backup", "1")
            ]
            conn.executemany("INSERT INTO settings (key, value) VALUES (?, ?)", default_settings)


# Instance globale
db = DatabaseManager()
