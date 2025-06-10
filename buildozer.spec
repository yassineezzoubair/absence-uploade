[app]
# Basic app info
title = PhotoUploader
package.name = photouploader
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
version = 1.0
# Consider adding version.regex for auto-versioning

# Python requirements - organized and with specific versions for stability
requirements = python3,kivy==2.1.0,plyer,google-api-python-client==2.88.0,google-auth==2.17.3,google-auth-oauthlib,google-auth-httplib2,certifi,urllib3,chardet,idna,requests,pillow

# App configuration
orientation = portrait
# Uncomment and add icon when ready
# icon.filename = %(source.dir)s/data/icon.png
# icon.adaptive_foreground.filename = %(source.dir)s/data/icon_fg.png
# icon.adaptive_background.filename = %(source.dir)s/data/icon_bg.png

# Permissions - organized by category
# Camera and storage
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE
# Network
android.permissions += ,INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE
# Additional useful permissions
android.permissions += ,WAKE_LOCK,VIBRATE

# Add service account credentials
android.add_src = service_account.json
# Alternative if the above doesn't work:
# android.add_asset = service_account.json

# Android API configuration - updated for better compatibility
android.api = 33
android.minapi = 21
android.ndk = 25b
android.arch = armeabi-v7a,arm64-v8a
android.sdk = 33
android.ndk_path = 
android.sdk_path = 

# Modern Android support
android.useandroidx = True
android.enable_androidx_workaround = True

# Gradle dependencies for Google services
android.gradle_dependencies = com.google.android.gms:play-services-auth:20.7.0,androidx.core:core:1.10.1,androidx.appcompat:appcompat:1.6.1

# Additional Android configuration
android.allow_backup = True
android.backup_rules = %(source.dir)s/backup_rules.xml
android.logcat_filters = *:S python:D

# Network security config for HTTPS
android.add_src = network_security_config.xml
android.manifest.intent_filters = intent_filters.xml

# Optimize build
android.release_artifact = aab
android.debug.sign = 1

# Application metadata
android.meta_data = com.google.android.gms.version=@integer/google_play_services_version

# Build optimization
android.gradle.option = android.useAndroidX=true
android.gradle.option += android.enableJetifier=true

[buildozer]
log_level = 2
warn_on_root = 1

# Build directories
build_dir = ./.buildozer
bin_dir = ./bin
