import gc
import logging
import os
import time

import cv2
import numpy as np
from drive_utils import get_or_create_folder, upload_to_drive

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Path setup
pdf_folder = "main/pdfs"
input_folder = os.path.join(pdf_folder, "Watermark_removed_images_600dpi")
output_folder = os.path.join(pdf_folder, "text_enhanced_images_600dpi")

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Create a folder in Google Drive for enhanced images
enhanced_images_folder_id = get_or_create_folder(
    "Text_Enhanced_Images_600dpi", parent_folder_id=os.getenv("GDRIVE_FOLDER_ID")
)


def enhance_image(image_file, retries=3, delay=2):
    """Enhances text in the image, retries on failure, and uploads if successful."""
    input_image_path = os.path.join(input_folder, image_file)
    output_path = os.path.join(output_folder, image_file)

    for attempt in range(1, retries + 1):
        img = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            logging.warning(f"❌ Failed to load image: {input_image_path}")
            return False  # Skip this image

        logging.info(f"🖼️ Processing Image ({attempt}/{retries}): {image_file}")

        try:
            # Gamma correction
            gamma = 0.6
            inv_gamma = 1.0 / gamma
            table = np.array(
                [((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]
            ).astype("uint8")
            gamma_corrected = cv2.LUT(img, table)

            # Advanced denoising
            denoised = cv2.fastNlMeansDenoising(
                gamma_corrected, h=10, templateWindowSize=11, searchWindowSize=25
            )

            # CLAHE
            clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(16, 16))
            clahe_img = clahe.apply(denoised)

            # Sharpening
            gaussian_blur = cv2.GaussianBlur(clahe_img, (0, 0), 3.0)
            sharpened = cv2.addWeighted(clahe_img, 2.2, gaussian_blur, -1.2, 0)

            # Adaptive thresholding
            binary = cv2.adaptiveThreshold(
                sharpened,
                255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY_INV,
                blockSize=43,
                C=8,
            )

            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            thickened = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=3)
            thickened = cv2.dilate(thickened, kernel, iterations=1)

            # Final noise removal and inversion
            final_img = cv2.medianBlur(thickened, 5)
            final_img = cv2.bitwise_not(final_img)

            # Save processed image
            cv2.imwrite(output_path, final_img, [cv2.IMWRITE_PNG_COMPRESSION, 8])

            logging.info(f"✅ Saved Enhanced Image: {image_file}")

            # Upload to Google Drive
            upload_to_drive(output_path, folder_name="Text_Enhanced_Images_600dpi")

            return True  # Success

        except Exception as e:
            logging.error(
                f"🔥 Error processing {image_file} (Attempt {attempt}): {str(e)}"
            )
            time.sleep(delay)  # Wait before retrying

        finally:
            # Memory cleanup
            del (
                img,
                gamma_corrected,
                denoised,
                clahe_img,
                sharpened,
                binary,
                thickened,
                final_img,
            )
            gc.collect()

    logging.error(f"❌ Skipping {image_file} after {retries} failed attempts.")
    return False  # Skip this image after multiple failures


if __name__ == "__main__":
    image_files = sorted(
        [
            f
            for f in os.listdir(input_folder)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
    )

    if image_files:
        logging.info(f"📂 Found {len(image_files)} images. Processing one by one...")

        for image in image_files:
            success = enhance_image(image)

            if not success:
                logging.warning(f"⚠️ Skipped {image} after retries.")

            time.sleep(1)  # Small delay before processing the next image

        logging.info(
            f"🎉 Enhancement complete! Results saved to {output_folder} and uploaded."
        )
    else:
        logging.warning("⚠️ No images found in input directory.")
