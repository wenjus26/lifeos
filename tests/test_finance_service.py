"""
Tests pour le service financier (FinanceService)
"""
import pytest
from app.services.finance_service import FinanceService
from app.core.exceptions import ValidationError, EntityNotFoundError
from app.core.constants import (
    WALLET_BANK, WALLET_MOBILE_MONEY,
    DEBT_OWED_BY_ME, DEBT_STATUS_PENDING, DEBT_STATUS_PARTIAL, DEBT_STATUS_PAID
)


def test_wallet_creation_and_balance(temp_db):
    finance = FinanceService(temp_db)
    w = finance.create_wallet(
        name="Wave Mobile Money",
        wallet_type=WALLET_MOBILE_MONEY,
        initial_balance_cents=50000,
        currency="XOF"
    )
    assert w.id is not None
    assert w.balance_cents == 50000

    fetched = finance.get_wallet(w.id)
    assert fetched.name == "Wave Mobile Money"
    assert fetched.balance_cents == 50000


def test_income_and_expense_balance_integrity(temp_db):
    finance = FinanceService(temp_db)
    wallets = finance.get_wallets()
    w_id = wallets[0].id
    initial_balance = wallets[0].balance_cents

    # Ajout revenu 250 000 FCFA
    tx_inc = finance.add_income(wallet_id=w_id, category_id=None, amount_cents=250000, note="Salaire")
    assert tx_inc.amount_cents == 250000

    w_updated = finance.get_wallet(w_id)
    assert w_updated.balance_cents == initial_balance + 250000

    # Ajout dépense 50 000 FCFA
    tx_exp, warning = finance.add_expense(wallet_id=w_id, category_id=None, amount_cents=50000, note="Courses")
    assert tx_exp.amount_cents == 50000

    w_updated2 = finance.get_wallet(w_id)
    assert w_updated2.balance_cents == initial_balance + 200000


def test_transfer_between_wallets_with_fees(temp_db):
    finance = FinanceService(temp_db)
    w_src = finance.create_wallet("Compte Bancaire", WALLET_BANK, 200000)
    w_dst = finance.create_wallet("Wave", WALLET_MOBILE_MONEY, 10000)

    # Transfert de 50 000 FCFA avec 500 FCFA de frais
    tx = finance.transfer(
        source_wallet_id=w_src.id,
        dest_wallet_id=w_dst.id,
        amount_cents=50000,
        fee_cents=500,
        note="Alimentation Wave"
    )

    src_after = finance.get_wallet(w_src.id)
    dst_after = finance.get_wallet(w_dst.id)

    # Source déduit de 50 000 + 500 = 50 500 -> reste 149 500
    assert src_after.balance_cents == 149500
    # Destination crédité de 50 000 -> 10 000 + 50 000 = 60 000
    assert dst_after.balance_cents == 60000


def test_budget_alert_threshold(temp_db):
    finance = FinanceService(temp_db)
    wallets = finance.get_wallets()
    w_id = wallets[0].id

    categories = finance.categories_repo.get_all(category_type="expense")
    cat_id = categories[0].id

    # Définit un budget de 100 000 FCFA avec seuil à 80%
    finance.set_budget(month="2026-11", limit_cents=100000, category_id=cat_id, alert_threshold_percent=80)

    # Dépense 70 000 FCFA (70% -> pas d'alerte)
    _, warn1 = finance.add_expense(wallet_id=w_id, category_id=cat_id, amount_cents=70000, date_str="2026-11-05")
    assert warn1 is None

    # Dépense 15 000 FCFA (Total 85 000 -> 85% >= 80% -> Alerte émise !)
    _, warn2 = finance.add_expense(wallet_id=w_id, category_id=cat_id, amount_cents=15000, date_str="2026-11-10")
    assert warn2 is not None
    assert warn2.budget_limit == 100000
    assert warn2.current_expense == 85000


def test_debt_and_partial_repayments(temp_db):
    finance = FinanceService(temp_db)
    wallets = finance.get_wallets()
    w_id = wallets[0].id

    # Création d'une dette de 60 000 FCFA envers un ami
    debt = finance.create_debt(
        party_name="Moussa Diop",
        amount_cents=60000,
        debt_type=DEBT_OWED_BY_ME,
        due_date="2026-12-01"
    )
    assert debt.status == DEBT_STATUS_PENDING
    assert debt.remaining_cents == 60000

    # Premier remboursement partiel de 20 000 FCFA
    finance.record_debt_payment(debt_id=debt.id, amount_cents=20000, wallet_id=w_id)
    d_part = finance.debts_repo.get_by_id(debt.id)
    assert d_part.status == DEBT_STATUS_PARTIAL
    assert d_part.paid_cents == 20000
    assert d_part.remaining_cents == 40000

    # Remboursement du solde restant (40 000 FCFA)
    finance.record_debt_payment(debt_id=debt.id, amount_cents=40000, wallet_id=w_id)
    d_paid = finance.debts_repo.get_by_id(debt.id)
    assert d_paid.status == DEBT_STATUS_PAID
    assert d_paid.remaining_cents == 0


def test_savings_goal_progression(temp_db):
    finance = FinanceService(temp_db)
    wallets = finance.get_wallets()
    w_id = wallets[0].id

    # Objectif : Ordinateur portable 500 000 FCFA
    goal = finance.create_savings_goal(
        title="Nouveau Laptop Pro",
        target_cents=500000,
        target_date="2027-01-31"
    )
    assert goal.progress_percent == 0
    assert not goal.is_completed

    # Dépôt de 250 000 FCFA (50%)
    goal_updated = finance.deposit_to_savings(goal.id, 250000, source_wallet_id=w_id)
    assert goal_updated.current_cents == 250000
    assert goal_updated.progress_percent == 50
    assert not goal_updated.is_completed

    # Dépôt de 250 000 FCFA supplémentaires (100% complété)
    goal_finished = finance.deposit_to_savings(goal.id, 250000, source_wallet_id=w_id)
    assert goal_finished.current_cents == 500000
    assert goal_finished.progress_percent == 100
    assert goal_finished.is_completed
