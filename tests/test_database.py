"""
Tests pour la connexion et l'initialisation de la base SQLite
"""
def test_database_initialization(temp_db):
    with temp_db.session() as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row["name"] for row in cursor.fetchall()]

        expected_tables = [
            "wallets", "categories", "transactions", "budgets", "debts",
            "debt_payments", "savings_goals", "tasks", "subtasks",
            "habits", "habit_records", "personal_goals", "goal_milestones",
            "calendar_events", "notes", "settings"
        ]
        for t in expected_tables:
            assert t in tables, f"Table {t} manquante dans la base de données."


def test_seed_default_data(temp_db):
    with temp_db.session() as conn:
        # Portefeuille par défaut
        cursor = conn.execute("SELECT COUNT(*) as count FROM wallets WHERE is_default = 1")
        assert cursor.fetchone()["count"] == 1

        # Catégories par défaut
        cursor = conn.execute("SELECT COUNT(*) as count FROM categories")
        assert cursor.fetchone()["count"] >= 14
