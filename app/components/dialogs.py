"""
LifeOS - Action Dialogs & Input Modals
Formulaires intuitifs mobiles pour l'enregistrement rapide des données
"""
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, RoundedRectangle, Line
from app.utils.currency import parse_currency_input
from app.core.constants import (
    TX_EXPENSE, TX_INCOME, TX_TRANSFER,
    PRIORITY_MEDIUM, TASK_PRIORITIES,
    FREQ_DAILY, GOAL_CATEGORIES
)
from app.utils.android_native import android_bridge


class BaseModal(ModalView):
    """Boîte modale Material Design stylisée."""
    def __init__(self, title_text: str, **kwargs):
        super().__init__(
            size_hint=(0.92, None),
            auto_dismiss=True,
            background_color=(0, 0, 0, 0.7),
            **kwargs
        )
        self.container = BoxLayout(
            orientation="vertical",
            padding=18,
            spacing=12,
            size_hint_y=None
        )
        self.container.bind(minimum_height=self.container.setter('height'))
        self.container.bind(pos=self._update_bg, size=self._update_bg)

        # En-tête
        lbl_title = Label(
            text=f"[b]{title_text}[/b]",
            markup=True,
            font_size="17sp",
            size_hint_y=None,
            height=26,
            color=(0.15, 0.65, 0.60, 1)
        )
        self.container.add_widget(lbl_title)
        self.add_widget(self.container)

    def _update_bg(self, *args):
        self.container.canvas.before.clear()
        with self.container.canvas.before:
            Color(0.14, 0.16, 0.20, 1.0)
            RoundedRectangle(pos=self.container.pos, size=self.container.size, radius=[18])
            Color(0.24, 0.28, 0.35, 1.0)
            Line(rounded_rectangle=(self.container.x, self.container.y, self.container.width, self.container.height, 18), width=1.2)


class AddTransactionDialog(BaseModal):
    """Modale pour ajouter une dépense ou un revenu rapidement."""
    def __init__(self, wallets, categories, on_save_callback, **kwargs):
        super().__init__("Nouvelle Transaction", **kwargs)
        self.wallets = wallets
        self.categories = categories
        self.on_save_callback = on_save_callback
        self.height = 380

        # Type (Dépense / Revenu)
        self.spinner_type = Spinner(
            text="Dépense",
            values=("Dépense", "Revenu"),
            size_hint_y=None,
            height=40,
            background_color=(0.20, 0.23, 0.29, 1.0),
            color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.spinner_type)

        # Montant
        self.txt_amount = TextInput(
            hint_text="Montant en FCFA (ex: 5000)",
            input_filter="int",
            multiline=False,
            size_hint_y=None,
            height=44,
            background_color=(0.18, 0.20, 0.25, 1.0),
            foreground_color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.txt_amount)

        # Portefeuille
        w_names = [w.name for w in wallets] if wallets else ["Portefeuille Principal"]
        self.spinner_wallet = Spinner(
            text=w_names[0],
            values=w_names,
            size_hint_y=None,
            height=40,
            background_color=(0.20, 0.23, 0.29, 1.0),
            color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.spinner_wallet)

        # Catégorie
        cat_names = [c.name for c in categories] if categories else ["Alimentation"]
        self.spinner_cat = Spinner(
            text=cat_names[0],
            values=cat_names,
            size_hint_y=None,
            height=40,
            background_color=(0.20, 0.23, 0.29, 1.0),
            color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.spinner_cat)

        # Note / Description
        self.txt_note = TextInput(
            hint_text="Description / Note (facultatif)",
            multiline=False,
            size_hint_y=None,
            height=40,
            background_color=(0.18, 0.20, 0.25, 1.0),
            foreground_color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.txt_note)

        # Boutons Enregistrer / Annuler
        actions = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=44)
        btn_cancel = Button(text="Annuler", background_color=(0.4, 0.4, 0.4, 1))
        btn_cancel.bind(on_release=lambda x: self.dismiss())

        btn_save = Button(text="Enregistrer", background_color=(0.15, 0.65, 0.60, 1))
        btn_save.bind(on_release=self._save)

        actions.add_widget(btn_cancel)
        actions.add_widget(btn_save)
        self.container.add_widget(actions)

    def _save(self, *args):
        amount = parse_currency_input(self.txt_amount.text)
        if amount <= 0:
            return

        tx_type = TX_EXPENSE if self.spinner_type.text == "Dépense" else TX_INCOME
        wallet = next((w for w in self.wallets if w.name == self.spinner_wallet.text), self.wallets[0] if self.wallets else None)
        category = next((c for c in self.categories if c.name == self.spinner_cat.text), None)

        if wallet:
            self.on_save_callback(
                tx_type=tx_type,
                wallet_id=wallet.id,
                category_id=category.id if category else None,
                amount_cents=amount,
                note=self.txt_note.text.strip()
            )
            self.dismiss()


class AddTaskDialog(BaseModal):
    """Modale pour ajouter une tâche avec priorité."""
    def __init__(self, on_save_callback, **kwargs):
        super().__init__("Nouvelle Tâche", **kwargs)
        self.on_save_callback = on_save_callback
        self.height = 320

        self.txt_title = TextInput(
            hint_text="Titre de la tâche (ex: Payer facture électricité)",
            multiline=False,
            size_hint_y=None,
            height=44,
            background_color=(0.18, 0.20, 0.25, 1.0),
            foreground_color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.txt_title)

        self.spinner_priority = Spinner(
            text="Priorité Moyenne",
            values=("Priorité Basse", "Priorité Moyenne", "Priorité Haute", "Urgent !"),
            size_hint_y=None,
            height=40,
            background_color=(0.20, 0.23, 0.29, 1.0),
            color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.spinner_priority)

        self.txt_due = TextInput(
            hint_text="Date limite (YYYY-MM-DD, ex: aujourd'hui)",
            multiline=False,
            size_hint_y=None,
            height=40,
            background_color=(0.18, 0.20, 0.25, 1.0),
            foreground_color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.txt_due)

        actions = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=44)
        btn_cancel = Button(text="Annuler", background_color=(0.4, 0.4, 0.4, 1))
        btn_cancel.bind(on_release=lambda x: self.dismiss())

        btn_save = Button(text="Créer la tâche", background_color=(0.15, 0.65, 0.60, 1))
        btn_save.bind(on_release=self._save)

        actions.add_widget(btn_cancel)
        actions.add_widget(btn_save)
        self.container.add_widget(actions)

    def _save(self, *args):
        title = self.txt_title.text.strip()
        if not title:
            return

        p_map = {
            "Priorité Basse": "low",
            "Priorité Moyenne": "medium",
            "Priorité Haute": "high",
            "Urgent !": "urgent"
        }
        priority = p_map.get(self.spinner_priority.text, "medium")
        due = self.txt_due.text.strip() or None

        self.on_save_callback(title=title, priority=priority, due_date=due)
        self.dismiss()


class AddHabitDialog(BaseModal):
    """Modale pour ajouter une habitude quotidienne."""
    def __init__(self, on_save_callback, **kwargs):
        super().__init__("Nouvelle Habitude", **kwargs)
        self.on_save_callback = on_save_callback
        self.height = 260

        self.txt_title = TextInput(
            hint_text="Nom de l'habitude (ex: Boire 2L d'eau)",
            multiline=False,
            size_hint_y=None,
            height=44,
            background_color=(0.18, 0.20, 0.25, 1.0),
            foreground_color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.txt_title)

        self.spinner_freq = Spinner(
            text="Tous les jours",
            values=("Tous les jours", "En semaine (Lun-Ven)", "Le week-end"),
            size_hint_y=None,
            height=40,
            background_color=(0.20, 0.23, 0.29, 1.0),
            color=(1, 1, 1, 1)
        )
        self.container.add_widget(self.spinner_freq)

        actions = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=44)
        btn_cancel = Button(text="Annuler", background_color=(0.4, 0.4, 0.4, 1))
        btn_cancel.bind(on_release=lambda x: self.dismiss())

        btn_save = Button(text="Créer l'habitude", background_color=(0.15, 0.65, 0.60, 1))
        btn_save.bind(on_release=self._save)

        actions.add_widget(btn_cancel)
        actions.add_widget(btn_save)
        self.container.add_widget(actions)

    def _save(self, *args):
        title = self.txt_title.text.strip()
        if not title:
            return
        self.on_save_callback(title=title, frequency="daily")
        self.dismiss()
