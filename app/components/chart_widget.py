"""
LifeOS - Canvas Charts & Visual Indicators
Widgets graphiques haute performance dessinés sur le Canvas Kivy (60 FPS, zéro dépendance lourde)
"""
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class ProgressBarWidget(Widget):
    """Barre de progression arrondie moderne."""
    progress = NumericProperty(0)  # 0 à 100
    bar_color = ListProperty([0.15, 0.65, 0.60, 1.0])  # Turquoise / Teal
    bg_color = ListProperty([0.2, 0.2, 0.25, 0.5])
    corner_radius = NumericProperty(6)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._update_canvas, size=self._update_canvas, progress=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Fond
            Color(*self.bg_color)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.corner_radius]
            )
            # Progression
            fill_width = (self.width * min(100, max(0, self.progress))) / 100.0
            if fill_width > 0:
                Color(*self.bar_color)
                RoundedRectangle(
                    pos=self.pos,
                    size=(fill_width, self.height),
                    radius=[self.corner_radius]
                )


class CategoryBarWidget(BoxLayout):
    """Ligne représentant la part d'une catégorie avec couleur, nom et pourcentage."""

    def __init__(self, name: str, amount_str: str, percent: int, color_hex: str = "#42A5F5", **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, height=44, spacing=4, **kwargs)

        # En-tête (Nom + Montant + %)
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=20)
        lbl_name = Label(
            text=f"[b]{name}[/b]",
            markup=True,
            font_size="13sp",
            halign="left",
            valign="middle",
            size_hint_x=0.6,
            color=(0.9, 0.9, 0.9, 1)
        )
        lbl_name.bind(size=lbl_name.setter('text_size'))

        lbl_amt = Label(
            text=f"{amount_str} ({percent}%)",
            font_size="12sp",
            halign="right",
            valign="middle",
            size_hint_x=0.4,
            color=(0.7, 0.7, 0.7, 1)
        )
        lbl_amt.bind(size=lbl_amt.setter('text_size'))

        header.add_widget(lbl_name)
        header.add_widget(lbl_amt)
        self.add_widget(header)

        # Barre
        r, g, b = self._hex_to_rgb(color_hex)
        bar = ProgressBarWidget(
            progress=percent,
            bar_color=[r, g, b, 1.0],
            size_hint_y=None,
            height=8
        )
        self.add_widget(bar)

    def _hex_to_rgb(self, hex_code: str):
        hex_code = hex_code.lstrip("#")
        if len(hex_code) == 6:
            return tuple(int(hex_code[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        return (0.26, 0.65, 0.96)
