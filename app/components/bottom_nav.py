"""
LifeOS - Bottom Navigation Component
Barre de navigation inférieure ergonomique pour Android
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Line
from kivy.properties import StringProperty, ObjectProperty
from app.utils.android_native import android_bridge


class NavButton(Button):
    def __init__(self, screen_id: str, label_text: str, icon_symbol: str, on_select_cb, **kwargs):
        super().__init__(**kwargs)
        self.screen_id = screen_id
        self.label_text = label_text
        self.icon_symbol = icon_symbol
        self.on_select_cb = on_select_cb
        self.is_active = False

        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        self.markup = True
        self._update_text()

    def set_active(self, active: bool):
        self.is_active = active
        self._update_text()

    def _update_text(self):
        color = "26A69A" if self.is_active else "888888"
        self.text = f"[color={color}][size=17sp]{self.icon_symbol}[/size]\n[size=10sp]{self.label_text}[/size][/color]"

    def on_press(self):
        android_bridge.vibrate(20)
        if self.on_select_cb:
            self.on_select_cb(self.screen_id)


class BottomNavBar(BoxLayout):
    """Barre inférieure de 5 onglets fixes pour la navigation mobile Android."""

    def __init__(self, on_navigate_callback, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=60,
            spacing=0,
            padding=[4, 2, 4, 2],
            **kwargs
        )
        self.on_navigate_callback = on_navigate_callback
        self.buttons = {}

        self.bind(pos=self._update_bg, size=self._update_bg)

        # Onglets
        tabs = [
            ("dashboard", "Accueil", "☵"),
            ("finance", "Finances", "◈"),
            ("tasks", "Tâches", "✓"),
            ("habits", "Habitudes", "★"),
            ("menu", "Plus", "≡")
        ]

        for screen_id, label, icon in tabs:
            btn = NavButton(screen_id, label, icon, self._handle_tab_press)
            self.buttons[screen_id] = btn
            self.add_widget(btn)

        self.set_active("dashboard")

    def _handle_tab_press(self, screen_id: str):
        self.set_active(screen_id)
        if self.on_navigate_callback:
            self.on_navigate_callback(screen_id)

    def set_active(self, active_screen_id: str):
        for sid, btn in self.buttons.items():
            btn.set_active(sid == active_screen_id)

    def _update_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.10, 0.11, 0.14, 1.0)
            Rectangle(pos=self.pos, size=self.size)
            # Ligne fine séparatrice supérieure
            Color(0.20, 0.22, 0.27, 0.8)
            Line(points=[self.x, self.y + self.height, self.x + self.width, self.y + self.height], width=1)
