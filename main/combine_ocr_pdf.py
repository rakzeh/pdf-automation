import os

import fitz  # PyMuPDF
from drive_utils import upload_to_drive  # Import upload function

# Define folder containing PDFs
pdf_folder = "main/pdfs/pdfs_output"
output_pdf = os.path.join(pdf_folder, "percentage.pdf")


# Function to extract page number safely
def extract_page_number(filename):
    parts = filename.split("_")
    try:
        return int(parts[-1].split(".")[0])  # Extract number if available
    except ValueError:
        return float("inf")  # If no number, place at the end


# Get and sort input PDFs **excluding** percentage.pdf
pdf_files = sorted(
    [f for f in os.listdir(pdf_folder) if f.endswith(".pdf") and f != "percentage.pdf"],
    key=extract_page_number,
)

if not pdf_files:
    print("⚠️ No valid PDF files found for merging.")
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

# Upload the final merged PDF to Google Drive
uploaded_pdf_id = upload_to_drive(output_pdf, folder_name="Merged_PDFs")

if uploaded_pdf_id:
    print(f"🚀 Uploaded merged PDF to Google Drive: {uploaded_pdf_id}")
else:
    print("❌ Failed to upload merged PDF.")
