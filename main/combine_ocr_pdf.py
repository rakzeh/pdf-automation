import os

import fitz  # PyMuPDF
from drive_utils import upload_to_drive  # Import upload function

# Define folder containing PDFs
pdf_folder = "main/pdfs/pdfs_output"
output_pdf = os.path.join(pdf_folder, "percentage.pdf")

# Get a sorted list of PDF files based on page numbers
pdf_files = sorted(
    [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")],
    key=lambda x: int(x.split("_")[-1].split(".")[0]),
)

if not pdf_files:
    print("⚠️ No PDF files found in the directory.")
    exit()

print(f"📄 Merging {len(pdf_files)} PDFs in order...")

# Create a new PDF document
merged_pdf = fitz.open()

for pdf in pdf_files:
    pdf_path = os.path.join(pdf_folder, pdf)
    doc = fitz.open(pdf_path)
    merged_pdf.insert_pdf(doc)
    doc.close()

# Save the merged PDF
merged_pdf.save(output_pdf)
merged_pdf.close()

print(f"✅ Merged PDF saved as: {output_pdf}")

# Upload to Google Drive
uploaded_pdf_id = upload_to_drive(
    output_pdf, parent_folder_id=os.getenv("GDRIVE_FOLDER_ID")
)

if uploaded_pdf_id:
    print(f"🚀 Uploaded merged PDF to Google Drive: {uploaded_pdf_id}")
else:
    print("❌ Failed to upload merged PDF.")
