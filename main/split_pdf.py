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


import os
import sys

from drive_utils import upload_to_drive
from pdf2image import convert_from_path

# Define input and output folders
pdf_folder = "main/pdfs"
final_output_pdf = os.path.join(pdf_folder, "demo.pdf")
output_folder = os.path.join(pdf_folder, "converted_images_600dpi")

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Define Google Drive folder for structured uploads
drive_folder_name = "Converted_Images_600DPI"

# Check if the input PDF exists before processing
if not os.path.exists(final_output_pdf):
    print(
        f"❌ ERROR: The file '{final_output_pdf}' was not found! Please check the file path."
    )
    sys.exit(1)

try:
    print(f"✂️📄✂️ Splitting PDF '{final_output_pdf}' into images at 600 DPI...")

    # Convert PDF pages to images
    images = convert_from_path(final_output_pdf, dpi=600)

    if not images:
        raise ValueError(
            "❌ ERROR: No images were generated from the PDF. Conversion might have failed."
        )

    print(f"✅ Successfully converted {len(images)} pages to images.")

    # Process each converted page
    for i, image in enumerate(images):
        try:
            image_name = f"final_output_page_{i+1}.png"
            image_path = os.path.join(output_folder, image_name)

            # Save image
            image.save(image_path, "PNG")
            print(f"📄 Page {i+1} saved as '{image_name}'")

            # Upload to Google Drive
            upload_to_drive(image_path, folder_name=drive_folder_name)
            print(
                f"📤 Uploaded '{image_name}' to Google Drive folder '{drive_folder_name}'"
            )

        except Exception as e:
            print(f"⚠️ ERROR: Failed to process Page {i+1}. Reason: {e}")

    print("🎉 All pages converted and uploaded successfully!")

except FileNotFoundError:
    print(
        "❌ ERROR: Poppler is not installed or not found. Install it using: 'sudo apt install poppler-utils'"
    )
    sys.exit(1)

except ValueError as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)

except Exception as e:
    print(f"❌ ERROR: An unexpected error occurred - {e}")
    sys.exit(1)
