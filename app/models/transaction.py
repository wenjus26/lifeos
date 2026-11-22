"""
LifeOS - Transaction Model
"""
from dataclasses import dataclass
from typing import Optional
from app.core.constants import TX_EXPENSE, FREQ_NONE
from app.utils.date_utils import today_str, now_iso


@dataclass
class Transaction:
    id: Optional[int] = None
    wallet_id: int = 1
    category_id: Optional[int] = None
    type: str = TX_EXPENSE  # 'income', 'expense', 'transfer'
    amount_cents: int = 0
    date: str = ""
    note: Optional[str] = ""
    recurrence: str = FREQ_NONE
    dest_wallet_id: Optional[int] = None  # Pour transferts
    fee_cents: int = 0
    created_at: str = ""

    def __post_init__(self):
        if not self.date:
            self.date = today_str()
        if not self.created_at:
            self.created_at = now_iso()

    @classmethod
    def from_row(cls, row) -> "Transaction":
        return cls(
            id=row["id"],
            wallet_id=row["wallet_id"],
            category_id=row["category_id"],
            type=row["type"],
            amount_cents=row["amount_cents"],
            date=row["date"],
            note=row["note"],
            recurrence=row["recurrence"],
            dest_wallet_id=row["dest_wallet_id"],
            fee_cents=row["fee_cents"],
            created_at=row["created_at"]
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "wallet_id": self.wallet_id,
            "category_id": self.category_id,
            "type": self.type,
            "amount_cents": self.amount_cents,
            "date": self.date,
            "note": self.note,
            "recurrence": self.recurrence,
            "dest_wallet_id": self.dest_wallet_id,
            "fee_cents": self.fee_cents,
            "created_at": self.created_at
        }
