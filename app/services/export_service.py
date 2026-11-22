"""
LifeOS - Export Service
Exportation des transactions en CSV et génération de rapports
"""
import csv
import os
from typing import Optional
from app.database.connection import db, DatabaseManager
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.wallet_repository import WalletRepository
from app.repositories.category_repository import CategoryRepository
from app.config.settings import settings
from app.utils.currency import format_currency
from app.utils.date_utils import now_iso, today_str


class ExportService:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager
        self.tx_repo = TransactionRepository(db_manager)
        self.wallet_repo = WalletRepository(db_manager)
        self.cat_repo = CategoryRepository(db_manager)

    def export_transactions_csv(self, output_path: Optional[str] = None) -> str:
        """Exporte l'historique des transactions dans un fichier CSV standard."""
        if not output_path:
            filename = f"lifeos_transactions_{today_str()}.csv"
            output_path = os.path.join(settings.exports_directory, filename)

        wallets = {w.id: w.name for w in self.wallet_repo.get_all(include_archived=True)}
        categories = {c.id: c.name for c in self.cat_repo.get_all()}
        transactions = self.tx_repo.get_all(limit=10000)

        with open(output_path, mode="w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")
            # En-têtes
            writer.writerow(["ID", "Date", "Type", "Montant", "Portefeuille", "Catégorie", "Note", "Frais"])

            for tx in transactions:
                w_name = wallets.get(tx.wallet_id, "Inconnu")
                c_name = categories.get(tx.category_id, "Non catégorisé") if tx.category_id else ""
                writer.writerow([
                    tx.id,
                    tx.date,
                    tx.type,
                    format_currency(tx.amount_cents),
                    w_name,
                    c_name,
                    tx.note or "",
                    format_currency(tx.fee_cents) if tx.fee_cents else "0"
                ])

        return output_path

    def export_financial_summary_text(self, month: str) -> str:
        """Génère un résumé financier structuré pour le partage ou l'impression."""
        from app.services.finance_service import FinanceService
        fin = FinanceService(self.db)
        rep = fin.get_monthly_report(month)

        lines = [
            f"=== RAPPORT FINANCIER LIFEOS — {rep['month']} ===",
            f"Revenus Totaux : {format_currency(rep['income_cents'])}",
            f"Dépenses Totales : {format_currency(rep['expense_cents'])}",
            f"Épargne Nette : {format_currency(rep['net_savings_cents'])}",
            f"Taux d'Épargne : {rep['savings_rate_percent']}%",
            "",
            "--- DÉPENSES PAR CATÉGORIE ---"
        ]

        for cat in rep["categories_breakdown"]:
            lines.append(f"• {cat['name']} : {format_currency(cat['total_cents'])}")

        lines.append(f"\nGénéré hors connexion le {now_iso()}")
        return "\n".join(lines)
