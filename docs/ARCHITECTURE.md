# ARCHITECTURE TECHNIQUE — LIFEOS

## 1. PRINCIPES DE CONCEPTION

LifeOS est conçu selon les principes de l'ingénierie logicielle moderne pour applications mobiles :
- **Clean Architecture & Separation of Concerns** : Séparation stricte entre les modèles, la persistance, la logique métier et l'interface utilisateur.
- **Repository Pattern** : Abstraction de la persistance SQLite permettant des requêtes paramétrées sécurisées et optimisées.
- **Offline-First & Local Sovereignty** : 100% des données sont traitées et stockées localement en SQLite avec mode WAL (Write-Ahead Logging). Aucune dépendance réseau.
- **Intégrité Monétaire** : Tous les montants financiers sont stockés en entiers exacts (`amount_cents`), éliminant tout risque d'arrondi ou de dérive binaire propre aux nombres flottants.

---

## 2. STRUCTURE DU PROJET

```
life/
├── main.py                     # Point d'entrée de l'application Kivy
├── requirements.txt            # Dépendances validées
├── buildozer.spec              # Configuration de packaging Android
├── build_apk_wsl.sh            # Script de compilation automatisé Ubuntu/WSL2
├── install_apk_adb.bat         # Script de déploiement USB ADB vers Xiaomi
│
├── app/
│   ├── core/
│   │   ├── constants.py        # Constantes (devises, priorités, statuts)
│   │   └── exceptions.py       # Exceptions métier hiérarchisées
│   ├── config/
│   │   └── settings.py         # Configuration centralisée & chemins
│   ├── database/
│   │   └── connection.py       # Connexion SQLite WAL & schéma DDL
│   ├── models/                 # Modèles de données (Dataclasses)
│   │   ├── wallet.py
│   │   ├── category.py
│   │   ├── transaction.py
│   │   ├── budget.py
│   │   ├── debt.py
│   │   ├── savings_goal.py
│   │   ├── task.py
│   │   ├── habit.py
│   │   ├── goal.py
│   │   ├── calendar_event.py
│   │   └── note.py
│   ├── repositories/           # Couche d'accès aux données (SQL)
│   ├── services/               # Couche logique métier
│   │   ├── finance_service.py
│   │   ├── task_service.py
│   │   ├── habit_service.py
│   │   ├── goal_service.py
│   │   ├── calendar_service.py
│   │   ├── note_service.py
│   │   ├── dashboard_service.py
│   │   ├── security_service.py
│   │   ├── export_service.py
│   │   └── backup_service.py
│   ├── components/             # Composants d'interface réutilisables
│   │   ├── kpi_card.py
│   │   ├── chart_widget.py
│   │   ├── bottom_nav.py
│   │   └── dialogs.py
│   ├── screens/                # Écrans de l'application
│   │   ├── dashboard/
│   │   ├── finance/
│   │   ├── tasks/
│   │   ├── habits/
│   │   ├── goals/
│   │   ├── calendar/
│   │   ├── notes/
│   │   ├── settings/
│   │   └── auth_screen.py
│   ├── navigation/
│   │   └── app_navigator.py    # Contrôleur ScreenManager & bouton Retour
│   └── utils/
│       ├── currency.py         # Formatage & calculs sans float
│       ├── date_utils.py       # Séries (streaks) & dates en français
│       └── android_native.py   # Pont PyJNIus Android natif
│
├── assets/
│   ├── icons/                  # Icônes de l'application
│   └── images/                 # Écran de démarrage (splash)
├── tests/                      # Tests automatisés pytest (24 tests validés)
├── docs/                       # Documentation technique et utilisateur
└── release/                    # Destination de l'APK compilé
```

---

## 3. COUCHE D'INTÉGRATION ANDROID (PYJNIUS)

Le module `app/utils/android_native.py` encapsule les appels Java natifs via `jnius.autoclass` :
1. **Notifications locales** : `android.app.NotificationManager` et `androidx.core.app.NotificationCompat`.
2. **Retour haptique** : `android.os.Vibrator` et `android.os.VibrationEffect`.
3. **Répertoire de stockage** : `context.getFilesDir().getAbsolutePath()`.
4. **Cycle de vie** : Gestion des événements `on_pause` et `on_resume` dans la classe principale Kivy.
