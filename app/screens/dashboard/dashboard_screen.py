"""
LifeOS - Dashboard Screen
Écran d'accueil unifié affichant les métriques temps réel de tous les modules
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line

from app.database.connection import db
from app.services.dashboard_service import DashboardService
from app.services.finance_service import FinanceService
from app.services.task_service import TaskService
from app.services.habit_service import HabitService
from app.components.kpi_card import MetricCard
from app.components.chart_widget import ProgressBarWidget
from app.components.dialogs import AddTransactionDialog, AddTaskDialog, AddHabitDialog
from app.utils.currency import format_currency, format_compact_amount
from app.utils.android_native import android_bridge


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dash_service = DashboardService(db)
        self.finance_service = FinanceService(db)
        self.task_service = TaskService(db)
        self.habit_service = HabitService(db)

        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)

        # En-tête fixe supérieur
        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=56, padding=[16, 8, 16, 8])
        lbl_app = Label(
            text="[b]LIFE[color=26A69A]OS[/color][/b]",
            markup=True,
            font_size="22sp",
            halign="left",
            valign="middle",
            size_hint_x=0.7
        )
        lbl_app.bind(size=lbl_app.setter('text_size'))
        top_bar.add_widget(lbl_app)

        self.lbl_score = Label(
            text="Productivité : 100%",
            font_size="12sp",
            halign="right",
            valign="middle",
            size_hint_x=0.3,
            color=(0.15, 0.65, 0.60, 1)
        )
        self.lbl_score.bind(size=self.lbl_score.setter('text_size'))
        top_bar.add_widget(self.lbl_score)
        root.add_widget(top_bar)

        # Contenu défilant
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(
            orientation="vertical",
            padding=[16, 8, 16, 20],
            spacing=16,
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        root.add_widget(self.scroll)

        self.add_widget(root)

    def on_enter(self, *args):
        """Recharge les données dynamiques à chaque affichage de l'écran."""
        self.refresh()

    def refresh(self):
        data = self.dash_service.get_dashboard_data()
        self.lbl_score.text = f"Score : {data['productivity_score']}%"
        self.content.clear_widgets()

        # 1. Carte Solde Total Disponible
        self.card_balance = MetricCard(
            title="Solde Disponible Global",
            value=format_currency(data["total_balance_cents"]),
            subtitle="Cumul de tous vos portefeuilles",
            size_hint_y=None,
            height=100,
            accent_color=[0.15, 0.75, 0.65, 1.0]
        )
        self.content.add_widget(self.card_balance)

        # 2. Deux colonnes : Revenus & Dépenses du mois
        row_cashflow = GridLayout(cols=2, spacing=10, size_hint_y=None, height=92)
        card_income = MetricCard(
            title="Revenus Mois",
            value=format_compact_amount(data["month_income_cents"]),
            accent_color=[0.40, 0.75, 0.40, 1.0]
        )
        card_expense = MetricCard(
            title="Dépenses Mois",
            value=format_compact_amount(data["month_expense_cents"]),
            accent_color=[0.95, 0.45, 0.40, 1.0]
        )
        row_cashflow.add_widget(card_income)
        row_cashflow.add_widget(card_expense)
        self.content.add_widget(row_cashflow)

        # 3. Jauge de Budget Consommé
        b_box = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None, height=70)
        lbl_b = Label(
            text=f"Budget mensuel : [b]{data['budget_consumed_percent']}% consommé[/b]",
            markup=True,
            font_size="13sp",
            size_hint_y=None,
            height=20,
            halign="left"
        )
        lbl_b.bind(size=lbl_b.setter('text_size'))
        b_box.add_widget(lbl_b)

        bar_color = [0.9, 0.3, 0.3, 1] if data["is_budget_exceeded"] else [0.15, 0.65, 0.60, 1]
        progress_bar = ProgressBarWidget(
            progress=data["budget_consumed_percent"],
            bar_color=bar_color,
            size_hint_y=None,
            height=10
        )
        b_box.add_widget(progress_bar)
        self.content.add_widget(b_box)

        # 4. Actions rapides (+ Dépense, + Tâche, + Habitude)
        actions_row = GridLayout(cols=3, spacing=8, size_hint_y=None, height=44)

        btn_tx = Button(
            text="+ Transaction",
            font_size="11sp",
            background_color=(0.15, 0.65, 0.60, 1.0)
        )
        btn_tx.bind(on_release=self._open_add_transaction)

        btn_task = Button(
            text="+ Tâche",
            font_size="11sp",
            background_color=(0.25, 0.45, 0.70, 1.0)
        )
        btn_task.bind(on_release=self._open_add_task)

        btn_habit = Button(
            text="+ Habitude",
            font_size="11sp",
            background_color=(0.55, 0.35, 0.70, 1.0)
        )
        btn_habit.bind(on_release=self._open_add_habit)

        actions_row.add_widget(btn_tx)
        actions_row.add_widget(btn_task)
        actions_row.add_widget(btn_habit)
        self.content.add_widget(actions_row)

        # 5. Tâches du Jour
        self.content.add_widget(Label(
            text="[b]TÂCHES DU JOUR[/b]",
            markup=True,
            font_size="13sp",
            size_hint_y=None,
            height=26,
            halign="left",
            color=(0.8, 0.8, 0.8, 1)
        ))

        today_tasks = data["today_tasks"]
        if not today_tasks:
            self.content.add_widget(Label(
                text="Aucune tâche en attente. Tout est sous contrôle !",
                font_size="12sp",
                size_hint_y=None,
                height=30,
                color=(0.5, 0.5, 0.5, 1)
            ))
        else:
            for task in today_tasks[:4]:
                t_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=44, spacing=8)
                btn_chk = Button(
                    text="✓" if task.is_completed else "○",
                    size_hint_x=None,
                    width=40,
                    background_color=(0.15, 0.65, 0.60, 1) if task.is_completed else (0.3, 0.3, 0.3, 1)
                )
                btn_chk.bind(on_release=lambda x, tid=task.id: self._toggle_task(tid))

                strike = "[s]" if task.is_completed else ""
                end_strike = "[/s]" if task.is_completed else ""
                lbl_t = Label(
                    text=f"{strike}{task.title}{end_strike}",
                    markup=True,
                    font_size="13sp",
                    halign="left",
                    valign="middle"
                )
                lbl_t.bind(size=lbl_t.setter('text_size'))

                t_row.add_widget(btn_chk)
                t_row.add_widget(lbl_t)
                self.content.add_widget(t_row)

        # 6. Habitudes Quotidiennes
        self.content.add_widget(Label(
            text="[b]HABITUDES DU JOUR[/b]",
            markup=True,
            font_size="13sp",
            size_hint_y=None,
            height=26,
            halign="left",
            color=(0.8, 0.8, 0.8, 1)
        ))

        today_habits = data["today_habits"]
        if not today_habits:
            self.content.add_widget(Label(
                text="Aucune habitude configurée.",
                font_size="12sp",
                size_hint_y=None,
                height=30,
                color=(0.5, 0.5, 0.5, 1)
            ))
        else:
            for item in today_habits[:4]:
                h = item["habit"]
                is_done = item["completed_today"]
                streak = item["current_streak"]

                h_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=44, spacing=8)
                btn_h = Button(
                    text="★" if is_done else "☆",
                    size_hint_x=None,
                    width=40,
                    background_color=(0.95, 0.70, 0.20, 1) if is_done else (0.3, 0.3, 0.3, 1)
                )
                btn_h.bind(on_release=lambda x, hid=h.id: self._toggle_habit(hid))

                lbl_h = Label(
                    text=f"[b]{h.title}[/b]  [size=11sp][color=FFA726]Série : {streak}j[/color][/size]",
                    markup=True,
                    font_size="13sp",
                    halign="left",
                    valign="middle"
                )
                lbl_h.bind(size=lbl_h.setter('text_size'))

                h_row.add_widget(btn_h)
                h_row.add_widget(lbl_h)
                self.content.add_widget(h_row)

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

    def _open_add_task(self, *args):
        dialog = AddTaskDialog(on_save_callback=self._handle_add_task)
        dialog.open()

    def _handle_add_task(self, title, priority, due_date):
        self.task_service.create_task(title=title, priority=priority, due_date=due_date)
        self.refresh()

    def _open_add_habit(self, *args):
        dialog = AddHabitDialog(on_save_callback=self._handle_add_habit)
        dialog.open()

    def _handle_add_habit(self, title, frequency):
        self.habit_service.create_habit(title=title, frequency=frequency)
        self.refresh()

    def _toggle_task(self, task_id: int):
        self.task_service.toggle_task(task_id)
        self.refresh()

    def _toggle_habit(self, habit_id: int):
        self.habit_service.toggle_today(habit_id)
        self.refresh()
