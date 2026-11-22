#!/bin/bash
# ==============================================================================
# LIFEOS — SCRIPT DE COMPILATION APK ANDROID VIA BUILDOZER (UBUNTU / WSL2)
# ==============================================================================

set -e

echo "=== [1/5] MISE À JOUR DU SYSTÈME ET DÉPENDANCES LINUX ==="
sudo apt-get update -y
sudo apt-get install -y \
    python3 python3-pip python3-setuptools python3-venv \
    git zip unzip openjdk-17-jdk autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 \
    cmake libffi-dev libssl-dev build-essential ccache

echo "=== [2/5] CONFIGURATION DE JAVA 17 ==="
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

echo "=== [3/5] CRÉATION D'UN ENVIRONNEMENT VIRTUEL ET INSTALLATION DE BUILDOZER ==="
python3 -m venv venv_buildozer
source venv_buildozer/bin/activate
pip install --upgrade pip
pip install "buildozer>=1.5.0" "cython<3.0.0" "virtualenv"

echo "=== [4/5] PRÉPARATION DU RÉPERTOIRE RELEASE ==="
mkdir -p release

echo "=== [5/5] LANCEMENT DE LA COMPILATION DE L'APK DEBUG ==="
# Compilation de l'APK
buildozer android debug

# Renommage et placement dans release/
if [ -f bin/*.apk ]; then
    cp bin/*.apk release/LifeOS-v1.0.0-debug.apk
    echo "=============================================================================="
    echo "SUCCÈS : L'APK a été généré avec succès dans release/LifeOS-v1.0.0-debug.apk"
    echo "=============================================================================="
else
    echo "ERREUR : Le fichier APK n'a pas été trouvé dans bin/"
    exit 1
fi
