"""
LifeOS - App Navigator & Lifecycle Management
Contrôleur de navigation central, ScreenManager et gestion du bouton Retour Android
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window

from app.database.connection import db
from app.services.security_service import SecurityService
from app.components.bottom_nav import BottomNavBar
from app.screens.dashboard.dashboard_screen import DashboardScreen
from app.screens.finance.finance_screen import FinanceScreen
from app.screens.tasks.tasks_screen import TasksScreen
from app.screens.habits.habits_screen import HabitsScreen
from app.screens.goals.goals_screen import GoalsScreen
from app.screens.calendar.calendar_screen import CalendarScreen
from app.screens.notes.notes_screen import NotesScreen
from app.screens.settings.settings_screen import SettingsScreen
from app.screens.auth_screen import AuthScreen


class AppRootView(BoxLayout):
    """Vue racine contenant le gestionnaire d'écrans et la barre de navigation inférieure."""

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.sec_service = SecurityService(db)

        # Gestionnaire d'écrans
        self.sm = ScreenManager(transition=SlideTransition(duration=0.2))

        # Écrans principaux
        self.dashboard_screen = DashboardScreen(name="dashboard")
        self.finance_screen = FinanceScreen(name="finance")
        self.tasks_screen = TasksScreen(name="tasks")
        self.habits_screen = HabitsScreen(name="habits")
        self.goals_screen = GoalsScreen(name="goals")
        self.calendar_screen = CalendarScreen(name="calendar")
        self.notes_screen = NotesScreen(name="notes")
        self.settings_screen = SettingsScreen(nav_callback=self.navigate_to, name="menu")

        self.sm.add_widget(self.dashboard_screen)
        self.sm.add_widget(self.finance_screen)
        self.sm.add_widget(self.tasks_screen)
        self.sm.add_widget(self.habits_screen)
        self.sm.add_widget(self.goals_screen)
        self.sm.add_widget(self.calendar_screen)
        self.sm.add_widget(self.notes_screen)
        self.sm.add_widget(self.settings_screen)

        # Écran de verrouillage PIN
        self.auth_screen = AuthScreen(on_unlock_success=self._on_pin_unlocked, name="auth")
        self.sm.add_widget(self.auth_screen)

        # Barre de navigation inférieure
        self.bottom_nav = BottomNavBar(on_navigate_callback=self.navigate_to)

        self.add_widget(self.sm)
        self.add_widget(self.bottom_nav)

        # Historique pour le bouton Retour physique Android
        self.screen_history = []

        # Écoute de la touche retour Android (code 27 = Escape / Back)
        Window.bind(on_keyboard=self._on_key_down)

        # Démarrage : vérifier si le PIN est actif
        if self.sec_service.is_pin_enabled():
            self.bottom_nav.height = 0
            self.bottom_nav.opacity = 0
            self.sm.current = "auth"
        else:
            self.sm.current = "dashboard"

    def navigate_to(self, screen_id: str):
        if self.sm.current != screen_id:
            self.screen_history.append(self.sm.current)
            self.sm.current = screen_id
            self.bottom_nav.set_active(screen_id)

    def _on_pin_unlocked(self):
        """Déclenché lorsque le PIN est validé avec succès."""
        self.bottom_nav.height = 60
        self.bottom_nav.opacity = 1.0
        self.sm.current = "dashboard"
        self.bottom_nav.set_active("dashboard")

    def _on_key_down(self, window, key, scancode, codepoint, modifier):
        """Gestionnaire pour la touche physique Android Back (touche 27)."""
        if key == 27:  # Android Back
            if self.sm.current == "auth":
                return False  # Empêcher de contourner l'écran PIN
            if self.screen_history:
                prev_screen = self.screen_history.pop()
                self.sm.current = prev_screen
                self.bottom_nav.set_active(prev_screen)
                return True
        return False
