"""
LifeOS - Finance Service
Logique métier complète pour la gestion financière :
- Revenus et dépenses avec mise à jour atomique des soldes
- Transferts entre portefeuilles avec prise en compte des frais
- Suivi des budgets mensuels et alertes de dépassement
- Gestion des dettes, créances et paiements partiels
- Gestion de l'épargne et des objectifs d'épargne
- Rapports et agrégations financières
"""
from typing import List, Optional, Dict, Tuple
from app.database.connection import db, DatabaseManager
from app.repositories.wallet_repository import WalletRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.budget_repository import BudgetRepository
from app.repositories.debt_repository import DebtRepository
from app.repositories.savings_repository import SavingsRepository
from app.models.wallet import Wallet
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.debt import Debt, DebtPayment
from app.models.savings_goal import SavingsGoal
from app.core.constants import (
    TX_INCOME, TX_EXPENSE, TX_TRANSFER,
    DEBT_OWED_BY_ME, DEBT_OWED_TO_ME,
    DEBT_STATUS_PENDING, DEBT_STATUS_PARTIAL, DEBT_STATUS_PAID
)
from app.core.exceptions import (
    ValidationError, EntityNotFoundError, InsufficientFundsError, BudgetExceededWarning
)
from app.utils.date_utils import current_month_str, get_month_date_range, today_str
from app.utils.android_native import android_bridge


class FinanceService:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager
        self.wallets_repo = WalletRepository(db_manager)
        self.categories_repo = CategoryRepository(db_manager)
        self.transactions_repo = TransactionRepository(db_manager)
        self.budgets_repo = BudgetRepository(db_manager)
        self.debts_repo = DebtRepository(db_manager)
        self.savings_repo = SavingsRepository(db_manager)

    # ==========================
    # PORTEFEUILLES (WALLETS)
    # ==========================

    def get_wallets(self, include_archived: bool = False) -> List[Wallet]:
        return self.wallets_repo.get_all(include_archived)

    def get_wallet(self, wallet_id: int) -> Wallet:
        wallet = self.wallets_repo.get_by_id(wallet_id)
        if not wallet:
            raise EntityNotFoundError("Portefeuille", wallet_id)
        return wallet

    def create_wallet(self, name: str, wallet_type: str, initial_balance_cents: int = 0,
                      currency: str = "XOF", icon: str = "wallet", color: str = "#26A69A",
                      is_default: bool = False) -> Wallet:
        if not name or not name.strip():
            raise ValidationError("Le nom du portefeuille ne peut pas être vide.", "name")
        wallet = Wallet(
            name=name.strip(),
            type=wallet_type,
            balance_cents=initial_balance_cents,
            currency=currency,
            icon=icon,
            color=color,
            is_default=is_default
        )
        return self.wallets_repo.create(wallet)

    def get_total_balance_cents(self) -> int:
        wallets = self.get_wallets(include_archived=False)
        return sum(w.balance_cents for w in wallets)

    # ==========================
    # TRANSACTIONS (REVENUS / DÉPENSES / TRANSFERTS)
    # ==========================

    def add_income(self, wallet_id: int, category_id: Optional[int], amount_cents: int,
                   date_str: str = None, note: str = "") -> Transaction:
        if amount_cents <= 0:
            raise ValidationError("Le montant du revenu doit être supérieur à zéro.", "amount_cents")
        wallet = self.get_wallet(wallet_id)

        tx = Transaction(
            wallet_id=wallet_id,
            category_id=category_id,
            type=TX_INCOME,
            amount_cents=amount_cents,
            date=date_str or today_str(),
            note=note
        )

        with self.db.session() as conn:
            created_tx = self.transactions_repo.create(tx, conn=conn)
            self.wallets_repo.update_balance(wallet_id, amount_cents, conn=conn)

        android_bridge.vibrate(30)
        return created_tx

    def add_expense(self, wallet_id: int, category_id: Optional[int], amount_cents: int,
                    date_str: str = None, note: str = "") -> Tuple[Transaction, Optional[BudgetExceededWarning]]:
        if amount_cents <= 0:
            raise ValidationError("Le montant de la dépense doit être supérieur à zéro.", "amount_cents")
        wallet = self.get_wallet(wallet_id)

        tx = Transaction(
            wallet_id=wallet_id,
            category_id=category_id,
            type=TX_EXPENSE,
            amount_cents=amount_cents,
            date=date_str or today_str(),
            note=note
        )

        with self.db.session() as conn:
            created_tx = self.transactions_repo.create(tx, conn=conn)
            self.wallets_repo.update_balance(wallet_id, -amount_cents, conn=conn)

        android_bridge.vibrate(30)

        # Vérification des alertes budget
        warning = None
        if category_id:
            month = (date_str or today_str())[:7]
            budget = self.budgets_repo.get_by_category_and_month(category_id, month)
            if budget and budget.limit_cents > 0:
                start_d, end_d = get_month_date_range(month)
                all_expenses = self.transactions_repo.get_all(
                    category_id=category_id, tx_type=TX_EXPENSE,
                    start_date=start_d, end_date=end_d, limit=1000
                )
                total_cat_expense = sum(t.amount_cents for t in all_expenses)
                percent = int((total_cat_expense / budget.limit_cents) * 100)
                if percent >= budget.alert_threshold_percent:
                    cat = self.categories_repo.get_by_id(category_id)
                    cat_name = cat.name if cat else "Catégorie"
                    warning = BudgetExceededWarning(cat_name, budget.limit_cents, total_cat_expense)
                    android_bridge.send_notification("Alerte Budget LifeOS", str(warning))

        return created_tx, warning

    def transfer(self, source_wallet_id: int, dest_wallet_id: int, amount_cents: int,
                 fee_cents: int = 0, date_str: str = None, note: str = "") -> Transaction:
        if amount_cents <= 0:
            raise ValidationError("Le montant du transfert doit être supérieur à zéro.", "amount_cents")
        if source_wallet_id == dest_wallet_id:
            raise ValidationError("Le portefeuille source et destination doivent être différents.")

        source_wallet = self.get_wallet(source_wallet_id)
        dest_wallet = self.get_wallet(dest_wallet_id)

        total_deduction = amount_cents + fee_cents

        tx = Transaction(
            wallet_id=source_wallet_id,
            dest_wallet_id=dest_wallet_id,
            type=TX_TRANSFER,
            amount_cents=amount_cents,
            fee_cents=fee_cents,
            date=date_str or today_str(),
            note=note
        )

        with self.db.session() as conn:
            created_tx = self.transactions_repo.create(tx, conn=conn)
            # Débit source (montant + frais)
            self.wallets_repo.update_balance(source_wallet_id, -total_deduction, conn=conn)
            # Crédit destination (montant net)
            self.wallets_repo.update_balance(dest_wallet_id, amount_cents, conn=conn)

        android_bridge.vibrate(40)
        return created_tx

    def delete_transaction(self, tx_id: int) -> bool:
        tx = self.transactions_repo.get_by_id(tx_id)
        if not tx:
            raise EntityNotFoundError("Transaction", tx_id)

        with self.db.session() as conn:
            if tx.type == TX_INCOME:
                self.wallets_repo.update_balance(tx.wallet_id, -tx.amount_cents, conn=conn)
            elif tx.type == TX_EXPENSE:
                self.wallets_repo.update_balance(tx.wallet_id, tx.amount_cents, conn=conn)
            elif tx.type == TX_TRANSFER and tx.dest_wallet_id:
                total_deduction = tx.amount_cents + tx.fee_cents
                self.wallets_repo.update_balance(tx.wallet_id, total_deduction, conn=conn)
                self.wallets_repo.update_balance(tx.dest_wallet_id, -tx.amount_cents, conn=conn)

            return self.transactions_repo.delete(tx_id, conn=conn)

    # ==========================
    # BUDGETS
    # ==========================

    def set_budget(self, month: str, limit_cents: int, category_id: Optional[int] = None,
                   alert_threshold_percent: int = 80) -> Budget:
        if limit_cents < 0:
            raise ValidationError("Le budget ne peut pas être négatif.", "limit_cents")
        budget = Budget(
            category_id=category_id,
            month=month,
            limit_cents=limit_cents,
            alert_threshold_percent=alert_threshold_percent
        )
        return self.budgets_repo.upsert(budget)

    def get_budget_status(self, month: str = None) -> Dict:
        """Retourne l'état de consommation du budget global et des catégories pour le mois."""
        m = month or current_month_str()
        start_d, end_d = get_month_date_range(m)

        global_budget = self.budgets_repo.get_by_category_and_month(None, m)
        monthly_totals = self.transactions_repo.get_monthly_totals(start_d, end_d)
        total_expense = monthly_totals.get("expense", 0)

        limit_cents = global_budget.limit_cents if global_budget else 0
        consumed_percent = int((total_expense / limit_cents) * 100) if limit_cents > 0 else 0

        # Budgets par catégorie
        category_budgets = self.budgets_repo.get_all(month=m)
        cat_statuses = []
        for b in category_budgets:
            if b.category_id is None:
                continue
            cat = self.categories_repo.get_by_id(b.category_id)
            txs = self.transactions_repo.get_all(
                category_id=b.category_id, tx_type=TX_EXPENSE,
                start_date=start_d, end_date=end_d, limit=1000
            )
            cat_spent = sum(t.amount_cents for t in txs)
            cat_percent = int((cat_spent / b.limit_cents) * 100) if b.limit_cents > 0 else 0
            cat_statuses.append({
                "budget_id": b.id,
                "category_id": b.category_id,
                "category_name": cat.name if cat else "Catégorie",
                "category_color": cat.color if cat else "#9E9E9E",
                "category_icon": cat.icon if cat else "tag",
                "limit_cents": b.limit_cents,
                "spent_cents": cat_spent,
                "consumed_percent": cat_percent,
                "is_exceeded": cat_spent > b.limit_cents
            })

        return {
            "month": m,
            "global_limit_cents": limit_cents,
            "total_expense_cents": total_expense,
            "consumed_percent": consumed_percent,
            "is_exceeded": total_expense > limit_cents if limit_cents > 0 else False,
            "categories": cat_statuses
        }

    # ==========================
    # DETTES & CRÉANCES
    # ==========================

    def create_debt(self, party_name: str, amount_cents: int, debt_type: str = DEBT_OWED_BY_ME,
                    due_date: str = None, notes: str = "") -> Debt:
        if not party_name or not party_name.strip():
            raise ValidationError("Le nom de la personne ou entité est requis.", "party_name")
        if amount_cents <= 0:
            raise ValidationError("Le montant doit être supérieur à zéro.", "amount_cents")

        debt = Debt(
            party_name=party_name.strip(),
            amount_cents=amount_cents,
            paid_cents=0,
            type=debt_type,
            due_date=due_date,
            status=DEBT_STATUS_PENDING,
            notes=notes
        )
        return self.debts_repo.create(debt)

    def record_debt_payment(self, debt_id: int, amount_cents: int, wallet_id: Optional[int] = None,
                             payment_date: str = None, notes: str = "") -> DebtPayment:
        if amount_cents <= 0:
            raise ValidationError("Le montant du remboursement doit être positif.", "amount_cents")
        debt = self.debts_repo.get_by_id(debt_id)
        if not debt:
            raise EntityNotFoundError("Dette/Créance", debt_id)

        new_paid = debt.paid_cents + amount_cents
        if new_paid >= debt.amount_cents:
            new_status = DEBT_STATUS_PAID
        elif new_paid > 0:
            new_status = DEBT_STATUS_PARTIAL
        else:
            new_status = DEBT_STATUS_PENDING

        debt.paid_cents = new_paid
        debt.status = new_status

        payment = DebtPayment(
            debt_id=debt_id,
            amount_cents=amount_cents,
            payment_date=payment_date or today_str(),
            wallet_id=wallet_id,
            notes=notes
        )

        with self.db.session() as conn:
            created_payment = self.debts_repo.add_payment(payment, conn=conn)
            self.debts_repo.update(debt, conn=conn)

            # Si lié à un portefeuille, ajuster le solde
            if wallet_id:
                if debt.type == DEBT_OWED_BY_ME:
                    # Je rembourse ma dette -> sortie d'argent
                    self.wallets_repo.update_balance(wallet_id, -amount_cents, conn=conn)
                else:
                    # On me rembourse une créance -> entrée d'argent
                    self.wallets_repo.update_balance(wallet_id, amount_cents, conn=conn)

        android_bridge.vibrate(30)
        return created_payment

    # ==========================
    # ÉPARGNE & OBJECTIFS D'ÉPARGNE
    # ==========================

    def create_savings_goal(self, title: str, target_cents: int, target_date: str = None,
                            icon: str = "piggy-bank", color: str = "#66BB6A") -> SavingsGoal:
        if not title or not title.strip():
            raise ValidationError("Le titre de l'objectif d'épargne est requis.", "title")
        if target_cents <= 0:
            raise ValidationError("Le montant cible doit être supérieur à zéro.", "target_cents")

        goal = SavingsGoal(
            title=title.strip(),
            target_cents=target_cents,
            current_cents=0,
            target_date=target_date,
            icon=icon,
            color=color
        )
        return self.savings_repo.create(goal)

    def deposit_to_savings(self, goal_id: int, amount_cents: int, source_wallet_id: Optional[int] = None) -> SavingsGoal:
        if amount_cents <= 0:
            raise ValidationError("Le montant à épargner doit être supérieur à zéro.", "amount_cents")
        goal = self.savings_repo.get_by_id(goal_id)
        if not goal:
            raise EntityNotFoundError("Objectif d'épargne", goal_id)

        goal.current_cents += amount_cents
        if goal.current_cents >= goal.target_cents:
            goal.is_completed = True

        with self.db.session() as conn:
            self.savings_repo.update(goal, conn=conn)
            if source_wallet_id:
                self.wallets_repo.update_balance(source_wallet_id, -amount_cents, conn=conn)

        android_bridge.vibrate(40)
        if goal.is_completed:
            android_bridge.send_notification("Félicitations LifeOS 🎉", f"Objectif d'épargne '{goal.title}' atteint !")

        return goal

    # ==========================
    # STATISTIQUES & RAPPORTS
    # ==========================

    def get_monthly_report(self, month: str = None) -> Dict:
        m = month or current_month_str()
        start_d, end_d = get_month_date_range(m)

        totals = self.transactions_repo.get_monthly_totals(start_d, end_d)
        income = totals.get("income", 0)
        expense = totals.get("expense", 0)
        net_savings = income - expense
        savings_rate_percent = int((net_savings / income) * 100) if income > 0 else 0

        categories_breakdown = self.transactions_repo.get_expenses_by_category(start_d, end_d)

        return {
            "month": m,
            "income_cents": income,
            "expense_cents": expense,
            "net_savings_cents": net_savings,
            "savings_rate_percent": savings_rate_percent,
            "categories_breakdown": categories_breakdown
        }
