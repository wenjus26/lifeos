"""
LifeOS - Tasks Screen
Gestion complète des tâches avec priorités, sous-tâches et filtres
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button

from app.database.connection import db
from app.services.task_service import TaskService
from app.components.dialogs import AddTaskDialog
from app.core.constants import PRIORITY_URGENT, PRIORITY_HIGH


class TasksScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_service = TaskService(db)
        self.current_filter = "all"

        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)

        # En-tête
        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=56, padding=[16, 8, 16, 8])
        lbl_title = Label(
            text="[b]GESTION DES TÂCHES[/b]",
            markup=True,
            font_size="18sp",
            halign="left",
            valign="middle",
            color=(0.15, 0.65, 0.60, 1)
        )
        lbl_title.bind(size=lbl_title.setter('text_size'))
        top_bar.add_widget(lbl_title)

        btn_add = Button(
            text="+ Tâche",
            font_size="12sp",
            size_hint_x=None,
            width=80,
            background_color=(0.15, 0.65, 0.60, 1)
        )
        btn_add.bind(on_release=self._open_add_task)
        top_bar.add_widget(btn_add)
        root.add_widget(top_bar)

        # Filtres (Toutes, Aujourd'hui, Urgentes, Terminées)
        filter_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=4, padding=[8, 2, 8, 2])
        self.filter_buttons = {}
        filters = [
            ("all", "En cours"),
            ("today", "Aujourd'hui"),
            ("urgent", "Urgentes"),
            ("done", "Terminées")
        ]
        for fid, flabel in filters:
            btn = Button(
                text=flabel,
                font_size="11sp",
                background_color=(0.15, 0.65, 0.60, 1) if fid == "all" else (0.2, 0.22, 0.26, 1)
            )
            btn.bind(on_release=lambda x, f_id=fid: self._switch_filter(f_id))
            self.filter_buttons[fid] = btn
            filter_bar.add_widget(btn)
        root.add_widget(filter_bar)

        # Contenu défilant
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(
            orientation="vertical",
            padding=[16, 12, 16, 20],
            spacing=10,
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        root.add_widget(self.scroll)

        self.add_widget(root)

    def on_enter(self, *args):
        self.refresh()

    def _switch_filter(self, f_id: str):
        self.current_filter = f_id
        for fid, btn in self.filter_buttons.items():
            btn.background_color = (0.15, 0.65, 0.60, 1) if fid == f_id else (0.2, 0.22, 0.26, 1)
        self.refresh()

    def refresh(self):
        self.content.clear_widgets()

        if self.current_filter == "all":
            tasks = self.task_service.get_tasks(include_completed=False)
        elif self.current_filter == "today":
            tasks = self.task_service.get_today_tasks()
        elif self.current_filter == "urgent":
            tasks = self.task_service.get_tasks(priority=PRIORITY_URGENT, include_completed=False)
        else:
            all_t = self.task_service.get_tasks(include_completed=True)
            tasks = [t for t in all_t if t.is_completed]

        if not tasks:
            self.content.add_widget(Label(
                text="Aucune tâche dans cette vue.",
                font_size="13sp",
                size_hint_y=None,
                height=40,
                color=(0.5, 0.5, 0.5, 1)
            ))
            return

        for task in tasks:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=54, spacing=10)

            btn_chk = Button(
                text="✓" if task.is_completed else "○",
                size_hint_x=None,
                width=42,
                background_color=(0.15, 0.65, 0.60, 1) if task.is_completed else (0.3, 0.3, 0.3, 1)
            )
            btn_chk.bind(on_release=lambda x, tid=task.id: self._toggle_task(tid))

            p_color = "EF5350" if task.priority in (PRIORITY_URGENT, PRIORITY_HIGH) else "9E9E9E"
            due_txt = f" • Échéance : {task.due_date}" if task.due_date else ""

            strike = "[s]" if task.is_completed else ""
            end_strike = "[/s]" if task.is_completed else ""

            lbl_info = Label(
                text=f"{strike}[b]{task.title}[/b]{end_strike}\n[size=11sp][color={p_color}]{task.priority.upper()}[/color]{due_txt}[/size]",
                markup=True,
                font_size="13sp",
                halign="left",
                valign="middle",
                size_hint_x=0.75
            )
            lbl_info.bind(size=lbl_info.setter('text_size'))

            btn_del = Button(
                text="✕",
                size_hint_x=None,
                width=36,
                background_color=(0.5, 0.2, 0.2, 1)
            )
            btn_del.bind(on_release=lambda x, tid=task.id: self._delete_task(tid))

            row.add_widget(btn_chk)
            row.add_widget(lbl_info)
            row.add_widget(btn_del)
            self.content.add_widget(row)

    def _open_add_task(self, *args):
        dialog = AddTaskDialog(on_save_callback=self._handle_add_task)
        dialog.open()

    def _handle_add_task(self, title, priority, due_date):
        self.task_service.create_task(title=title, priority=priority, due_date=due_date)
        self.refresh()

    def _toggle_task(self, task_id: int):
        self.task_service.toggle_task(task_id)
        self.refresh()

    def _delete_task(self, task_id: int):
        self.task_service.delete_task(task_id)
        self.refresh()
