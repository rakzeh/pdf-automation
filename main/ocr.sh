#!/bin/bash

# Define directories
input_dir="main/pdfs/text_enhanced_images_600dpi"      # Folder containing enhanced images
output_dir="main/pdfs/pdfs_output"        # Folder to store the output PDFs

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# Languages for OCR
langs="eng+hin"

# Set image DPI for OCRmyPDF
image_dpi=600

# Loop through all images in the enhance_images folder
for img in "$input_dir"/*.{png,jpg,jpeg}; do
    # Check if the image file exists and is not a directory
    if [ -f "$img" ]; then
        # Get the filename without extension
        filename=$(basename "$img" | sed 's/\(.*\)\..*/\1/')

        # Define the output PDF path (same name as the image)
        output_pdf="$output_dir/${filename}.pdf"

        echo "Processing $img..."

        # Use OCRmyPDF to convert the image to a PDF with OCR
        ocrmypdf -l "$langs" --image-dpi "$image_dpi" --clean "$img" "$output_pdf"

        # Check if the conversion was successful
        if [ $? -eq 0 ]; then
            echo "Successfully converted $img to $output_pdf"
        else
            echo "Error processing $img"
        fi
    else
        echo "Skipping $img (not a valid image file)"
    fi
done

echo "All images have been processed."

