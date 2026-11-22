# LIFEOS — APPLICATION MOBILE ANDROID NATIVE

**LifeOS** est un système d'exploitation personnel mobile complet développé avec **Python 3**, **Kivy** et **KivyMD**, fonctionnant **100% hors-ligne** et conçu pour les smartphones **Xiaomi Redmi (MIUI / HyperOS)**.

---

## 🚀 FONCTIONNALITÉS PRINCIPALES

- 📊 **Tableau de Bord Dynamique** : Solde global disponible, revenus & dépenses mensuels, jauge budgétaire, tâches du jour, routines d'habitudes et score de productivité.
- 💳 **Gestion Financière Complète** :
  - Devise par défaut : **Franc CFA (XOF / FCFA)**, montants stockés sans float.
  - Multi-portefeuilles (Espèces, Wave Mobile Money, Compte Bancaire, Orange Money).
  - Gestion des budgets mensuels avec alertes de dépassement (80%, 100%).
  - Suivi des dettes et créances avec remboursements partiels.
  - Objectifs d'épargne avec suivi de progression.
  - Exportation CSV instantanée sans connexion Internet.
- 📋 **Gestion des Tâches** : Priorités (Basse, Moyenne, Haute, Urgent), sous-tâches (checklist), récurrences automatiques.
- ★ **Suivi des Habitudes (Habits Tracker)** : Check-in quotidien, calcul de séries consécutives (*streaks*), matrice d'accomplissement sur 30 jours.
- 🎯 **Objectifs de Vie** : Objectifs personnels, professionnels et financiers avec calcul automatique du pourcentage d'avancement selon les jalons complétés.
- 📅 **Calendrier & Agenda** : Planification de rendez-vous et vue quotidienne unifiée.
- 📝 **Carnet de Notes** : Recherche en temps réel, favoris/épingles, catégorisation.
- 🔒 **Sécurité & Données** : Verrouillage par code PIN (hachage PBKDF2/SHA-256 avec sel), sauvegardes locales JSON et SQLite.

---

## 🛠️ STACK TECHNIQUE

- **Langage** : Python 3.10+
- **Framework UI** : Kivy 2.3.2 / KivyMD 2.0.0 (Material Design mobile)
- **Base de données** : SQLite 3 (Mode WAL, Foreign Keys activées, requêtes paramétrées)
- **Architecture** : Clean Architecture, Repository Pattern, Services centralisés
- **Tests** : Pytest 9.1+ (24 tests automatisés passés avec succès)
- **Compilation Mobile** : Buildozer & python-for-android
- **Intégration Native** : PyJNIus (Notifications, Vibration haptique, Cycle de vie Android)

---

## 🧪 EXÉCUTION DES TESTS AUTOMATISÉS

Pour lancer l'ensemble de la suite de tests automatisés :
```bash
python -m pytest -v
```

---

## 📱 COMPILATION DE L'APK ANDROID (BUILDOZER / WSL2 / LINUX)

Pour compiler le fichier APK installable sur votre Xiaomi Redmi :

### Option A : Via Ubuntu sur WSL2
```bash
chmod +x build_apk_wsl.sh
./build_apk_wsl.sh
```

### Option B : Via Docker
```bash
docker build -f Dockerfile.buildozer -t lifeos-builder .
docker run --rm -v $(pwd):/home/builder/app lifeos-builder
```

Le fichier APK compilé est automatiquement généré dans :
```
release/LifeOS-v1.0.0-debug.apk
```

---

## 📲 INSTALLATION SUR XIAOMI REDMI VIA ADB

1. Activez le **Débogage USB** et **Installer via USB** dans les options développeur de votre Xiaomi Redmi.
2. Connectez le téléphone à l'ordinateur en USB.
3. Lancez le script :
```cmd
install_apk_adb.bat
```
Ou tapez directement :
```cmd
adb install -r release/LifeOS-v1.0.0-debug.apk
```

---

## 📂 STRUCTURE DU PROJET

Consultez [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) pour les détails d'architecture et [docs/USER_GUIDE.md](docs/USER_GUIDE.md) pour le guide utilisateur complet.
