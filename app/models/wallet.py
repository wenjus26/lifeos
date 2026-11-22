"""
LifeOS - Wallet Model
"""
from dataclasses import dataclass
from typing import Optional
from app.core.constants import WALLET_CASH, DEFAULT_CURRENCY
from app.utils.date_utils import now_iso


@dataclass
class Wallet:
    id: Optional[int] = None
    name: str = ""
    type: str = WALLET_CASH
    balance_cents: int = 0
    currency: str = DEFAULT_CURRENCY
    icon: str = "wallet"
    color: str = "#26A69A"
    is_default: bool = False
    is_archived: bool = False
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = now_iso()

    @classmethod
    def from_row(cls, row) -> "Wallet":
        return cls(
            id=row["id"],
            name=row["name"],
            type=row["type"],
            balance_cents=row["balance_cents"],
            currency=row["currency"],
            icon=row["icon"],
            color=row["color"],
            is_default=bool(row["is_default"]),
            is_archived=bool(row["is_archived"]),
            created_at=row["created_at"]
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "balance_cents": self.balance_cents,
            "currency": self.currency,
            "icon": self.icon,
            "color": self.color,
            "is_default": int(self.is_default),
            "is_archived": int(self.is_archived),
            "created_at": self.created_at
        }
