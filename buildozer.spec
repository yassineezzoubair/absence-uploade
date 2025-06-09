[app]
title = AbsenceUploader
package.name = absenceuploader
package.domain = org.school
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,requests,google-api-python-client,oauth2client,httplib2,pillow
orientation = portrait
fullscreen = 1
android.permissions = CAMERA,INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.hardware = camera
entrypoint = the_phone_app.py
[buildozer]
log_level = 2
warn_on_root = 1
android.api = 31
android.minapi = 21
android.ndk = 23b
android.arch = armeabi-v7a
