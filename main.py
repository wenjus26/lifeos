"""
LifeOS - Application Mobile Android Native
Point d'entrée principal de l'application
"""
import os
import sys

# Ajustement de la taille de fenêtre pour l'émulation mobile sur bureau (Format smartphone Xiaomi Redmi)
from kivy.config import Config
Config.set('graphics', 'width', '390')
Config.set('graphics', 'height', '844')
Config.set('graphics', 'resizable', '1')

from kivy.app import App
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

from app.database.connection import db
from app.config.settings import settings
from app.navigation.app_navigator import AppRootView
from app.utils.android_native import is_android


class LifeOSApp(App):
    """Classe principale de l'application LifeOS."""

    def build(self):
        self.title = settings.app_name
        self.icon = "assets/icons/icon.png"

        # Fond sombre moderne Material (Dark Theme par défaut)
        Window.clearcolor = get_color_from_hex("#121418")

        # Initialisation garantie de la base de données SQLite locale
        db.initialize_database()

        # Construction de la vue racine et du contrôleur de navigation
        self.root_view = AppRootView()
        return self.root_view

    def on_pause(self):
        """Cycle de vie Android : mise en pause (sauvegarde de l'état)."""
        return True

    def on_resume(self):
        """Cycle de vie Android : reprise au premier plan."""
        pass


if __name__ == "__main__":
    LifeOSApp().run()
