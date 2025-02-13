import json
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build, http

# Load service account credentials from environment variable
SERVICE_ACCOUNT_JSON = os.getenv("GDRIVE_SERVICE_ACCOUNT")
FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")  # Read from GitHub secrets

if not SERVICE_ACCOUNT_JSON:
    raise ValueError(
        "❌ Service Account JSON not found! Set GDRIVE_SERVICE_ACCOUNT as a secret."
    )
if not FOLDER_ID:
    raise ValueError(
        "❌ Google Drive Folder ID not found! Set GDRIVE_FOLDER_ID as a secret."
    )

# Save service account JSON to a temporary file
SERVICE_ACCOUNT_FILE = "service_account.json"
with open(SERVICE_ACCOUNT_FILE, "w") as f:
    f.write(SERVICE_ACCOUNT_JSON)

# Authenticate and create the Drive API service
SCOPES = ["https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("drive", "v3", credentials=creds)

# Remove the service account file for security
os.remove(SERVICE_ACCOUNT_FILE)

# 📂 Define folder to store files
LOCAL_PDF_DIR = "main/pdfs"
if not os.path.exists(LOCAL_PDF_DIR):
    os.makedirs(LOCAL_PDF_DIR)


def download_from_drive(file_name):
    """
    Downloads a specific file from Google Drive to GitHub repo.

    :param file_name: The name of the file to download.
    """
    query = f"'{FOLDER_ID}' in parents and name='{file_name}'"
    results = service.files().list(q=query, fields="files(id, name)").execute()

    files = results.get("files", [])
    if not files:
        print(f"⚠️ File {file_name} not found in Google Drive.")
        return

    file_id = files[0]["id"]
    file_path = os.path.join(LOCAL_PDF_DIR, file_name)

    # Download the file
    request = service.files().get_media(fileId=file_id)
    with open(file_path, "wb") as pdf_file:
        pdf_file.write(request.execute())

    print(f"✅ Downloaded {file_name} from Google Drive to {file_path}")


def upload_to_drive(file_path):
    """
    Uploads a file from GitHub repo to Google Drive.

    :param file_path: Local file path to upload.
    """
    file_name = os.path.basename(file_path)

    file_metadata = {"name": file_name, "parents": [FOLDER_ID]}
    media = http.MediaFileUpload(file_path, mimetype="image/png")

    uploaded_file = (
        service.files().create(body=file_metadata, media_body=media).execute()
    )
    print(
        f"✅ Uploaded {file_name} to Google Drive (File ID: {uploaded_file.get('id')})"
    )
