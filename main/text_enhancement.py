import gc
import logging
import multiprocessing as mp
import os

import cv2
import numpy as np
from drive_utils import create_folder_in_drive, upload_to_drive

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


def enhance_image(image_file):
    """Enhances text in the image by applying contrast adjustment, denoising, sharpening, and binarization."""
    input_image_path = os.path.join(input_folder, image_file)
    img = cv2.imread(
        input_image_path, cv2.IMREAD_GRAYSCALE
    )  # Load directly in grayscale
    if img is None:
        logging.warning(f"❌ Failed to load image: {input_image_path}")
        return

    filename = os.path.basename(input_image_path)
    logging.info(f"🖼️ Processing Image: {filename}")

    try:
        # Gamma correction for contrast enhancement
        gamma = 0.6
        inv_gamma = 1.0 / gamma
        table = np.array(
            [((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]
        ).astype("uint8")
        gamma_corrected = cv2.LUT(img, table)

        # Advanced denoising
        denoised = cv2.fastNlMeansDenoising(
            gamma_corrected,
            h=10,  # Increased filter strength
            templateWindowSize=11,
            searchWindowSize=25,
        )

        # Contrast Limited Adaptive Histogram Equalization (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(16, 16))
        clahe_img = clahe.apply(denoised)

        # Sharpening using unsharp masking
        gaussian_blur = cv2.GaussianBlur(clahe_img, (0, 0), 3.0)
        sharpened = cv2.addWeighted(clahe_img, 2.2, gaussian_blur, -1.2, 0)

        # Adaptive thresholding for binarization
        binary = cv2.adaptiveThreshold(
            sharpened,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV,
            blockSize=43,  # Larger block size for better local adaptation
            C=8,
        )

        # Morphological operations for text thickening
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        thickened = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=3)
        thickened = cv2.dilate(thickened, kernel, iterations=1)

        # Final noise removal and inversion
        final_img = cv2.medianBlur(thickened, 5)
        final_img = cv2.bitwise_not(final_img)

        # Save processed image
        output_path = os.path.join(
            output_folder, os.path.splitext(filename)[0] + ".png"
        )
        cv2.imwrite(output_path, final_img, [cv2.IMWRITE_PNG_COMPRESSION, 8])

        logging.info(f"✅ Saved Enhanced Image: {filename}")

        # Upload processed image to Google Drive
        upload_to_drive(output_path, parent_folder_id=enhanced_images_folder_id)

    except Exception as e:
        logging.error(f"🔥 Error processing {filename}: {str(e)}")

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


if __name__ == "__main__":
    image_files = [
        f
        for f in os.listdir(input_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    if image_files:
        logging.info(
            f"📂 Found {len(image_files)} images. Processing with {mp.cpu_count()//2} cores..."
        )

        # Create a folder in Google Drive for the enhanced images
        enhanced_images_folder_id = create_folder_in_drive(
            "Text_Enhanced_Images_600dpi",
            parent_folder_id=os.getenv("GDRIVE_FOLDER_ID"),
        )

        # Process images using multiprocessing
        with mp.Pool(processes=mp.cpu_count() // 2) as pool:
            pool.map(enhance_image, image_files)

        logging.info(
            f"🎉 Enhancement complete! Results saved to {output_folder} and uploaded to Google Drive."
        )
    else:
        logging.warning("⚠️ No images found in input directory.")
