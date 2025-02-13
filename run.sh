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
echo "✂️ Splitting PDFs..."
python main/split_pdf.py

echo "✅ Workflow completed!"

