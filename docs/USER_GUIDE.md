# GUIDE D'UTILISATION ET INSTALLATION — LIFEOS

Bienvenue dans **LifeOS**, votre système d'exploitation personnel mobile conçu pour fonctionner **100% hors connexion** sur votre smartphone Xiaomi Redmi (MIUI / HyperOS).

---

## 1. INSTALLATION SUR XIAOMI REDMI (MIUI / HYPEROS)

### A. Prérequis sur votre téléphone
1. **Activer les Options Développeur** :
   - Allez dans `Paramètres` > `À propos de l'appareil`.
   - Tapez 7 fois de suite sur **Version de l'OS** (ou Version MIUI) jusqu'au message *"Vous êtes désormais développeur"*.
2. **Activer le Débogage USB & Installer via USB** :
   - Allez dans `Paramètres` > `Paramètres supplémentaires` > `Options pour les développeurs`.
   - Cochez **Débogage USB**.
   - Cochez **Installer via USB** *(indispensable sur Xiaomi / HyperOS)*.
   - Cochez **Débogage USB (paramètres de sécurité)** si demandé.

### B. Installation directe par câble USB
Connectez votre Xiaomi Redmi à l'ordinateur par câble USB, puis exécutez le script :
```cmd
install_apk_adb.bat
```
Ou manuellement via ADB :
```cmd
adb install -r release\LifeOS-v1.0.0-debug.apk
```

### C. Installation directe sans PC
1. Transférez le fichier `LifeOS-v1.0.0-debug.apk` sur votre téléphone (via WhatsApp, Telegram, câble ou carte SD).
2. Ouvrez l'application **Gestionnaire de fichiers** de votre Xiaomi.
3. Touchez le fichier APK et autorisez l'installation d'applications de sources inconnues.

---

## 2. FONCTIONNALITÉS ET GUIDE AU QUOTIDIEN

### 💰 A. Finances personnelles
- **Devise par défaut** : Franc CFA (XOF / FCFA).
- **Portefeuilles multiples** : Espèces, Wave Mobile Money, Compte Bancaire, Orange Money, etc.
- **Revenus & Dépenses** : Enregistrement avec mise à jour instantanée du solde de vos comptes.
- **Budgets mensuels** : Définissez un budget global ou par catégorie (Alimentation, Transport, Sorties). Une alerte visuelle et une vibration se déclenchent dès 80% du seuil atteint.
- **Dettes & Créances** : Suivez précisément l'argent que vous devez et celui qu'on vous doit, avec historique des remboursements partiels.
- **Objectifs d'épargne** : Définissez vos objectifs d'achat (Laptop, Voyage, Fonds d'urgence) avec barre de progression.
- **Export CSV** : Exportez tout votre historique financier en un clic sans Internet.

### 📋 B. Tâches & Productivité
- **Priorités visuelles** : Urgent, Haute, Moyenne, Basse.
- **Sous-tâches** : Listes de contrôle à cocher étape par étape.
- **Tâches récurrentes** : Quotidiennes, hebdomadaires, mensuelles. Dès qu'une tâche récurrente est cochée, la suivante est automatiquement planifiée.

### 🎯 C. Habitudes & Streaks (Séries)
- Suivez vos routines quotidiennes (ex: Sport, Lecture, Méditation, Eau).
- **Validation en un clic** : Cochez l'étoile ★ chaque jour.
- **Compteur de séries** : Suivez votre régularité et votre record de jours consécutifs.

### 🏆 D. Objectifs de vie
- Définissez vos grands projets personnels et professionnels.
- Décomposez chaque objectif en **Jalons**. La progression globale en pourcentage se met à jour automatiquement.

### 📅 E. Calendrier & Agenda
- Vue synthétique de votre journée combinant vos rendez-vous, vos tâches prioritaires et vos habitudes.

### 📝 F. Carnet de Notes
- Vos idées, comptes-rendus et listes rapides avec recherche instantanée et épinglage en favoris.

### 🔒 G. Sécurité & Données
- **Verrouillage PIN** : Protégez l'accès à vos informations sensibles.
- **Sauvegarde intégrale** : Créez une sauvegarde JSON ou base brute SQLite en un clic dans la mémoire locale de votre téléphone.
