"""
Pytest Fixtures - LifeOS
Configuration d'une base de données SQLite temporaire isolée pour les tests
"""
import pytest
import tempfile
import os
from app.database.connection import DatabaseManager


@pytest.fixture
def temp_db():
    """Crée une base de données SQLite temporaire avec schéma et seed initial."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    manager = DatabaseManager(db_path=path)
    manager.initialize_database()

    yield manager

    try:
        os.remove(path)
    except Exception:
        pass
