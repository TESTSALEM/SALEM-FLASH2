[app]

# (str) Title of your application
title = SALEMFLASH

# (str) Package name
package.name = salemflash

# (str) Package domain (needed for android/ios packaging)
package.domain = org.salemflash

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Application versioning
version = 1.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
# هام جداً: التعديل تم هنا (pyjnius)
requirements = python3,kivy==2.2.0,android,pyjnius,arabic-reshaper,python-bidi

# (str) Icon of the application
icon.filename = flashlight-app-icon-14.jpg

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = CAMERA,FLASHLIGHT

# (int) Target Android API, should be as high as possible (usually 33+)
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (int) python-for-android version to use
p4a.branch = master

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
