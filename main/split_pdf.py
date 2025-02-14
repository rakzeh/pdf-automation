# import os
#
# from pdf2image import convert_from_path
#
# from drive_utils import upload_to_drive
#
# # Define input and output folders
# pdf_folder = "main/pdfs"
# final_output_pdf = os.path.join(pdf_folder, "demo.pdf")
# output_folder = os.path.join(pdf_folder, "converted_images_600dpi")
#
# # Ensure output folder exists
# if not os.path.exists(output_folder):
#     os.makedirs(output_folder)
#
# # Convert PDF to images at 600 DPI
# images = convert_from_path(final_output_pdf, dpi=600)
#
# # Define systematic folder name in Google Drive
# drive_folder_name = "Converted_Images_600DPI"
#
# # Save and upload each image
# for i, image in enumerate(images):
#     image_name = f"final_output_page_{i+1}.png"
#     image_path = os.path.join(output_folder, image_name)
#     image.save(image_path, "PNG")
#
#     print(f"✅ Page {i+1} saved as {image_name}")
#
#     # Upload image to structured Google Drive folder
#     upload_to_drive(image_path, folder_name=drive_folder_name)
#
# print("🎉 PDF converted and uploaded systematically to Drive!")

import gc
import os
import time

from drive_utils import upload_to_drive
from pdf2image import convert_from_path
from pdf2image.pdf2image import pdfinfo_from_path

# Define input and output folders
pdf_folder = "main/pdfs"
final_output_pdf = os.path.join(pdf_folder, "demo.pdf")
output_folder = os.path.join(pdf_folder, "converted_images_600dpi")
os.makedirs(output_folder, exist_ok=True)

# Get total number of pages
total_pages = pdfinfo_from_path(final_output_pdf)["Pages"]

# Define Google Drive folder for structured uploads
drive_folder_name = "Converted_Images_600DPI"

# Process and upload each page one at a time
for page_number in range(1, total_pages + 1):
    try:
        images = convert_from_path(
            final_output_pdf, dpi=600, first_page=page_number, last_page=page_number
        )
        image = images[0]  # Process only 1 page at a time

        image_name = f"final_output_page_{page_number}.png"
        image_path = os.path.join(output_folder, image_name)

        # Save the image
        image.save(image_path, "PNG")
        print(f"✅ Page {page_number} saved as {image_name}")

        # Prevent duplicate uploads
        if not os.path.exists(image_path):
            time.sleep(5)  # Small delay before upload
            upload_to_drive(image_path, folder_name=drive_folder_name)
            print(f"📤 Uploaded '{image_name}' to Google Drive")
        else:
            print(f"⚠️ Skipping duplicate upload for '{image_name}'")

        # Free memory immediately
        del image
        gc.collect()

        # Prevent GitHub Actions timeout issues
        time.sleep(10)

    except Exception as e:
        print(f"⚠️ ERROR: Could not process Page {page_number}. Reason: {e}")

print("🎉 PDF converted and uploaded systematically to Drive!")
