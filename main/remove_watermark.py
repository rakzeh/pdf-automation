import os

import cv2
import numpy as np
from drive_utils import create_folder_in_drive, upload_to_drive
from skimage import io

# Define input and output folders
pdf_folder = "main/pdfs"
input_folder = os.path.join(pdf_folder, "converted_images_600dpi")
output_folder = os.path.join(pdf_folder, "Watermark_removed_images_600dpi")

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)
print(f"📂 Created output directory: {output_folder}")


# Pixel selection function (Detects watermark pixels)
def select_watermark_pixel(r, g, b):
    """Detects watermark pixels by checking their color range."""
    return 150 <= r <= 255 and 150 <= g <= 255 and 150 <= b <= 255


# Image processing function (Removes watermark)
def remove_watermark(imgs):
    """Convert watermark pixels to pure white (255,255,255)."""
    height, width, _ = imgs.shape
    changed_pixels = 0
    for i in range(height):
        for j in range(width):
            if select_watermark_pixel(imgs[i][j][0], imgs[i][j][1], imgs[i][j][2]):
                imgs[i][j][0] = imgs[i][j][1] = imgs[i][j][2] = (
                    255  # Convert to pure white
                )
                changed_pixels += 1
    print(f"✅ Modified {changed_pixels} watermark pixels.")
    return imgs


# Process each image from the input folder
image_files = sorted(
    [f for f in os.listdir(input_folder) if f.endswith((".png", ".jpg", ".jpeg"))]
)

if image_files:
    print(f"📷 Found {len(image_files)} images in: {input_folder}")

    # Create a subfolder in Google Drive for cleaned images
    watermark_removed_folder_id = create_folder_in_drive(
        "Watermark_Removed_Images", parent_folder_id=os.getenv("GDRIVE_FOLDER_ID")
    )

    # Process each image to remove watermark
    for image_file in image_files:
        input_image_path = os.path.join(input_folder, image_file)

        # Read the image
        img = cv2.imread(input_image_path)
        if img is None:
            print(f"⚠️ Failed to load: {input_image_path}")
            continue

        # Remove watermark
        img_np = remove_watermark(img)

        # Save cleaned image
        cleaned_image_path = os.path.join(output_folder, image_file)
        io.imsave(cleaned_image_path, img_np)
        print(f"✅ Processed & saved: {cleaned_image_path}")

        # Upload to Google Drive
        upload_to_drive(
            cleaned_image_path, parent_folder_id=watermark_removed_folder_id
        )

    print(f"🎉 Watermark removal complete! Images uploaded to Google Drive.")
else:
    print(f"⚠️ No images found in: {input_folder}")
