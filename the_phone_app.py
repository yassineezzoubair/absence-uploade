from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from plyer import camera
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class MyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        button = Button(text='Take Photo and Upload')
        button.bind(on_press=self.capture_and_upload)
        layout.add_widget(button)
        return layout

    def capture_and_upload(self, instance):
        filepath = "/sdcard/photo.jpg"
        camera.take_picture(filename=filepath, on_complete=self.upload_to_drive)

    def upload_to_drive(self, filepath):
        if not filepath:
            print("No photo taken.")
            return

        creds = authenticate()
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {'name': os.path.basename(filepath)}
        media = MediaFileUpload(filepath, mimetype='image/jpeg')
        service.files().create(body=file_metadata, media_body=media).execute()
        print("Uploaded to Drive:", filepath)

def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

if __name__ == '__main__':
    MyApp().run()
