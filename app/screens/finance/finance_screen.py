"""
LifeOS - Finance Screen
Hub financier complet : Portefeuilles, Transactions, Budgets, Dettes, Épargne et Exports
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line

from app.database.connection import db
from app.services.finance_service import FinanceService
from app.services.export_service import ExportService
from app.components.kpi_card import MetricCard
from app.components.chart_widget import CategoryBarWidget
from app.components.dialogs import AddTransactionDialog
from app.utils.currency import format_currency
from app.core.constants import TX_EXPENSE, TX_INCOME, TX_TRANSFER


class FinanceScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.finance_service = FinanceService(db)
        self.export_service = ExportService(db)
        self.current_subtab = "overview"

        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)

        # En-tête
        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=56, padding=[16, 8, 16, 8])
        lbl_title = Label(
            text="[b]GESTION FINANCIÈRE[/b]",
            markup=True,
            font_size="18sp",
            halign="left",
            valign="middle",
            color=(0.15, 0.65, 0.60, 1)
        )
        lbl_title.bind(size=lbl_title.setter('text_size'))
        top_bar.add_widget(lbl_title)

        btn_csv = Button(
            text="Export CSV",
            font_size="11sp",
            size_hint_x=None,
            width=90,
            background_color=(0.20, 0.50, 0.40, 1)
        )
        btn_csv.bind(on_release=self._export_csv)
        top_bar.add_widget(btn_csv)
        root.add_widget(top_bar)

        # Sous-onglets (Aperçu, Transactions, Budgets, Dettes, Épargne)
        subtab_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=4, padding=[8, 2, 8, 2])
        self.tab_buttons = {}
        tabs = [
            ("overview", "Aperçu"),
            ("txs", "Historique"),
            ("budgets", "Budgets"),
            ("debts", "Dettes"),
            ("savings", "Épargne")
        ]
        for tid, tlabel in tabs:
            btn = Button(
                text=tlabel,
                font_size="11sp",
                background_color=(0.15, 0.65, 0.60, 1) if tid == "overview" else (0.2, 0.22, 0.26, 1)
            )
            btn.bind(on_release=lambda x, sub_id=tid: self._switch_subtab(sub_id))
            self.tab_buttons[tid] = btn
            subtab_bar.add_widget(btn)
        root.add_widget(subtab_bar)

        # Contenu défilant
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(
            orientation="vertical",
            padding=[16, 12, 16, 20],
            spacing=14,
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        root.add_widget(self.scroll)

        self.add_widget(root)

    def on_enter(self, *args):
        self.refresh()

    def _switch_subtab(self, sub_id: str):
        self.current_subtab = sub_id
        for tid, btn in self.tab_buttons.items():
            btn.background_color = (0.15, 0.65, 0.60, 1) if tid == sub_id else (0.2, 0.22, 0.26, 1)
        self.refresh()

    def refresh(self):
        self.content.clear_widgets()
        if self.current_subtab == "overview":
            self._render_overview()
        elif self.current_subtab == "txs":
            self._render_transactions()
        elif self.current_subtab == "budgets":
            self._render_budgets()
        elif self.current_subtab == "debts":
            self._render_debts()
        elif self.current_subtab == "savings":
            self._render_savings()

    def _render_overview(self):
        # 1. Portefeuilles
        self.content.add_widget(Label(
            text="[b]MES PORTEFEUILLES[/b]",
            markup=True,
            font_size="13sp",
            size_hint_y=None,
            height=24,
            halign="left"
        ))
        wallets = self.finance_service.get_wallets()
        for w in wallets:
            w_card = MetricCard(
                title=w.name,
                value=format_currency(w.balance_cents, w.currency),
                subtitle=f"Type: {w.type.upper()}",
                size_hint_y=None,
                height=80,
                accent_color=[0.15, 0.65, 0.60, 1.0]
            )
            self.content.add_widget(w_card)

        # 2. Répartition des dépenses du mois
        self.content.add_widget(Label(
            text="[b]DÉPENSES PAR CATÉGORIE CE MOIS[/b]",
            markup=True,
            font_size="13sp",
            size_hint_y=None,
            height=28,
            halign="left"
        ))
        rep = self.finance_service.get_monthly_report()
        total_exp = rep["expense_cents"]

        if not rep["categories_breakdown"]:
            self.content.add_widget(Label(
                text="Aucune dépense enregistrée ce mois-ci.",
                font_size="12sp",
                size_hint_y=None,
                height=30,
                color=(0.5, 0.5, 0.5, 1)
            ))
        else:
            for cat in rep["categories_breakdown"]:
                pct = int((cat["total_cents"] / total_exp) * 100) if total_exp > 0 else 0
                bar = CategoryBarWidget(
                    name=cat["name"],
                    amount_str=format_currency(cat["total_cents"]),
                    percent=pct,
                    color_hex=cat["color"]
                )
                self.content.add_widget(bar)

    def _render_transactions(self):
        btn_add = Button(
            text="+ Nouvelle Transaction",
            font_size="13sp",
            size_hint_y=None,
            height=44,
            background_color=(0.15, 0.65, 0.60, 1)
        )
        btn_add.bind(on_release=self._open_add_transaction)
        self.content.add_widget(btn_add)

        txs = self.finance_service.transactions_repo.get_all(limit=50)
        categories = {c.id: c.name for c in self.finance_service.categories_repo.get_all()}
        wallets = {w.id: w.name for w in self.finance_service.get_wallets(include_archived=True)}

        if not txs:
            self.content.add_widget(Label(
                text="Aucune transaction enregistrée.",
                font_size="12sp",
                size_hint_y=None,
                height=40,
                color=(0.5, 0.5, 0.5, 1)
            ))
            return

        for tx in txs:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=52, spacing=8)
            sign = "+" if tx.type == TX_INCOME else "-"
            amt_color = "66BB6A" if tx.type == TX_INCOME else "EF5350"
            c_name = categories.get(tx.category_id, "Non catégorisé")
            w_name = wallets.get(tx.wallet_id, "Portefeuille")

            lbl_info = Label(
                text=f"[b]{c_name}[/b]\n[size=11sp]{w_name} • {tx.date}[/size]",
                markup=True,
                font_size="13sp",
                halign="left",
                valign="middle",
                size_hint_x=0.6
            )
            lbl_info.bind(size=lbl_info.setter('text_size'))

            lbl_amt = Label(
                text=f"[b][color={amt_color}]{sign}{format_currency(tx.amount_cents)}[/color][/b]",
                markup=True,
                font_size="13sp",
                halign="right",
                valign="middle",
                size_hint_x=0.4
            )
            lbl_amt.bind(size=lbl_amt.setter('text_size'))

            row.add_widget(lbl_info)
            row.add_widget(lbl_amt)
            self.content.add_widget(row)

    def _render_budgets(self):
        status = self.finance_service.get_budget_status()
        self.content.add_widget(MetricCard(
            title="Budget Global Consommé",
            value=f"{status['consumed_percent']}%",
            subtitle=f"{format_currency(status['total_expense_cents'])} / {format_currency(status['global_limit_cents'])}",
            size_hint_y=None,
            height=90,
            accent_color=[0.9, 0.3, 0.3, 1] if status["is_exceeded"] else [0.15, 0.65, 0.60, 1]
        ))

        self.content.add_widget(Label(
            text="[b]BUDGETS PAR CATÉGORIE[/b]",
            markup=True,
            font_size="13sp",
            size_hint_y=None,
            height=26,
            halign="left"
        ))

        for cat_b in status["categories"]:
            bar = CategoryBarWidget(
                name=cat_b["category_name"],
                amount_str=f"{format_currency(cat_b['spent_cents'])} / {format_currency(cat_b['limit_cents'])}",
                percent=cat_b["consumed_percent"],
                color_hex=cat_b["category_color"]
            )
            self.content.add_widget(bar)

    def _render_debts(self):
        debts = self.finance_service.debts_repo.get_all()
        if not debts:
            self.content.add_widget(Label(
                text="Aucune dette ou créance en cours.",
                font_size="12sp",
                size_hint_y=None,
                height=40,
                color=(0.5, 0.5, 0.5, 1)
            ))
            return

        for d in debts:
            color = [0.9, 0.4, 0.3, 1] if d.type == "debt" else [0.3, 0.7, 0.4, 1]
            title_prefix = "Dette envers" if d.type == "debt" else "Créance sur"
            card = MetricCard(
                title=f"{title_prefix} {d.party_name}",
                value=f"Reste : {format_currency(d.remaining_cents)}",
                subtitle=f"Total: {format_currency(d.amount_cents)} • Statut: {d.status.upper()}",
                size_hint_y=None,
                height=90,
                accent_color=color
            )
            self.content.add_widget(card)

    def _render_savings(self):
        goals = self.finance_service.savings_repo.get_all()
        if not goals:
            self.content.add_widget(Label(
                text="Aucun objectif d'épargne créé.",
                font_size="12sp",
                size_hint_y=None,
                height=40,
                color=(0.5, 0.5, 0.5, 1)
            ))
            return

        for g in goals:
            card = MetricCard(
                title=f"Épargne : {g.title}",
                value=f"{format_currency(g.current_cents)} ({g.progress_percent}%)",
                subtitle=f"Cible : {format_currency(g.target_cents)}",
                size_hint_y=None,
                height=90,
                accent_color=[0.3, 0.7, 0.4, 1]
            )
            self.content.add_widget(card)

    def _open_add_transaction(self, *args):
        wallets = self.finance_service.get_wallets()
        categories = self.finance_service.categories_repo.get_all()
        dialog = AddTransactionDialog(
            wallets=wallets,
            categories=categories,
            on_save_callback=self._handle_add_transaction
        )
        dialog.open()

    def _handle_add_transaction(self, tx_type, wallet_id, category_id, amount_cents, note):
        if tx_type == "expense":
            self.finance_service.add_expense(wallet_id, category_id, amount_cents, note=note)
        else:
            self.finance_service.add_income(wallet_id, category_id, amount_cents, note=note)
        self.refresh()

    def _export_csv(self, *args):
        path = self.export_service.export_transactions_csv()
        print(f"Export CSV sauvegardé : {path}")
