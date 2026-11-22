"""
LifeOS - Security Service
Sécurité, hachage PBKDF2/SHA-256 du code PIN et verrouillage
"""
import hashlib
import os
import secrets
from app.database.connection import db, DatabaseManager
from app.repositories.settings_repository import SettingsRepository
from app.core.exceptions import AuthenticationError


class SecurityService:
    def __init__(self, db_manager: DatabaseManager = db):
        self.db = db_manager
        self.settings_repo = SettingsRepository(db_manager)

    def is_pin_enabled(self) -> bool:
        val = self.settings_repo.get("pin_enabled", "0")
        return val == "1"

    def set_pin(self, pin_code: str):
        """Définit ou modifie le code PIN de l'utilisateur."""
        if not pin_code or len(pin_code) not in (4, 6) or not pin_code.isdigit():
            raise ValueError("Le code PIN doit comporter 4 ou 6 chiffres.")

        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            pin_code.encode("utf-8"),
            salt.encode("utf-8"),
            iterations=100000
        ).hex()

        stored_value = f"{salt}:{hashed}"
        self.settings_repo.set("pin_hash", stored_value)
        self.settings_repo.set("pin_enabled", "1")

    def disable_pin(self, current_pin: str) -> bool:
        """Désactive le code PIN après vérification."""
        if self.verify_pin(current_pin):
            self.settings_repo.set("pin_enabled", "0")
            self.settings_repo.set("pin_hash", "")
            return True
        return False

    def verify_pin(self, input_pin: str) -> bool:
        """Vérifie si le code PIN saisi correspond au hash stocké."""
        stored_value = self.settings_repo.get("pin_hash", "")
        if not stored_value or ":" not in stored_value:
            return True  # Aucun PIN configuré

        salt, expected_hash = stored_value.split(":", 1)
        test_hash = hashlib.pbkdf2_hmac(
            "sha256",
            input_pin.encode("utf-8"),
            salt.encode("utf-8"),
            iterations=100000
        ).hex()

        return secrets.compare_digest(expected_hash, test_hash)
