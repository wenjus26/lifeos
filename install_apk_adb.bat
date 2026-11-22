@echo off
REM ==============================================================================
REM LIFEOS — SCRIPT D'INSTALLATION ADB SUR SMARTPHONE XIAOMI REDMI
REM ==============================================================================
echo =======================================================
echo          INSTALLATION DE LIFEOS SUR XIAOMI REDMI
echo =======================================================

SET ADB_PATH=C:\Users\Juste.DESKTOP-ERTI752\AppData\Local\Android\Sdk\platform-tools\adb.exe
SET APK_PATH=release\LifeOS-v1.0.0-debug.apk

if not exist "%ADB_PATH%" (
    echo [ERREUR] ADB est introuvable au chemin specifie : %ADB_PATH%
    pause
    exit /b 1
)

if not exist "%APK_PATH%" (
    echo [ERREUR] Le fichier APK est introuvable : %APK_PATH%
    echo Assurez-vous d'avoir compile l'APK prealablement.
    pause
    exit /b 1
)

echo [1/3] Verification de l'appareil connecte...
"%ADB_PATH%" devices

echo.
echo [2/3] Installation de l'application LifeOS...
"%ADB_PATH%" install -r "%APK_PATH%"

if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] L'installation a echoue. Verifiez que l'option "Installer via USB"
    echo est activee dans les options developpeur de votre Xiaomi Redmi / HyperOS.
    pause
    exit /b 1
)

echo.
echo [3/3] Lancement de LifeOS sur le telephone...
"%ADB_PATH%" shell am start -n org.lifeos.lifeos/org.kivy.android.PythonActivity

echo =======================================================
echo SUCCES : LifeOS a ete installe et lance avec succes !
echo =======================================================
pause
