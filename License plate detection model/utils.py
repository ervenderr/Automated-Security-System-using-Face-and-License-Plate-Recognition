import cv2
import easyocr

# Load the OCR model
reader = easyocr.Reader(['en'])

# Load and preprocess the image
image = cv2.imread("license_plate_regions/best_license_plate.jpg")

# Perform OCR on the image
results = reader.readtext(image)

# Extract and print the recognized text
plate_num = ""
for (bbox, text, prob) in results:
    plate_num += text + ' '

print("Extracted Text:", plate_num)
