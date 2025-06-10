[app]
# Basic app info
title = PhotoUploader
package.name = photouploader
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
version = 1.0

# Python requirements - updated versions with service account support
requirements = 
    python3,
    kivy==2.3.0,
    plyer==2.1.0,
    google-api-python-client==2.117.0,
    google-auth==2.27.0,
    google-auth-oauthlib==1.2.0,
    google-auth-httplib2==0.1.1,
    certifi,
    pillow==10.2.0,
    requests==2.31.0,
    oauth2client==4.1.3  # Added for better service account support

# App configuration
orientation = portrait

# Permissions - keeping storage access for service account
android.permissions = 
    CAMERA,
    INTERNET,
    ACCESS_NETWORK_STATE,
    ACCESS_WIFI_STATE,
    WAKE_LOCK,
    VIBRATE,
    READ_EXTERNAL_STORAGE,
    WRITE_EXTERNAL_STORAGE

# Service account configuration
android.add_src = service_account.json

# Android API configuration
android.api = 34
android.minapi = 21
android.ndk = 25.2.9519653
android.arch = arm64-v8a
android.sdk = 34

# Modern Android support
android.useandroidx = True
android.enable_androidx_workaround = True

# Gradle dependencies with service account support
android.gradle_dependencies = 
    com.google.android.gms:play-services-auth:21.0.0,
    androidx.core:core-ktx:1.12.0,
    androidx.appcompat:appcompat:1.6.1,
    com.google.api-client:google-api-client-android:2.2.0

# Additional Android configuration
android.allow_backup = True
android.logcat_filters = *:S python:D

# Build configuration
android.release_artifact = apk
android.debug.sign = 1

# Application metadata
android.meta_data = 
    com.google.android.gms.version=@integer/google_play_services_version

# Build optimization
android.gradle.option = 
    android.useAndroidX=true,
    android.enableJetifier=true

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
