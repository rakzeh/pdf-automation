import json
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load service account credentials from environment variable
SERVICE_ACCOUNT_JSON = os.getenv("GDRIVE_SERVICE_ACCOUNT")
FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")  # Read from GitHub secrets

# Ensure required environment variables are set
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

# Directory to store downloaded PDFs
PDF_DIR = "pdfs"

# Authenticate and create the Drive API service
SCOPES = ["https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("drive", "v3", credentials=creds)


def download_pdfs():
    """Download PDFs from a specific Google Drive folder."""
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR)

    # Search for PDFs in the specified Google Drive folder
    query = f"'{FOLDER_ID}' in parents and mimeType='application/pdf'"
    results = service.files().list(q=query, fields="files(id, name)").execute()

    files = results.get("files", [])
    if not files:
        print("⚠️ No PDFs found in Google Drive folder.")
        return

    for file in files:
        file_id = file["id"]
        file_name = file["name"]
        file_path = os.path.join(PDF_DIR, file_name)

        # Download the file
        request = service.files().get_media(fileId=file_id)
        with open(file_path, "wb") as pdf_file:
            pdf_file.write(request.execute())

        print(f"✅ Downloaded: {file_name}")


if __name__ == "__main__":
    try:
        download_pdfs()
    finally:
        # Delete the service account file after execution
        if os.path.exists(SERVICE_ACCOUNT_FILE):
            os.remove(SERVICE_ACCOUNT_FILE)
            print("🛑 Deleted temporary service account file.")
