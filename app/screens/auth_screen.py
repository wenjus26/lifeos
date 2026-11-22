"""
LifeOS - PIN Authentication Screen
Écran de déverrouillage sécurisé par code PIN à l'ouverture de l'application
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from app.database.connection import db
from app.services.security_service import SecurityService
from app.utils.android_native import android_bridge


class AuthScreen(Screen):
    def __init__(self, on_unlock_success, **kwargs):
        super().__init__(**kwargs)
        self.on_unlock_success = on_unlock_success
        self.sec_service = SecurityService(db)
        self.entered_pin = ""

        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", padding=[24, 40, 24, 20], spacing=20)

        # En-tête
        lbl_app = Label(
            text="[b]LIFE[color=26A69A]OS[/color][/b]",
            markup=True,
            font_size="28sp",
            size_hint_y=None,
            height=40
        )
        root.add_widget(lbl_app)

        lbl_instruct = Label(
            text="Entrez votre code PIN pour déverrouiller",
            font_size="13sp",
            size_hint_y=None,
            height=20,
            color=(0.7, 0.7, 0.7, 1)
        )
        root.add_widget(lbl_instruct)

        # Affichage des points du PIN
        self.lbl_dots = Label(
            text="○ ○ ○ ○",
            font_size="28sp",
            size_hint_y=None,
            height=50,
            color=(0.15, 0.65, 0.60, 1)
        )
        root.add_widget(self.lbl_dots)

        self.lbl_error = Label(
            text="",
            font_size="12sp",
            size_hint_y=None,
            height=20,
            color=(0.9, 0.3, 0.3, 1)
        )
        root.add_widget(self.lbl_error)

        # Pavé numérique
        keypad = GridLayout(cols=3, spacing=14, size_hint=(1, None), height=280)
        digits = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "C", "0", "⌫"]

        for d in digits:
            btn = Button(
                text=d,
                font_size="20sp",
                background_color=(0.18, 0.20, 0.25, 1.0)
            )
            btn.bind(on_release=lambda x, val=d: self._handle_key(val))
            keypad.add_widget(btn)

        root.add_widget(keypad)
        self.add_widget(root)

    def on_enter(self, *args):
        self.entered_pin = ""
        self._update_dots()
        self.lbl_error.text = ""

    def _handle_key(self, val: str):
        android_bridge.vibrate(20)
        if val == "C":
            self.entered_pin = ""
        elif val == "⌫":
            self.entered_pin = self.entered_pin[:-1]
        elif len(self.entered_pin) < 6:
            self.entered_pin += val

        self._update_dots()

        # Si le PIN atteint 4 chiffres, tester
        if len(self.entered_pin) >= 4:
            if self.sec_service.verify_pin(self.entered_pin):
                android_bridge.vibrate(40)
                self.on_unlock_success()
            elif len(self.entered_pin) == 6 or len(self.entered_pin) == 4:
                # Si 4 chiffres échouent et qu'on ne continue pas vers 6
                if len(self.entered_pin) == 4 and not self.sec_service.verify_pin(self.entered_pin):
                    self.lbl_error.text = "Code PIN incorrect"
                    android_bridge.vibrate(100)

    def _update_dots(self):
        count = len(self.entered_pin)
        dots = ["●" if i < count else "○" for i in range(max(4, count))]
        self.lbl_dots.text = " ".join(dots)
