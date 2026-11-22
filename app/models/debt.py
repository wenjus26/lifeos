"""
LifeOS - Debt and DebtPayment Models
"""
from dataclasses import dataclass
from typing import Optional
from app.core.constants import DEBT_OWED_BY_ME, DEBT_STATUS_PENDING
from app.utils.date_utils import now_iso, today_str


@dataclass
class Debt:
    id: Optional[int] = None
    party_name: str = ""
    amount_cents: int = 0
    paid_cents: int = 0
    type: str = DEBT_OWED_BY_ME  # 'debt' ou 'receivable'
    due_date: Optional[str] = None
    status: str = DEBT_STATUS_PENDING  # 'pending', 'partial', 'paid'
    notes: Optional[str] = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = now_iso()

    @property
    def remaining_cents(self) -> int:
        return max(0, self.amount_cents - self.paid_cents)

    @classmethod
    def from_row(cls, row) -> "Debt":
        return cls(
            id=row["id"],
            party_name=row["party_name"],
            amount_cents=row["amount_cents"],
            paid_cents=row["paid_cents"],
            type=row["type"],
            due_date=row["due_date"],
            status=row["status"],
            notes=row["notes"],
            created_at=row["created_at"]
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "party_name": self.party_name,
            "amount_cents": self.amount_cents,
            "paid_cents": self.paid_cents,
            "type": self.type,
            "due_date": self.due_date,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at
        }


@dataclass
class DebtPayment:
    id: Optional[int] = None
    debt_id: int = 0
    amount_cents: int = 0
    payment_date: str = ""
    wallet_id: Optional[int] = None
    notes: Optional[str] = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.payment_date:
            self.payment_date = today_str()
        if not self.created_at:
            self.created_at = now_iso()

    @classmethod
    def from_row(cls, row) -> "DebtPayment":
        return cls(
            id=row["id"],
            debt_id=row["debt_id"],
            amount_cents=row["amount_cents"],
            payment_date=row["payment_date"],
            wallet_id=row["wallet_id"],
            notes=row["notes"],
            created_at=row["created_at"]
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "debt_id": self.debt_id,
            "amount_cents": self.amount_cents,
            "payment_date": self.payment_date,
            "wallet_id": self.wallet_id,
            "notes": self.notes,
            "created_at": self.created_at
        }
