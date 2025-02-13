import os

from drive_utils import download_from_drive, upload_to_drive

# 📂 Define folder for storing PDFs
PDF_DIR = "main/pdfs"

# List of PDFs to download and re-upload
PDF_NAMES = ["demo.pdf"]  # Add more names if needed

if __name__ == "__main__":
    for pdf_name in PDF_NAMES:
        # Download the PDF from Google Drive
        download_from_drive(pdf_name)

        # Path of the downloaded PDF
        pdf_path = os.path.join(PDF_DIR, pdf_name)

        # Upload the PDF back to Google Drive
        if os.path.exists(pdf_path):
            upload_to_drive(pdf_path)
        else:
            print(f"❌ Error: {pdf_name} not found after download!")
