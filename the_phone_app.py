from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from plyer import camera
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Google Drive API scope
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Path to your service account file (must be in root folder and added via buildozer.spec)
SERVICE_ACCOUNT_FILE = 'service_account.json'

class MyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        button = Button(text='Take Photo and Upload')
        button.bind(on_press=self.capture_and_upload)
        layout.add_widget(button)
        return layout

    def capture_and_upload(self, instance):
        # File path where the photo will be saved
        self.filepath = "/sdcard/photo.jpg"
        try:
            camera.take_picture(filename=self.filepath, on_complete=self.upload_to_drive)
        except Exception as e:
            print("Camera error:", e)

    def upload_to_drive(self, filepath):
        if not filepath:
            print("No photo taken.")
            return

        try:
            # Authenticate using the service account
            creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)

            # Connect to the Drive API
            service = build('drive', 'v3', credentials=creds)

            # Prepare file metadata and media
            file_metadata = {'name': os.path.basename(filepath)}
            media = MediaFileUpload(filepath, mimetype='image/jpeg')

            # Upload the file
            uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print("Uploaded to Drive. File ID:", uploaded_file.get('id'))

        except Exception as e:
            print("Upload failed:", e)

if __name__ == '__main__':
    MyApp().run()
