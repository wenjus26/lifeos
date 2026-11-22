"""
LifeOS - Notes Screen
Gestionnaire de notes personnelles et professionnelles avec recherche et favoris
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from app.database.connection import db
from app.services.note_service import NoteService
from app.components.dialogs import BaseModal


class AddNoteDialog(BaseModal):
    def __init__(self, on_save_callback, **kwargs):
        super().__init__("Nouvelle Note", **kwargs)
        self.on_save_callback = on_save_callback
        self.height = 340

        self.txt_title = TextInput(
            hint_text="Titre de la note",
            multiline=False,
            size_hint_y=None,
            height=44,
            background_color=(0.18, 0.20, 0.25, 1.0),
            foreground_color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.txt_title)

        self.txt_cat = TextInput(
            hint_text="Catégorie (ex: Travail, Idées, Personnel)",
            multiline=False,
            size_hint_y=None,
            height=40,
            background_color=(0.18, 0.20, 0.25, 1.0),
            foreground_color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.txt_cat)

        self.txt_content = TextInput(
            hint_text="Contenu de la note...",
            multiline=True,
            size_hint_y=None,
            height=90,
            background_color=(0.18, 0.20, 0.25, 1.0),
            foreground_color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.txt_content)

        actions = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=44)
        btn_cancel = Button(text="Annuler", background_color=(0.4, 0.4, 0.4, 1))
        btn_cancel.bind(on_release=lambda x: self.dismiss())

        btn_save = Button(text="Enregistrer", background_color=(0.15, 0.65, 0.60, 1))
        btn_save.bind(on_release=self._save)

        actions.add_widget(btn_cancel)
        actions.add_widget(btn_save)
        self.container.add_widget(actions)

    def _save(self, *args):
        title = self.txt_title.text.strip()
        cat = self.txt_cat.text.strip() or "Général"
        content = self.txt_content.text.strip()
        if not title:
            return
        self.on_save_callback(title=title, content=content, category=cat)
        self.dismiss()


class NotesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.note_service = NoteService(db)
        self.search_query = ""

        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)

        # En-tête
        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=56, padding=[16, 8, 16, 8])
        lbl_title = Label(
            text="[b]CARNET DE NOTES[/b]",
            markup=True,
            font_size="18sp",
            halign="left",
            valign="middle",
            color=(0.15, 0.65, 0.60, 1)
        )
        lbl_title.bind(size=lbl_title.setter('text_size'))
        top_bar.add_widget(lbl_title)

        btn_add = Button(
            text="+ Note",
            font_size="12sp",
            size_hint_x=None,
            width=80,
            background_color=(0.15, 0.65, 0.60, 1)
        )
        btn_add.bind(on_release=self._open_add_note)
        top_bar.add_widget(btn_add)
        root.add_widget(top_bar)

        # Barre de recherche
        search_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=44, padding=[16, 0, 16, 4])
        self.txt_search = TextInput(
            hint_text="Rechercher une note...",
            multiline=False,
            background_color=(0.18, 0.20, 0.25, 1.0),
            foreground_color=(1, 1, 1, 1)
        )
        self.txt_search.bind(text=self._on_search_text)
        search_box.add_widget(self.txt_search)
        root.add_widget(search_box)

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

    def _on_search_text(self, instance, text):
        self.search_query = text.strip()
        self.refresh()

    def refresh(self):
        self.content.clear_widgets()
        notes = self.note_service.get_notes(search_query=self.search_query if self.search_query else None)

        if not notes:
            self.content.add_widget(Label(
                text="Aucune note trouvée.",
                font_size="13sp",
                size_hint_y=None,
                height=40,
                color=(0.5, 0.5, 0.5, 1)
            ))
            return

        for note in notes:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=60, spacing=8)

            btn_pin = Button(
                text="★" if note.is_pinned else "☆",
                size_hint_x=None,
                width=36,
                background_color=(0.95, 0.70, 0.20, 1) if note.is_pinned else (0.3, 0.3, 0.3, 1)
            )
            btn_pin.bind(on_release=lambda x, nid=note.id: self._toggle_pin(nid))

            content_snippet = (note.content[:40] + "...") if len(note.content) > 40 else note.content
            lbl_info = Label(
                text=f"[b]{note.title}[/b]  [size=11sp][color=26A69A]{note.category}[/color][/size]\n[size=12sp]{content_snippet}[/size]",
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
            btn_del.bind(on_release=lambda x, nid=note.id: self._delete_note(nid))

            row.add_widget(btn_pin)
            row.add_widget(lbl_info)
            row.add_widget(btn_del)
            self.content.add_widget(row)

    def _open_add_note(self, *args):
        dialog = AddNoteDialog(on_save_callback=self._handle_add_note)
        dialog.open()

    def _handle_add_note(self, title, content, category):
        self.note_service.create_note(title=title, content=content, category=category)
        self.refresh()

    def _toggle_pin(self, note_id: int):
        self.note_service.toggle_pin(note_id)
        self.refresh()

    def _delete_note(self, note_id: int):
        self.note_service.delete_note(note_id)
        self.refresh()
