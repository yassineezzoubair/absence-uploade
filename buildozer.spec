[app]

title = PhotoUploader
package.name = photouploader
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3,kivy,plyer,google-api-python-client,google-auth,certifi,urllib3,chardet,idna
orientation = portrait

android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

# إضافة ملف credentials
android.add_asset = service_account.json

# دعم كاميرا أندرويد
android.api = 31
android.minapi = 21
android.ndk = 23b
android.arch = armeabi-v7a
android.sdk = 30
android.ndk_path = 
android.sdk_path = 

# لمنع مشاكل التصاريح
android.useandroidx = True
android.enable_androidx_workaround = True

# دعم الإصدارات الجديدة
android.gradle_dependencies = com.google.android.gms:play-services-auth:20.1.0
android.add_asset = service_account.json

# لإضافة صلاحيات رفع الملفات والوصول للإنترنت
android.allow_backup = True
android.logcat_filters = *:S python:D

# هذا إذا أردت أيقونة لاحقًا
# icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
