import os

from pdf2image import convert_from_path

# Define the folder paths /content/demo.pdf
pdf_folder = "main/pdfs"
final_output_pdf = os.path.join(pdf_folder, "demo.pdf")

# Output folder for images
output_folder = os.path.join(pdf_folder, "converted_images_600dpi")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Convert PDF to images at 600 DPI
images = convert_from_path(final_output_pdf, dpi=600)

# Save images with sequential naming based on the page number
for i, image in enumerate(images):
    image_name = f"final_output_page_{i+1}.png"
    image_path = os.path.join(output_folder, image_name)
    image.save(image_path, "PNG")
    print(f"Page {i+1} saved as {image_name}")

print("PDF converted to images successfully!")
