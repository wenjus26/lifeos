[app]

# (str) Title of your application
title = LifeOS

# (str) Package name
package.name = lifeos

# (str) Package domain (needed for android/ios packaging)
package.domain = org.lifeos

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,db,json,txt

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,app/*

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.2,kivymd==2.0.0,sqlite3,pillow,pyjnius

# (str) Presplash of the application
presplash.filename = %(source.dir)s/assets/images/splash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icons/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = VIBRATE,POST_NOTIFICATIONS,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 35

# (int) Minimum API your APP will support.
android.minapi = 26

# (str) Android NDK version to use
android.ndk = 28.2.13676358

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# arm64-v8a est l'architecture standard des smartphones Xiaomi Redmi modernes
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) The format used to package the app for release mode (aab or apk)
android.release_artifact = apk

# (str) The format used to package the app for debug mode (apk)
android.debug_artifact = apk

# (str) python-for-android git clone directory
p4a.branch = master

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug with command output)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifacts
bin_dir = ./release
