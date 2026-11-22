"""
LifeOS - Android Native Integration
Couche d'abstraction PyJNIus pour les fonctionnalités natives Android :
- Notifications locales
- Vibration / Retour haptique
- Chemins de stockage Xiaomi / Android
- Cycle de vie et informations batterie
"""
import os
import sys
import logging

logger = logging.getLogger("LifeOS.Android")


def is_android() -> bool:
    """Détecte si l'application s'exécute sur le système Android."""
    return "ANDROID_STORAGE" in os.environ or hasattr(sys, "getandroidapilevel")


class AndroidNativeBridge:
    """Pont de communication avec l'API Android via PyJNIus."""

    def __init__(self):
        self._is_android = is_android()
        self._context = None
        self._vibrator = None
        self._notification_manager = None
        self._init_pyjnius()

    def _init_pyjnius(self):
        if not self._is_android:
            logger.info("LifeOS s'exécute hors Android (Mode Bureau/Test).")
            return

        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            self._context = PythonActivity.mActivity
            Context = autoclass("android.content.Context")
            self._vibrator = self._context.getSystemService(Context.VIBRATOR_SERVICE)
            self._notification_manager = self._context.getSystemService(Context.NOTIFICATION_SERVICE)
            logger.info("PyJNIus initialisé avec succès sur Android.")
        except Exception as e:
            logger.warning(f"Échec de l'initialisation de PyJNIus : {e}")

    def vibrate(self, milliseconds: int = 50):
        """Déclenche une légère vibration haptique."""
        if not self._is_android or not self._vibrator:
            logger.debug(f"[Simulé] Vibration {milliseconds}ms")
            return
        try:
            from jnius import autoclass
            Build = autoclass("android.os.Build")
            if Build.VERSION.SDK_INT >= 26:
                VibrationEffect = autoclass("android.os.VibrationEffect")
                effect = VibrationEffect.createOneShot(milliseconds, VibrationEffect.DEFAULT_AMPLITUDE)
                self._vibrator.vibrate(effect)
            else:
                self._vibrator.vibrate(milliseconds)
        except Exception as e:
            logger.error(f"Erreur lors de la vibration : {e}")

    def send_notification(self, title: str, message: str, notification_id: int = 1):
        """Envoie une notification locale sur Android."""
        if not self._is_android or not self._context:
            logger.info(f"[Notification Simulée] {title}: {message}")
            return
        try:
            from jnius import autoclass
            Build = autoclass("android.os.Build")
            NotificationManager = autoclass("android.app.NotificationManager")
            NotificationCompat = autoclass("androidx.core.app.NotificationCompat$Builder")
            channel_id = "lifeos_main_channel"

            if Build.VERSION.SDK_INT >= 26:
                NotificationChannel = autoclass("android.app.NotificationChannel")
                channel = NotificationChannel(
                    channel_id,
                    "LifeOS Notifications",
                    NotificationManager.IMPORTANCE_DEFAULT
                )
                channel.setDescription("Notifications et rappels LifeOS")
                self._notification_manager.createNotificationChannel(channel)

            builder = NotificationCompat(self._context, channel_id)
            builder.setContentTitle(title)
            builder.setContentText(message)
            builder.setSmallIcon(self._context.getApplicationInfo().icon)
            builder.setAutoCancel(True)

            self._notification_manager.notify(notification_id, builder.build())
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de notification Android : {e}")

    def get_app_storage_dir(self) -> str:
        """Retourne le répertoire de stockage persistant de l'application."""
        if self._is_android and self._context:
            try:
                files_dir = self._context.getFilesDir().getAbsolutePath()
                return files_dir
            except Exception as e:
                logger.warning(f"Impossible de lire getFilesDir : {e}")

        # Fallback pour environnement bureau / tests
        base_dir = os.path.expanduser(os.path.join("~", ".lifeos"))
        os.makedirs(base_dir, exist_ok=True)
        return base_dir


# Instance singleton
android_bridge = AndroidNativeBridge()
