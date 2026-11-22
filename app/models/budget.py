"""
LifeOS - Budget Model
"""
from dataclasses import dataclass
from typing import Optional
from app.utils.date_utils import current_month_str, now_iso


@dataclass
class Budget:
    id: Optional[int] = None
    category_id: Optional[int] = None  # None = Budget global
    month: str = ""  # YYYY-MM
    limit_cents: int = 0
    alert_threshold_percent: int = 80
    created_at: str = ""

    def __post_init__(self):
        if not self.month:
            self.month = current_month_str()
        if not self.created_at:
            self.created_at = now_iso()

    @classmethod
    def from_row(cls, row) -> "Budget":
        return cls(
            id=row["id"],
            category_id=row["category_id"],
            month=row["month"],
            limit_cents=row["limit_cents"],
            alert_threshold_percent=row["alert_threshold_percent"],
            created_at=row["created_at"]
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category_id": self.category_id,
            "month": self.month,
            "limit_cents": self.limit_cents,
            "alert_threshold_percent": self.alert_threshold_percent,
            "created_at": self.created_at
        }
