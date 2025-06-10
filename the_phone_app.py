from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
from plyer import camera, storagepath
import os
import threading
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime

# Google Drive API scope
SCOPES = ['https://www.googleapis.com/auth/drive.file']
# Path to your service account file
SERVICE_ACCOUNT_FILE = 'service_account.json'

class PhotoUploaderApp(App):
    def build(self):
        self.title = "Photo Uploader"
        
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Status label
        self.status_label = Label(
            text='Ready to take photos!',
            size_hint_y=0.3,
            text_size=(None, None),
            halign='center'
        )
        
        # Capture button
        self.capture_btn = Button(
            text='📷 Take Photo & Upload',
            size_hint_y=0.4,
            font_size='18sp'
        )
        self.capture_btn.bind(on_press=self.capture_and_upload)
        
        # Info label
        info_label = Label(
            text='Photos will be uploaded to Google Drive',
            size_hint_y=0.3,
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1)
        )
        
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
    
    def update_status(self, message):
        """Update status label safely from any thread"""
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', message))
    
    def set_button_enabled(self, enabled):
        """Enable/disable the capture button"""
        Clock.schedule_once(lambda dt: setattr(self.capture_btn, 'disabled', not enabled))
    
    def get_photo_path(self):
        """Get appropriate path for saving photos based on platform"""
        try:
            # Try to get external storage path
            external_path = storagepath.get_external_storage_dir()
            if external_path:
                photos_dir = os.path.join(external_path, 'Pictures', 'PhotoUploader')
                os.makedirs(photos_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                return os.path.join(photos_dir, f"photo_{timestamp}.jpg")
        except Exception as e:
            print(f"External storage error: {e}")
        
        # Fallback to internal storage
        try:
            internal_path = storagepath.get_pictures_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return os.path.join(internal_path, f"photo_{timestamp}.jpg")
        except:
            # Last resort fallback
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"/sdcard/photo_{timestamp}.jpg"
    
    def capture_and_upload(self, instance):
        """Capture photo and start upload process"""
        self.set_button_enabled(False)
        self.update_status('Taking photo...')
        
        try:
            self.filepath = self.get_photo_path()
            print(f"Photo will be saved to: {self.filepath}")
            
            camera.take_picture(
                filename=self.filepath,
                on_complete=self.on_photo_complete
            )
        except Exception as e:
            error_msg = f"Camera error: {str(e)}"
            print(error_msg)
            self.update_status('Camera failed!')
            Clock.schedule_once(lambda dt: self.show_popup('Camera Error', error_msg), 0.5)
            self.set_button_enabled(True)
    
    def on_photo_complete(self, filepath):
        """Called when photo capture is complete"""
        if not filepath or not os.path.exists(filepath):
            self.update_status('Photo capture failed!')
            Clock.schedule_once(lambda dt: self.show_popup('Error', 'Failed to capture photo'), 0.5)
            self.set_button_enabled(True)
            return
        
        self.update_status('Photo captured! Uploading...')
        # Start upload in background thread to avoid blocking UI
        threading.Thread(target=self.upload_to_drive, args=(filepath,), daemon=True).start()
    
    def upload_to_drive(self, filepath):
        """Upload photo to Google Drive (runs in background thread)"""
        try:
            # Check if service account file exists
            if not os.path.exists(SERVICE_ACCOUNT_FILE):
                raise FileNotFoundError(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")
            
            # Authenticate using the service account
            self.update_status('Authenticating...')
            creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            
            # Connect to the Drive API
            self.update_status('Connecting to Drive...')
            service = build('drive', 'v3', credentials=creds)
            
            # Prepare file metadata
            filename = os.path.basename(filepath)
            file_metadata = {
                'name': filename,
                'description': f'Photo uploaded from PhotoUploader app on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            }
            
            # Prepare media upload
            self.update_status('Uploading photo...')
            media = MediaFileUpload(filepath, mimetype='image/jpeg')
            
            # Upload the file
            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            ).execute()
            
            # Success
            file_id = uploaded_file.get('id')
            file_name = uploaded_file.get('name')
            success_msg = f'✅ Upload successful!\nFile: {file_name}\nID: {file_id}'
            
            print(f"Uploaded to Drive. File ID: {file_id}")
            self.update_status('Upload completed!')
            
            Clock.schedule_once(lambda dt: self.show_popup('Success', success_msg), 0.5)
            
            # Clean up local file (optional)
            try:
                os.remove(filepath)
                print(f"Cleaned up local file: {filepath}")
            except:
                pass
                
        except Exception as e:
            error_msg = f"Upload failed: {str(e)}"
            print(error_msg)
            self.update_status('Upload failed!')
            Clock.schedule_once(lambda dt: self.show_popup('Upload Error', error_msg), 0.5)
        
        finally:
            # Re-enable button
            self.set_button_enabled(True)

if __name__ == '__main__':
    PhotoUploaderApp().run()
