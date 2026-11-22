"""
LifeOS - Settings & More Screen
Paramètres, Sécurité PIN, Sauvegardes locales et Navigation vers les sous-modules
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from app.database.connection import db
from app.services.security_service import SecurityService
from app.services.backup_service import BackupService
from app.config.settings import settings
from app.components.dialogs import BaseModal


class SetPinDialog(BaseModal):
    def __init__(self, on_set_callback, **kwargs):
        super().__init__("Définir un Code PIN", **kwargs)
        self.on_set_callback = on_set_callback
        self.height = 220

        self.txt_pin = TextInput(
            hint_text="Code PIN (4 ou 6 chiffres)",
            password=True,
            input_filter="int",
            multiline=False,
            size_hint_y=None,
            height=44,
            background_color=(0.18, 0.20, 0.25, 1.0),
            foreground_color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.txt_pin)

        actions = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=44)
        btn_cancel = Button(text="Annuler", background_color=(0.4, 0.4, 0.4, 1))
        btn_cancel.bind(on_release=lambda x: self.dismiss())

        btn_save = Button(text="Enregistrer le PIN", background_color=(0.15, 0.65, 0.60, 1))
        btn_save.bind(on_release=self._save)

        actions.add_widget(btn_cancel)
        actions.add_widget(btn_save)
        self.container.add_widget(actions)

    def _save(self, *args):
        pin = self.txt_pin.text.strip()
        if len(pin) in (4, 6) and pin.isdigit():
            self.on_set_callback(pin)
            self.dismiss()


class SettingsScreen(Screen):
    def __init__(self, nav_callback, **kwargs):
        super().__init__(**kwargs)
        self.nav_callback = nav_callback
        self.sec_service = SecurityService(db)
        self.backup_service = BackupService(db)

        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)

        # En-tête
        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=56, padding=[16, 8, 16, 8])
        lbl_title = Label(
            text="[b]PARAMÈTRES & MODULES[/b]",
            markup=True,
            font_size="18sp",
            halign="left",
            valign="middle",
            color=(0.15, 0.65, 0.60, 1)
        )
        lbl_title.bind(size=lbl_title.setter('text_size'))
        top_bar.add_widget(lbl_title)
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

        # 1. Raccourcis vers autres modules (Objectifs, Calendrier, Notes)
        self.content.add_widget(Label(
            text="[b]AUTRES MODULES LIFEOS[/b]",
            markup=True,
            font_size="13sp",
            size_hint_y=None,
            height=26,
            halign="left"
        ))

        modules = [
            ("goals", "🎯 Objectifs de Vie (Milestones)", (0.2, 0.45, 0.65, 1)),
            ("calendar", "📅 Calendrier & Agenda Quotidien", (0.35, 0.45, 0.60, 1)),
            ("notes", "📝 Carnet de Notes & Recherche", (0.50, 0.35, 0.65, 1))
        ]

        for sid, label, color in modules:
            btn = Button(
                text=label,
                font_size="13sp",
                size_hint_y=None,
                height=46,
                background_color=color
            )
            btn.bind(on_release=lambda x, target=sid: self.nav_callback(target))
            self.content.add_widget(btn)

        # 2. Sécurité PIN
        self.content.add_widget(Label(
            text="[b]SÉCURITÉ & VERROUILLAGE[/b]",
            markup=True,
            font_size="13sp",
            size_hint_y=None,
            height=30,
            halign="left"
        ))

        is_pin = self.sec_service.is_pin_enabled()
        status_pin = "Activé" if is_pin else "Désactivé"

        lbl_pin = Label(
            text=f"Code PIN : [b]{status_pin}[/b]",
            markup=True,
            font_size="13sp",
            size_hint_y=None,
            height=26,
            halign="left"
        )
        lbl_pin.bind(size=lbl_pin.setter('text_size'))
        self.content.add_widget(lbl_pin)

        if not is_pin:
            btn_set_pin = Button(
                text="Activer un code PIN",
                font_size="13sp",
                size_hint_y=None,
                height=44,
                background_color=(0.15, 0.65, 0.60, 1)
            )
            btn_set_pin.bind(on_release=self._open_set_pin)
            self.content.add_widget(btn_set_pin)
        else:
            btn_dis_pin = Button(
                text="Désactiver le code PIN",
                font_size="13sp",
                size_hint_y=None,
                height=44,
                background_color=(0.5, 0.25, 0.25, 1)
            )
            btn_dis_pin.bind(on_release=self._disable_pin)
            self.content.add_widget(btn_dis_pin)

        # 3. Sauvegardes & Restauration
        self.content.add_widget(Label(
            text="[b]SAUVEGARDE & DONNÉES LOCALES[/b]",
            markup=True,
            font_size="13sp",
            size_hint_y=None,
            height=30,
            halign="left"
        ))

        btn_backup = Button(
            text="Créer une sauvegarde JSON locale",
            font_size="13sp",
            size_hint_y=None,
            height=44,
            background_color=(0.20, 0.50, 0.40, 1)
        )
        btn_backup.bind(on_release=self._create_backup)
        self.content.add_widget(btn_backup)

        self.lbl_backup_status = Label(
            text="",
            font_size="11sp",
            size_hint_y=None,
            height=20,
            color=(0.6, 0.8, 0.6, 1)
        )
        self.content.add_widget(self.lbl_backup_status)

        # 4. Informations App & Devise
        self.content.add_widget(Label(
            text=f"Devise principale : FCFA (XOF)\nLifeOS Mobile v{settings.version}\n100% Hors-ligne • Données chiffrées localement",
            font_size="11sp",
            size_hint_y=None,
            height=54,
            halign="center",
            color=(0.5, 0.5, 0.5, 1)
        ))

    def _open_set_pin(self, *args):
        dialog = SetPinDialog(on_set_callback=self._handle_set_pin)
        dialog.open()

    def _handle_set_pin(self, pin_code: str):
        self.sec_service.set_pin(pin_code)
        self.refresh()

    def _disable_pin(self, *args):
        # Pour simplifier l'ergonomie
        self.sec_service.settings_repo.set("pin_enabled", "0")
        self.sec_service.settings_repo.set("pin_hash", "")
        self.refresh()

    def _create_backup(self, *args):
        path = self.backup_service.create_json_backup()
        self.lbl_backup_status.text = f"Sauvegarde créée : {path.split('/')[-1].split(chr(92))[-1]}"
