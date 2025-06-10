from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
from plyer import camera, storagepath
import os
import threading
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime
from kivy.utils import platform

# Google Drive API scope
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class PhotoUploaderApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service_account_info = None
        self.load_service_account()

    def load_service_account(self):
        """Load service account from file or environment variable"""
        try:
            # Try to load from file first (for development)
            if os.path.exists('service_account.json'):
                with open('service_account.json', 'r') as f:
                    self.service_account_info = json.load(f)
                return
            
            # Try to load from environment variable (for Android/build)
            import android  # Only available on Android
            from jnius import autoclass  # For accessing Java environment
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            current_activity = PythonActivity.mActivity
            env = current_activity.getApplicationContext().getResources()
            
            # Get service account from build config
            service_account_json = env.getString(
                current_activity.getResources().getIdentifier(
                    'service_account_json', 
                    'string', 
                    current_activity.getPackageName()
                )
            )
            
            if service_account_json:
                self.service_account_info = json.loads(service_account_json)
                
        except Exception as e:
            print(f"Error loading service account: {e}")

    def build(self):
        self.title = "Photo Uploader"
        
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Status label
        self.status_label = Label(
            text='Ready to take photos!' if self.service_account_info else '⚠️ Service account not configured!',
            size_hint_y=0.3,
            text_size=(None, None),
            halign='center',
            color=(1, 1, 1, 1) if self.service_account_info else (1, 0.5, 0.5, 1)
        )
        
        # Capture button
        self.capture_btn = Button(
            text='📷 Take Photo & Upload',
            size_hint_y=0.4,
            font_size='18sp',
            disabled=not self.service_account_info
        )
        self.capture_btn.bind(on_press=self.capture_and_upload)
        
        # Info label
        info_label = Label(
            text='Photos will be uploaded to Google Drive' if self.service_account_info else 'Configure service account to enable uploads',
            size_hint_y=0.3,
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1)
        
        layout.add_widget(self.status_label)
        layout.add_widget(self.capture_btn)
        layout.add_widget(info_label)
        
        return layout
    
    def show_popup(self, title, message):
        """Show a popup with the given title and message"""
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_label = Label(text=message, text_size=(280, None), halign='center')
        popup_button = Button(text='OK', size_hint_y=0.3)
        
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(popup_button)
        
        popup = Popup(
            title=title,
            content=popup_layout,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        popup_button.bind(on_press=popup.dismiss)
        popup.open()
    
    def update_status(self, message, is_error=False):
        """Update status label safely from any thread"""
        color = (1, 0.5, 0.5, 1) if is_error else (1, 1, 1, 1)
        Clock.schedule_once(
            lambda dt: (
                setattr(self.status_label, 'text', message),
                setattr(self.status_label, 'color', color)
            )
        )
    
    def set_button_enabled(self, enabled):
        """Enable/disable the capture button"""
        Clock.schedule_once(lambda dt: setattr(self.capture_btn, 'disabled', not enabled))
    
    def get_photo_path(self):
        """Get appropriate path for saving photos based on platform"""
        try:
            if platform == 'android':
                # Use Android-specific storage locations
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
                
                # Try to get DCIM directory first
                dcim_path = os.path.join(storagepath.get_external_storage_dir(), 'DCIM')
                if os.path.exists(dcim_path):
                    photos_dir = os.path.join(dcim_path, 'PhotoUploader')
                    os.makedirs(photos_dir, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    return os.path.join(photos_dir, f"photo_{timestamp}.jpg")
            
            # Fallback for all platforms
            photos_dir = os.path.join(storagepath.get_pictures_dir(), 'PhotoUploader')
            os.makedirs(photos_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return os.path.join(photos_dir, f"photo_{timestamp}.jpg")
            
        except Exception as e:
            print(f"Storage path error: {e}")
            # Last resort fallback
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"photo_{timestamp}.jpg"
    
    def capture_and_upload(self, instance):
        """Capture photo and start upload process"""
        if not self.service_account_info:
            self.show_popup('Error', 'Service account not configured')
            return
            
        self.set_button_enabled(False)
        self.update_status('Taking photo...')
        
        try:
            self.filepath = self.get_photo_path()
            print(f"Photo will be saved to: {self.filepath}")
            
            # Handle Android-specific camera requirements
            if platform == 'android':
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.CAMERA])
            
            camera.take_picture(
                filename=self.filepath,
                on_complete=self.on_photo_complete
            )
        except Exception as e:
            error_msg = f"Camera error: {str(e)}"
            print(error_msg)
            self.update_status('Camera failed!', True)
            Clock.schedule_once(lambda dt: self.show_popup('Camera Error', error_msg), 0.5)
            self.set_button_enabled(True)
    
    def on_photo_complete(self, filepath):
        """Called when photo capture is complete"""
        if not filepath or not os.path.exists(filepath):
            self.update_status('Photo capture failed!', True)
            Clock.schedule_once(lambda dt: self.show_popup('Error', 'Failed to capture photo'), 0.5)
            self.set_button_enabled(True)
            return
        
        self.update_status('Photo captured! Uploading...')
        # Start upload in background thread to avoid blocking UI
        threading.Thread(
            target=self.upload_to_drive, 
            args=(filepath,),
            daemon=True
        ).start()
    
    def upload_to_drive(self, filepath):
        """Upload photo to Google Drive (runs in background thread)"""
        try:
            if not self.service_account_info:
                raise Exception("Service account not loaded")
            
            # Authenticate using the service account
            self.update_status('Authenticating...')
            creds = service_account.Credentials.from_service_account_info(
                self.service_account_info, 
                scopes=SCOPES
            )
            
            # Connect to the Drive API
            self.update_status('Connecting to Drive...')
            service = build('drive', 'v3', credentials=creds)
            
            # Prepare file metadata
            filename = os.path.basename(filepath)
            file_metadata = {
                'name': filename,
                'description': f'Photo uploaded from PhotoUploader app on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                'parents': ['root']  # Upload to root folder
            }
            
            # Prepare media upload
            self.update_status('Uploading photo...')
            media = MediaFileUpload(
                filepath, 
                mimetype='image/jpeg',
                resumable=True
            )
            
            # Upload the file with progress tracking
            request = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    self.update_status(f'Uploading... {progress}%')
            
            # Success
            file_id = response.get('id')
            file_name = response.get('name')
            success_msg = f'✅ Upload successful!\nFile: {file_name}'
            
            print(f"Uploaded to Drive. File ID: {file_id}")
            self.update_status('Upload completed!')
            
            Clock.schedule_once(lambda dt: self.show_popup('Success', success_msg), 0.5)
            
        except Exception as e:
            error_msg = f"Upload failed: {str(e)}"
            print(error_msg)
            self.update_status('Upload failed!', True)
            Clock.schedule_once(lambda dt: self.show_popup('Upload Error', error_msg), 0.5)
        
        finally:
            # Clean up local file
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"Cleaned up local file: {filepath}")
            except Exception as e:
                print(f"Error cleaning up file: {e}")
            
            # Re-enable button
            self.set_button_enabled(True)

if __name__ == '__main__':
    PhotoUploaderApp().run()
