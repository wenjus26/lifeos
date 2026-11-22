"""
LifeOS - Habits Screen
Suivi quotidien des habitudes et visualisation des séries (streaks)
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button

from app.database.connection import db
from app.services.habit_service import HabitService
from app.components.dialogs import AddHabitDialog
from app.components.kpi_card import MetricCard


class HabitsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.habit_service = HabitService(db)

        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)

        # En-tête
        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=56, padding=[16, 8, 16, 8])
        lbl_title = Label(
            text="[b]SUIVI DES HABITUDES[/b]",
            markup=True,
            font_size="18sp",
            halign="left",
            valign="middle",
            color=(0.15, 0.65, 0.60, 1)
        )
        lbl_title.bind(size=lbl_title.setter('text_size'))
        top_bar.add_widget(lbl_title)

        btn_add = Button(
            text="+ Habitude",
            font_size="12sp",
            size_hint_x=None,
            width=90,
            background_color=(0.15, 0.65, 0.60, 1)
        )
        btn_add.bind(on_release=self._open_add_habit)
        top_bar.add_widget(btn_add)
        root.add_widget(top_bar)

        # Contenu défilant
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(
            orientation="vertical",
            padding=[16, 12, 16, 20],
            spacing=12,
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        root.add_widget(self.scroll)

        self.add_widget(root)

    def on_enter(self, *args):
        self.refresh()

    def refresh(self):
        self.content.clear_widgets()
        habits = self.habit_service.get_habits()

        if not habits:
            self.content.add_widget(Label(
                text="Aucune habitude définie. Cliquez sur '+ Habitude' pour commencer !",
                font_size="13sp",
                size_hint_y=None,
                height=40,
                color=(0.5, 0.5, 0.5, 1)
            ))
            return

        for h in habits:
            stats = self.habit_service.get_habit_stats(h.id)

            card = MetricCard(
                title=f"{h.title}",
                value=f"Série : {stats['current_streak']} jours 🔥",
                subtitle=f"Record : {stats['longest_streak']}j • Taux 30j : {stats['rate_last_30_days']}%",
                size_hint_y=None,
                height=85,
                accent_color=[0.95, 0.70, 0.20, 1.0]
            )

            # Ligne de contrôle (Valider pour aujourd'hui + Supprimer)
            ctrl_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=44, spacing=8)
            is_done = stats["is_completed_today"]
            btn_toggle = Button(
                text="✓ Validé pour aujourd'hui" if is_done else "○ Valider aujourd'hui",
                font_size="12sp",
                background_color=(0.15, 0.65, 0.60, 1) if is_done else (0.3, 0.35, 0.4, 1)
            )
            btn_toggle.bind(on_release=lambda x, hid=h.id: self._toggle_habit(hid))

            btn_del = Button(
                text="Supprimer",
                font_size="11sp",
                size_hint_x=None,
                width=80,
                background_color=(0.4, 0.2, 0.2, 1)
            )
            btn_del.bind(on_release=lambda x, hid=h.id: self._delete_habit(hid))

            ctrl_row.add_widget(btn_toggle)
            ctrl_row.add_widget(btn_del)

            self.content.add_widget(card)
            self.content.add_widget(ctrl_row)

    def _open_add_habit(self, *args):
        dialog = AddHabitDialog(on_save_callback=self._handle_add_habit)
        dialog.open()

    def _handle_add_habit(self, title, frequency):
        self.habit_service.create_habit(title=title, frequency=frequency)
        self.refresh()

    def _toggle_habit(self, habit_id: int):
        self.habit_service.toggle_today(habit_id)
        self.refresh()

    def _delete_habit(self, habit_id: int):
        self.habit_service.delete_habit(habit_id)
        self.refresh()
