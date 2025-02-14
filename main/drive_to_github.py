# import os
#
# from drive_utils import download_from_drive, upload_to_drive
#
# # 📂 Define folder for storing PDFs
# PDF_DIR = "main/pdfs"
#
# # List of PDFs to download and re-upload
# PDF_NAMES = ["demo.pdf"]  # Add more names if needed
#
# if __name__ == "__main__":
#     for pdf_name in PDF_NAMES:
#         # Download the PDF from Google Drive
#         download_from_drive(pdf_name)
#
#         # Path of the downloaded PDF
#         pdf_path = os.path.join(PDF_DIR, pdf_name)
#
#         # Upload the PDF back to Google Drive
#         if os.path.exists(pdf_path):
#             upload_to_drive(pdf_path)
#         else:
#             print(f"❌ Error: {pdf_name} not found after download!")

import os
import time

from drive_utils import download_from_drive, upload_to_drive

# 📂 Define folder for storing PDFs
PDF_DIR = "main/pdfs"
os.makedirs(PDF_DIR, exist_ok=True)  # Ensure the directory exists

# 📄 List of PDFs to download and re-upload
PDF_NAMES = ["demo.pdf"]  # Add more names if needed

if __name__ == "__main__":
    for pdf_name in PDF_NAMES:
        print(f"🔄 Processing {pdf_name}...")

        # Step 1: Download the PDF from Google Drive
        download_from_drive(pdf_name)

        # Path of the downloaded PDF
        pdf_path = os.path.join(PDF_DIR, pdf_name)

        # Wait for the file to appear (handling potential delays)
        for _ in range(10):  # Retry for up to 10 seconds
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                break
            print(f"⏳ Waiting for {pdf_name} to appear...")
            time.sleep(1)

        # Step 2: Upload the PDF back to Google Drive
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            upload_to_drive(pdf_path)
            print(f"✅ Successfully processed {pdf_name}\n")
        else:
            print(f"❌ Error: {pdf_name} not found or empty after download!\n")
