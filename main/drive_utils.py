# import json
# import os
# import time
#
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from googleapiclient.http import MediaFileUpload
#
# # Load service account credentials from environment variable
# SERVICE_ACCOUNT_JSON = os.getenv("GDRIVE_SERVICE_ACCOUNT")
# FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")  # Root folder ID from GitHub secrets
#
# if not SERVICE_ACCOUNT_JSON:
#     raise ValueError(
#         "❌ Service Account JSON not found! Set GDRIVE_SERVICE_ACCOUNT as a secret."
#     )
# if not FOLDER_ID:
#     raise ValueError(
#         "❌ Google Drive Folder ID not found! Set GDRIVE_FOLDER_ID as a secret."
#     )
#
# # Save service account JSON to a temporary file
# SERVICE_ACCOUNT_FILE = "service_account.json"
# with open(SERVICE_ACCOUNT_FILE, "w") as f:
#     f.write(SERVICE_ACCOUNT_JSON)
#
# # Authenticate and create the Drive API service
# SCOPES = ["https://www.googleapis.com/auth/drive"]
# creds = service_account.Credentials.from_service_account_file(
#     SERVICE_ACCOUNT_FILE, scopes=SCOPES
# )
# service = build("drive", "v3", credentials=creds)
#
# # Remove the service account file for security
# os.remove(SERVICE_ACCOUNT_FILE)
#
# # 📂 Define local PDF storage folder
# LOCAL_PDF_DIR = "main/pdfs"
# os.makedirs(LOCAL_PDF_DIR, exist_ok=True)
#
#
# def get_or_create_folder(folder_name, parent_folder_id=FOLDER_ID):
#     """Checks if a folder exists in Google Drive; creates it if not."""
#     query = f"'{parent_folder_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
#     try:
#         response = service.files().list(q=query, fields="files(id)").execute()
#         folders = response.get("files", [])
#
#         if folders:
#             return folders[0]["id"]  # Folder exists, return its ID
#
#         # Create a new folder
#         folder_metadata = {
#             "name": folder_name,
#             "mimeType": "application/vnd.google-apps.folder",
#             "parents": [parent_folder_id],
#         }
#         folder = service.files().create(body=folder_metadata, fields="id").execute()
#         return folder.get("id")
#     except HttpError as error:
#         print(f"❌ Error creating folder '{folder_name}': {error}")
#         return None
#
#
# def download_from_drive(file_name, local_dir=LOCAL_PDF_DIR, retries=3):
#     """Downloads a specific file from Google Drive."""
#     query = f"'{FOLDER_ID}' in parents and name='{file_name}'"
#     try:
#         results = service.files().list(q=query, fields="files(id, name)").execute()
#         files = results.get("files", [])
#         if not files:
#             print(f"⚠️ File {file_name} not found in Google Drive.")
#             return
#
#         file_id = files[0]["id"]
#         file_path = os.path.join(local_dir, file_name)
#
#         for attempt in range(retries):
#             try:
#                 request = service.files().get_media(fileId=file_id)
#                 with open(file_path, "wb") as file:
#                     file.write(request.execute())
#                 print(f"✅ Downloaded {file_name} to {file_path}")
#                 return
#             except HttpError as error:
#                 print(
#                     f"❌ Error downloading {file_name} (attempt {attempt+1}/{retries}): {error}"
#                 )
#                 time.sleep(2**attempt)  # Exponential backoff
#     except HttpError as error:
#         print(f"❌ Failed to search for {file_name}: {error}")
#
#
# def upload_to_drive(file_path, folder_name=None, parent_folder_id=FOLDER_ID, retries=3):
#     """Uploads a file to Google Drive inside a specified folder."""
#     file_name = os.path.basename(file_path)
#
#     # Ensure file exists before uploading
#     if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
#         print(f"⚠️ Skipping upload: {file_path} does not exist or is empty.")
#         return
#
#     # Determine MIME type based on file extension
#     mime_types = {
#         ".pdf": "application/pdf",
#         ".png": "image/png",
#         ".jpg": "image/jpeg",
#         ".jpeg": "image/jpeg",
#         ".txt": "text/plain",
#     }
#     mime_type = mime_types.get(
#         os.path.splitext(file_name)[1], "application/octet-stream"
#     )
#
#     # Get or create the subfolder in Google Drive
#     if folder_name:
#         parent_folder_id = get_or_create_folder(folder_name, parent_folder_id)
#
#     file_metadata = {"name": file_name, "parents": [parent_folder_id]}
#     media = MediaFileUpload(file_path, mimetype=mime_type)
#
#     for attempt in range(retries):
#         try:
#             uploaded_file = (
#                 service.files().create(body=file_metadata, media_body=media).execute()
#             )
#             print(
#                 f"✅ Uploaded {file_name} to Google Drive in {folder_name or 'root'} (File ID: {uploaded_file.get('id')})"
#             )
#             return
#         except HttpError as error:
#             print(f"❌ Upload failed (attempt {attempt+1}/{retries}): {error}")
#             time.sleep(2**attempt)  # Exponential backoff
#
#
# def upload_folder_to_drive(local_folder, drive_folder_name, parent_folder_id=FOLDER_ID):
#     """Uploads all files in a local folder to Google Drive under a specific folder."""
#     if not os.path.exists(local_folder):
#         print(f"⚠️ Local folder '{local_folder}' does not exist. Skipping upload.")
#         return
#
#     drive_folder_id = get_or_create_folder(drive_folder_name, parent_folder_id)
#     files = [
#         f
#         for f in os.listdir(local_folder)
#         if os.path.isfile(os.path.join(local_folder, f))
#     ]
#
#     if not files:
#         print(f"⚠️ No files found in '{local_folder}' to upload.")
#         return
#
#     for file_name in files:
#         file_path = os.path.join(local_folder, file_name)
#         upload_to_drive(
#             file_path, folder_name=drive_folder_name, parent_folder_id=parent_folder_id
#         )
#
#
# def delete_file_from_drive(file_name, parent_folder_id=FOLDER_ID):
#     """Deletes a file from Google Drive."""
#     query = f"'{parent_folder_id}' in parents and name='{file_name}'"
#     try:
#         results = service.files().list(q=query, fields="files(id)").execute()
#         files = results.get("files", [])
#
#         if not files:
#             print(f"⚠️ File {file_name} not found in Google Drive.")
#             return
#
#         service.files().delete(fileId=files[0]["id"]).execute()
#         print(f"🗑️ Deleted {file_name} from Google Drive.")
#     except HttpError as error:
#         print(f"❌ Failed to delete {file_name}: {error}")
#
#
# def delete_folder_from_drive(folder_name, parent_folder_id=FOLDER_ID):
#     """Deletes a folder and all its contents from Google Drive."""
#     query = f"'{parent_folder_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
#     try:
#         results = service.files().list(q=query, fields="files(id)").execute()
#         folders = results.get("files", [])
#
#         if not folders:
#             print(f"⚠️ Folder '{folder_name}' not found in Google Drive.")
#             return
#
#         service.files().delete(fileId=folders[0]["id"]).execute()
#         print(f"🗑️ Deleted folder '{folder_name}' from Google Drive.")
#     except HttpError as error:
#         print(f"❌ Failed to delete folder '{folder_name}': {error}")


import json
import os
import time

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Load service account credentials from environment variable
SERVICE_ACCOUNT_JSON = os.getenv("GDRIVE_SERVICE_ACCOUNT")
FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")  # Root folder ID from GitHub secrets

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

# 📂 Define local PDF storage folder
LOCAL_PDF_DIR = "main/pdfs"
os.makedirs(LOCAL_PDF_DIR, exist_ok=True)


def get_or_create_folder(folder_name, parent_folder_id=FOLDER_ID):
    """Checks if a folder exists in Google Drive; creates it if not."""
    query = f"'{parent_folder_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    try:
        response = service.files().list(q=query, fields="files(id)").execute()
        folders = response.get("files", [])

        if folders:
            return folders[0]["id"]  # Folder exists, return its ID

        # Create a new folder
        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_folder_id],
        }
        folder = service.files().create(body=folder_metadata, fields="id").execute()
        return folder.get("id")
    except HttpError as error:
        print(f"❌ Error creating folder '{folder_name}': {error}")
        return None


def download_from_drive(file_name, local_dir=LOCAL_PDF_DIR, retries=3):
    """Downloads a specific file from Google Drive with retries."""
    query = f"'{FOLDER_ID}' in parents and name='{file_name}'"
    try:
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get("files", [])
        if not files:
            print(f"⚠️ File {file_name} not found in Google Drive.")
            return

        file_id = files[0]["id"]
        file_path = os.path.join(local_dir, file_name)

        for attempt in range(retries):
            try:
                request = service.files().get_media(fileId=file_id)
                with open(file_path, "wb") as file:
                    file.write(request.execute())
                print(f"✅ Downloaded {file_name} to {file_path}")
                return
            except HttpError as error:
                print(
                    f"❌ Error downloading {file_name} (attempt {attempt+1}/{retries}): {error}"
                )
                time.sleep(2**attempt)  # Exponential backoff
    except HttpError as error:
        print(f"❌ Failed to search for {file_name}: {error}")


def upload_to_drive(file_path, folder_name=None, parent_folder_id=FOLDER_ID, retries=3):
    """Uploads a file to Google Drive inside a specified folder using resumable upload."""
    file_name = os.path.basename(file_path)

    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"⚠️ Skipping upload: {file_path} does not exist or is empty.")
        return

    # Determine MIME type based on file extension
    mime_types = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".txt": "text/plain",
    }
    mime_type = mime_types.get(
        os.path.splitext(file_name)[1], "application/octet-stream"
    )

    # Get or create the subfolder in Google Drive
    if folder_name:
        parent_folder_id = get_or_create_folder(folder_name, parent_folder_id)

    file_metadata = {"name": file_name, "parents": [parent_folder_id]}
    media = MediaFileUpload(
        file_path, mimetype=mime_type, resumable=True, chunksize=20 * 1024 * 1024
    )

    for attempt in range(retries):
        try:
            uploaded_file = (
                service.files().create(body=file_metadata, media_body=media).execute()
            )
            print(
                f"✅ Uploaded {file_name} to Google Drive in {folder_name or 'root'} (File ID: {uploaded_file.get('id')})"
            )
            return
        except HttpError as error:
            print(f"❌ Upload failed (attempt {attempt+1}/{retries}): {error}")
            time.sleep(2**attempt)  # Exponential backoff


def upload_folder_to_drive(local_folder, drive_folder_name, parent_folder_id=FOLDER_ID):
    """Uploads all files in a local folder to Google Drive under a specific folder."""
    if not os.path.exists(local_folder):
        print(f"⚠️ Local folder '{local_folder}' does not exist. Skipping upload.")
        return

    drive_folder_id = get_or_create_folder(drive_folder_name, parent_folder_id)
    files = [
        f
        for f in os.listdir(local_folder)
        if os.path.isfile(os.path.join(local_folder, f))
    ]

    if not files:
        print(f"⚠️ No files found in '{local_folder}' to upload.")
        return

    for file_name in files:
        file_path = os.path.join(local_folder, file_name)
        upload_to_drive(
            file_path, folder_name=drive_folder_name, parent_folder_id=parent_folder_id
        )


def delete_file_from_drive(file_name, parent_folder_id=FOLDER_ID):
    """Deletes a file from Google Drive."""
    query = f"'{parent_folder_id}' in parents and name='{file_name}'"
    try:
        results = service.files().list(q=query, fields="files(id)").execute()
        files = results.get("files", [])

        if not files:
            print(f"⚠️ File {file_name} not found in Google Drive.")
            return

        service.files().delete(fileId=files[0]["id"]).execute()
        print(f"🗑️ Deleted {file_name} from Google Drive.")
    except HttpError as error:
        print(f"❌ Failed to delete {file_name}: {error}")


def delete_folder_from_drive(folder_name, parent_folder_id=FOLDER_ID):
    """Deletes a folder and all its contents from Google Drive."""
    query = f"'{parent_folder_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    try:
        results = service.files().list(q=query, fields="files(id)").execute()
        folders = results.get("files", [])

        if not folders:
            print(f"⚠️ Folder '{folder_name}' not found in Google Drive.")
            return

        service.files().delete(fileId=folders[0]["id"]).execute()
        print(f"🗑️ Deleted folder '{folder_name}' from Google Drive.")
    except HttpError as error:
        print(f"❌ Failed to delete folder '{folder_name}': {error}")
