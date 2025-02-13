import json
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

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


def get_or_create_folder(folder_name, parent_folder_id=None):
    """
    Checks if a folder exists in Google Drive; creates it if not.
    :param folder_name: Name of the folder.
    :param parent_folder_id: Parent folder ID where this folder should be created.
    :return: Folder ID of the existing or newly created folder.
    """
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"

    response = service.files().list(q=query, fields="files(id)").execute()
    folders = response.get("files", [])

    if folders:
        return folders[0]["id"]  # Folder exists, return its ID

    # Create a new folder
    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_folder_id:
        folder_metadata["parents"] = [parent_folder_id]

    folder = service.files().create(body=folder_metadata, fields="id").execute()
    return folder.get("id")  # Return the newly created folder's ID


def download_from_drive(file_name, local_dir=LOCAL_PDF_DIR):
    """
    Downloads a specific file from Google Drive to a local directory.
    :param file_name: The name of the file to download.
    :param local_dir: Local directory to save the file.
    """
    query = f"'{FOLDER_ID}' in parents and name='{file_name}'"
    results = service.files().list(q=query, fields="files(id, name)").execute()

    files = results.get("files", [])
    if not files:
        print(f"⚠️ File {file_name} not found in Google Drive.")
        return

    file_id = files[0]["id"]
    file_path = os.path.join(local_dir, file_name)

    request = service.files().get_media(fileId=file_id)
    with open(file_path, "wb") as file:
        file.write(request.execute())

    print(f"✅ Downloaded {file_name} from Google Drive to {file_path}")


def upload_to_drive(file_path, folder_name=None, parent_folder_id=FOLDER_ID):
    """
    Uploads a file to Google Drive inside a specified folder.
    :param file_path: Local file path to upload.
    :param folder_name: Optional name of the folder inside Google Drive.
    :param parent_folder_id: Parent folder ID where the file will be uploaded.
    """
    file_name = os.path.basename(file_path)
    mime_type = "application/octet-stream"  # Default MIME type

    # Determine MIME type based on file extension
    if file_name.endswith(".pdf"):
        mime_type = "application/pdf"
    elif file_name.endswith(".png"):
        mime_type = "image/png"
    elif file_name.endswith(".jpg") or file_name.endswith(".jpeg"):
        mime_type = "image/jpeg"
    elif file_name.endswith(".txt"):
        mime_type = "text/plain"

    # Get or create a folder inside Google Drive
    if folder_name:
        parent_folder_id = get_or_create_folder(folder_name, parent_folder_id)

    file_metadata = {"name": file_name, "parents": [parent_folder_id]}
    media = MediaFileUpload(file_path, mimetype=mime_type)

    try:
        uploaded_file = (
            service.files().create(body=file_metadata, media_body=media).execute()
        )
        print(
            f"✅ Uploaded {file_name} to Google Drive in {folder_name or 'root'} (File ID: {uploaded_file.get('id')})"
        )
    except HttpError as error:
        print(f"❌ Failed to upload {file_name}: {error}")
