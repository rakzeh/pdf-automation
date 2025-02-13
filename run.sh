#!/bin/bash

# Exit script on error
set -e

echo "🚀 Starting PDF Sync and Processing Workflow..."

# Step 1: Activate virtual environment (if you use one)
# source venv/bin/activate

# Step 2: Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Step 3: Download PDFs from Google Drive
echo "📥 Downloading PDFs from Google Drive..."
python main/drive_to_github.py

# Step 4: Split PDFs
echo "✂️📄✂️ Splitting PDFs..."
python main/split_pdf.py


# Step 5: Remove Watermark 
echo "🧼 Removing Watermark From Images..."
python main/remove_watermark.py

# Step 6: Text Enhancement
echo "🔍 Enhancing text in images..."
python main/text_enhancement.py

# Step 7: Doing Ocr 
echo "Ocr ... "
bash ocr.sh

# Step 8: Combine Ocr Done Pdf's
 echo "Combining Ocr Done Pdfs"
 python main/combine_ocr_pdf.py

# Step 9: Numbering to the pdf's 
#

# Step 10: Upload it to drive (Done)


echo "✅ Workflow completed!"

