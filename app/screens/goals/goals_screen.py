"""
LifeOS - Goals Screen
Gestion des objectifs personnels, professionnels et financiers avec jalons
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from app.database.connection import db
from app.services.goal_service import GoalService
from app.components.kpi_card import MetricCard
from app.components.chart_widget import ProgressBarWidget
from app.components.dialogs import BaseModal


class AddGoalDialog(BaseModal):
    def __init__(self, on_save_callback, **kwargs):
        super().__init__("Nouvel Objectif", **kwargs)
        self.on_save_callback = on_save_callback
        self.height = 300

        self.txt_title = TextInput(
            hint_text="Intitulé de l'objectif (ex: Lancer mon entreprise)",
            multiline=False,
            size_hint_y=None,
            height=44,
            background_color=(0.18, 0.20, 0.25, 1.0),
            foreground_color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.txt_title)

        self.txt_milestones = TextInput(
            hint_text="Jalons séparés par virgule (ex: Plan, Budget, Lancement)",
            multiline=False,
            size_hint_y=None,
            height=44,
            background_color=(0.18, 0.20, 0.25, 1.0),
            foreground_color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.txt_milestones)

        actions = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=44)
        btn_cancel = Button(text="Annuler", background_color=(0.4, 0.4, 0.4, 1))
        btn_cancel.bind(on_release=lambda x: self.dismiss())

        btn_save = Button(text="Créer l'objectif", background_color=(0.15, 0.65, 0.60, 1))
        btn_save.bind(on_release=self._save)

        actions.add_widget(btn_cancel)
        actions.add_widget(btn_save)
        self.container.add_widget(actions)

    def _save(self, *args):
        title = self.txt_title.text.strip()
        if not title:
            return
        ms_text = self.txt_milestones.text.strip()
        milestones = [m.strip() for m in ms_text.split(",") if m.strip()] if ms_text else []
        self.on_save_callback(title=title, milestones=milestones)
        self.dismiss()


class GoalsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.goal_service = GoalService(db)

        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)

        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=56, padding=[16, 8, 16, 8])
        lbl_title = Label(
            text="[b]OBJECTIFS DE VIE[/b]",
            markup=True,
            font_size="18sp",
            halign="left",
            valign="middle",
            color=(0.15, 0.65, 0.60, 1)
        )
        lbl_title.bind(size=lbl_title.setter('text_size'))
        top_bar.add_widget(lbl_title)

        btn_add = Button(
            text="+ Objectif",
            font_size="12sp",
            size_hint_x=None,
            width=90,
            background_color=(0.15, 0.65, 0.60, 1)
        )
        btn_add.bind(on_release=self._open_add_goal)
        top_bar.add_widget(btn_add)
        root.add_widget(top_bar)

        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(
            orientation="vertical",
            padding=[16, 12, 16, 20],
            spacing=16,
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
        goals = self.goal_service.get_goals(include_completed=True)

        if not goals:
            self.content.add_widget(Label(
                text="Aucun objectif défini. Ajoutez votre premier grand projet !",
                font_size="13sp",
                size_hint_y=None,
                height=40,
                color=(0.5, 0.5, 0.5, 1)
            ))
            return

        for goal in goals:
            card_box = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None, height=100)
            card = MetricCard(
                title=f"Objectif : {goal.title}",
                value=f"Progression : {goal.progress_percent}%",
                subtitle=f"Jalons : {len(goal.milestones)} étapes",
                size_hint_y=None,
                height=70,
                accent_color=[0.15, 0.65, 0.60, 1] if not goal.is_completed else [0.4, 0.8, 0.4, 1]
            )
            bar = ProgressBarWidget(
                progress=goal.progress_percent,
                bar_color=[0.15, 0.65, 0.60, 1] if not goal.is_completed else [0.4, 0.8, 0.4, 1],
                size_hint_y=None,
                height=8
            )
            card_box.add_widget(card)
            card_box.add_widget(bar)
            self.content.add_widget(card_box)

            # Liste des jalons
            for ms in goal.milestones:
                ms_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=36, spacing=8, padding=[12, 0, 0, 0])
                btn_ms = Button(
                    text="✓" if ms.is_completed else "○",
                    size_hint_x=None,
                    width=32,
                    background_color=(0.15, 0.65, 0.60, 1) if ms.is_completed else (0.3, 0.3, 0.3, 1)
                )
                btn_ms.bind(on_release=lambda x, gid=goal.id, mid=ms.id, curr=ms.is_completed: self._toggle_ms(gid, mid, not curr))

                lbl_ms = Label(
                    text=f"[size=12sp]{ms.title}[/size]",
                    markup=True,
                    halign="left",
                    valign="middle"
                )
                lbl_ms.bind(size=lbl_ms.setter('text_size'))

                ms_row.add_widget(btn_ms)
                ms_row.add_widget(lbl_ms)
                self.content.add_widget(ms_row)

    def _open_add_goal(self, *args):
        dialog = AddGoalDialog(on_save_callback=self._handle_add_goal)
        dialog.open()

    def _handle_add_goal(self, title, milestones):
        self.goal_service.create_goal(title=title, milestone_titles=milestones)
        self.refresh()

    def _toggle_ms(self, goal_id: int, milestone_id: int, new_val: bool):
        self.goal_service.toggle_milestone(goal_id, milestone_id, new_val)
        self.refresh()
