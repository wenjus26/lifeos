"""
LifeOS - Application Settings
Configuration centralisée de l'application
"""
import os
from dataclasses import dataclass
from app.utils.android_native import android_bridge
from app.core.constants import DEFAULT_CURRENCY, THEME_DARK


@dataclass
class AppSettings:
    """Paramètres d'exécution de LifeOS."""
    app_name: str = "LifeOS"
    version: str = "1.0.0"
    db_filename: str = "lifeos_data.db"
    default_currency: str = DEFAULT_CURRENCY
    theme_style: str = THEME_DARK
    pin_enabled: bool = False
    pin_hash: str = ""
    biometrics_enabled: bool = False
    auto_backup: bool = True
    daily_reminder_time: str = "08:00"

    @property
    def storage_directory(self) -> str:
        """Chemin vers le répertoire des données locales."""
        return android_bridge.get_app_storage_dir()

    @property
    def database_path(self) -> str:
        """Chemin absolu vers le fichier de base de données SQLite."""
        return os.path.join(self.storage_directory, self.db_filename)

    @property
    def backups_directory(self) -> str:
        """Chemin vers les sauvegardes locales."""
        backups_dir = os.path.join(self.storage_directory, "backups")
        os.makedirs(backups_dir, exist_ok=True)
        return backups_dir

    @property
    def exports_directory(self) -> str:
        """Chemin vers les exports CSV/rapports."""
        exports_dir = os.path.join(self.storage_directory, "exports")
        os.makedirs(exports_dir, exist_ok=True)
        return exports_dir


settings = AppSettings()
