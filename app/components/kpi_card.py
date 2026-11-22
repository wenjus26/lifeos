"""
LifeOS - KPI & Metric Cards
Cartes Material modernes pour le tableau de bord et les résumés
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import ListProperty, NumericProperty


class MetricCard(BoxLayout):
    """Carte métrique arrondie élégante avec fond contrasté."""
    bg_color = ListProperty([0.13, 0.15, 0.19, 1.0])
    border_color = ListProperty([0.22, 0.25, 0.30, 0.8])
    corner_radius = NumericProperty(14)

    def __init__(self, title: str, value: str, subtitle: str = "",
                 accent_color: list = None, **kwargs):
        super().__init__(orientation="vertical", padding=14, spacing=4, **kwargs)
        self.accent_color = accent_color or [0.15, 0.65, 0.60, 1.0]

        self.bind(pos=self._update_canvas, size=self._update_canvas)

        # Titre
        self.lbl_title = Label(
            text=f"[color=888888]{title.upper()}[/color]",
            markup=True,
            font_size="11sp",
            bold=True,
            size_hint_y=None,
            height=16,
            halign="left",
            valign="middle"
        )
        self.lbl_title.bind(size=self.lbl_title.setter('text_size'))
        self.add_widget(self.lbl_title)

        # Valeur principale
        self.lbl_value = Label(
            text=f"[b]{value}[/b]",
            markup=True,
            font_size="18sp",
            size_hint_y=None,
            height=28,
            halign="left",
            valign="middle",
            color=self.accent_color
        )
        self.lbl_value.bind(size=self.lbl_value.setter('text_size'))
        self.add_widget(self.lbl_value)

        # Sous-titre
        if subtitle:
            self.lbl_sub = Label(
                text=subtitle,
                font_size="11sp",
                size_hint_y=None,
                height=16,
                halign="left",
                valign="middle",
                color=(0.6, 0.6, 0.6, 1)
            )
            self.lbl_sub.bind(size=self.lbl_sub.setter('text_size'))
            self.add_widget(self.lbl_sub)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.corner_radius])
            Color(*self.border_color)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.corner_radius), width=1.1)

    def update_values(self, value: str, subtitle: str = ""):
        self.lbl_value.text = f"[b]{value}[/b]"
        if hasattr(self, "lbl_sub") and subtitle:
            self.lbl_sub.text = subtitle
