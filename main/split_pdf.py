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
from pdf2image import PDFInfoNotInstalledError, convert_from_path

# Define input and output folders
pdf_folder = "main/pdfs"
final_output_pdf = os.path.join(pdf_folder, "demo.pdf")
output_folder = os.path.join(pdf_folder, "converted_images_600dpi")

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Define systematic folder name in Google Drive
drive_folder_name = "Converted_Images_600DPI"

# Check if the input PDF exists
if not os.path.exists(final_output_pdf):
    print(
        f"❌ ERROR: The file '{final_output_pdf}' does not exist. Please check the path."
    )
    sys.exit(1)

try:
    # Convert PDF to images at 600 DPI
    print(f"🔄 Converting '{final_output_pdf}' to images at 600 DPI...")
    images = convert_from_path(final_output_pdf, dpi=600)

    if not images:
        raise ValueError(
            "❌ ERROR: No images were generated from the PDF. Conversion might have failed."
        )

    # Save and upload each image
    for i, image in enumerate(images):
        try:
            image_name = f"final_output_page_{i+1}.png"
            image_path = os.path.join(output_folder, image_name)

            image.save(image_path, "PNG")
            print(f"✅ Page {i+1} saved as '{image_name}'")

            # Upload image to structured Google Drive folder
            upload_to_drive(image_path, folder_name=drive_folder_name)
            print(
                f"📤 Uploaded '{image_name}' to Google Drive folder '{drive_folder_name}'"
            )

        except Exception as e:
            print(f"⚠️ ERROR: Failed to process Page {i+1}. Reason: {e}")

    print("🎉 PDF converted and uploaded systematically to Drive!")

except PDFInfoNotInstalledError:
    print(
        "❌ ERROR: pdf2image requires Poppler to be installed. Install it via 'sudo apt install poppler-utils'."
    )
    sys.exit(1)

except FileNotFoundError as e:
    print(f"❌ ERROR: File not found - {e}")
    sys.exit(1)

except ValueError as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)

except Exception as e:
    print(f"❌ ERROR: Unexpected error occurred: {e}")
    sys.exit(1)
