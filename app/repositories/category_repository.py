"""
LifeOS - Category Repository
"""
from typing import List, Optional
from app.database.connection import db, DatabaseManager
from app.models.category import Category


class CategoryRepository:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager

    def get_all(self, category_type: Optional[str] = None) -> List[Category]:
        with self.db.session() as conn:
            if category_type:
                cursor = conn.execute(
                    "SELECT * FROM categories WHERE type = ? ORDER BY is_default DESC, name ASC",
                    (category_type,)
                )
            else:
                cursor = conn.execute("SELECT * FROM categories ORDER BY type ASC, name ASC")
            return [Category.from_row(row) for row in cursor.fetchall()]

    def get_by_id(self, cat_id: int) -> Optional[Category]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM categories WHERE id = ?", (cat_id,))
            row = cursor.fetchone()
            return Category.from_row(row) if row else None

    def create(self, category: Category) -> Category:
        with self.db.session() as conn:
            cursor = conn.execute(
                """
                INSERT INTO categories (name, type, icon, color, is_default, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    category.name, category.type, category.icon, category.color,
                    int(category.is_default), category.created_at
                )
            )
            category.id = cursor.lastrowid
            return category

    def update(self, category: Category) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute(
                """
                UPDATE categories
                SET name = ?, type = ?, icon = ?, color = ?
                WHERE id = ?
                """,
                (category.name, category.type, category.icon, category.color, category.id)
            )
            return cursor.rowcount > 0

    def delete(self, cat_id: int) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
            return cursor.rowcount > 0
