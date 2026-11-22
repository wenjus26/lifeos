"""
LifeOS - Calendar Screen
Vue calendrier et agenda intégré (événements, rendez-vous, tâches du jour)
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from app.database.connection import db
from app.services.calendar_service import CalendarService
from app.components.dialogs import BaseModal
from app.utils.date_utils import today_str, format_date_fr


class AddEventDialog(BaseModal):
    def __init__(self, on_save_callback, **kwargs):
        super().__init__("Nouvel Événement", **kwargs)
        self.on_save_callback = on_save_callback
        self.height = 300

        self.txt_title = TextInput(
            hint_text="Titre (ex: Rendez-vous Médical)",
            multiline=False,
            size_hint_y=None,
            height=44,
            background_color=(0.18, 0.20, 0.25, 1.0),
            foreground_color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.txt_title)

        self.txt_date = TextInput(
            hint_text="Date (YYYY-MM-DD, ex: 2026-11-25)",
            multiline=False,
            size_hint_y=None,
            height=44,
            background_color=(0.18, 0.20, 0.25, 1.0),
            foreground_color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.txt_date)

        actions = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=44)
        btn_cancel = Button(text="Annuler", background_color=(0.4, 0.4, 0.4, 1))
        btn_cancel.bind(on_release=lambda x: self.dismiss())

        btn_save = Button(text="Créer l'événement", background_color=(0.15, 0.65, 0.60, 1))
        btn_save.bind(on_release=self._save)

        actions.add_widget(btn_cancel)
        actions.add_widget(btn_save)
        self.container.add_widget(actions)

    def _save(self, *args):
        title = self.txt_title.text.strip()
        date_val = self.txt_date.text.strip() or today_str()
        if not title:
            return
        start_dt = f"{date_val}T09:00:00"
        end_dt = f"{date_val}T10:00:00"
        self.on_save_callback(title=title, start_dt=start_dt, end_dt=end_dt)
        self.dismiss()


class CalendarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cal_service = CalendarService(db)

        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)

        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=56, padding=[16, 8, 16, 8])
        lbl_title = Label(
            text="[b]CALENDRIER & AGENDA[/b]",
            markup=True,
            font_size="18sp",
            halign="left",
            valign="middle",
            color=(0.15, 0.65, 0.60, 1)
        )
        lbl_title.bind(size=lbl_title.setter('text_size'))
        top_bar.add_widget(lbl_title)

        btn_add = Button(
            text="+ Événement",
            font_size="11sp",
            size_hint_x=None,
            width=96,
            background_color=(0.15, 0.65, 0.60, 1)
        )
        btn_add.bind(on_release=self._open_add_event)
        top_bar.add_widget(btn_add)
        root.add_widget(top_bar)

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
        today = today_str()
        agenda = self.cal_service.get_daily_agenda(today)

        self.content.add_widget(Label(
            text=f"[b]AGENDA DU JOUR — {format_date_fr(today)}[/b]",
            markup=True,
            font_size="13sp",
            size_hint_y=None,
            height=28,
            halign="left"
        ))

        events = agenda["events"]
        if not events:
            self.content.add_widget(Label(
                text="Aucun rendez-vous aujourd'hui.",
                font_size="12sp",
                size_hint_y=None,
                height=30,
                color=(0.5, 0.5, 0.5, 1)
            ))
        else:
            for ev in events:
                time_str = ev.start_datetime.split("T")[1][:5] if "T" in ev.start_datetime else ""
                row = BoxLayout(orientation="horizontal", size_hint_y=None, height=44, spacing=8)
                lbl = Label(
                    text=f"[b]{time_str}[/b]  {ev.title}",
                    markup=True,
                    font_size="13sp",
                    halign="left",
                    valign="middle"
                )
                lbl.bind(size=lbl.setter('text_size'))
                row.add_widget(lbl)
                self.content.add_widget(row)

        # Prochains événements à venir
        self.content.add_widget(Label(
            text="[b]PROCHAINS ÉVÉNEMENTS[/b]",
            markup=True,
            font_size="13sp",
            size_hint_y=None,
            height=32,
            halign="left"
        ))
        all_future = self.cal_service.get_events()
        future = [e for e in all_future if e.start_datetime >= today][:5]
        if not future:
            self.content.add_widget(Label(
                text="Aucun événement à venir.",
                font_size="12sp",
                size_hint_y=None,
                height=30,
                color=(0.5, 0.5, 0.5, 1)
            ))
        else:
            for ev in future:
                d_str = ev.start_datetime.split("T")[0]
                row = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=8)
                lbl = Label(
                    text=f"[color=26A69A]{d_str}[/color] • {ev.title}",
                    markup=True,
                    font_size="13sp",
                    halign="left",
                    valign="middle"
                )
                lbl.bind(size=lbl.setter('text_size'))
                row.add_widget(lbl)
                self.content.add_widget(row)

    def _open_add_event(self, *args):
        dialog = AddEventDialog(on_save_callback=self._handle_add_event)
        dialog.open()

    def _handle_add_event(self, title, start_dt, end_dt):
        self.cal_service.create_event(title=title, start_datetime=start_dt, end_datetime=end_dt)
        self.refresh()
