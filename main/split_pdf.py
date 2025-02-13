import os

from pdf2image import convert_from_path

from drive_utils import upload_to_drive

# Define input and output folders
pdf_folder = "main/pdfs"
final_output_pdf = os.path.join(pdf_folder, "demo.pdf")
output_folder = os.path.join(pdf_folder, "converted_images_600dpi")

# Ensure output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Convert PDF to images at 600 DPI
images = convert_from_path(final_output_pdf, dpi=600)

# Define systematic folder name in Google Drive
drive_folder_name = "Converted_Images_600DPI"

# Save and upload each image
for i, image in enumerate(images):
    image_name = f"final_output_page_{i+1}.png"
    image_path = os.path.join(output_folder, image_name)
    image.save(image_path, "PNG")

    print(f"✅ Page {i+1} saved as {image_name}")

    # Upload image to structured Google Drive folder
    upload_to_drive(image_path, folder_name=drive_folder_name)

print("🎉 PDF converted and uploaded systematically to Drive!")
