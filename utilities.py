import cv2
from ultralytics import YOLO
import pytesseract
import os

# Set the Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r'G:\Program Files\Tesseract-OCR\tesseract.exe'

# Load the YOLO model
model_path = os.path.join('.', 'runs', 'detect', 'train', 'weights', 'best.pt')
lpr_model = YOLO(model_path)
threshold = 0.50

# Load the original image
car_image_path = 'Images/car4.jpg'
original_image = cv2.imread(car_image_path)

# Predict on the image using YOLO
results_list = lpr_model(car_image_path)
results = results_list[0]  # Assuming there is only one element in the list

# Iterate through the detected boxes and draw rectangles
for result in results.boxes.data.tolist():
    x1, y1, x2, y2, score, class_id = result

    if score > threshold:
        # Draw rectangle on the original image
        cv2.rectangle(original_image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255), 2)

        # Extract the license plate region
        license_plate_region = original_image[int(y1):int(y2), int(x1):int(x2)]

        try:
            # Preprocess the license plate region
            resized_license_plate = cv2.resize(
                license_plate_region, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

            grayscale_license_plate = cv2.cvtColor(
                resized_license_plate, cv2.COLOR_BGR2GRAY)

            blurred_license_plate = cv2.GaussianBlur(
                grayscale_license_plate, (5, 5), 0)

            _, thresholded_license_plate = cv2.threshold(
                blurred_license_plate, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            morph_image = cv2.morphologyEx(thresholded_license_plate, cv2.MORPH_CLOSE, kernel)

            # Perform OCR on the preprocessed license plate
            config = ('--oem 3 -l eng --psm 6 -c '
                      'tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            ocr_result = pytesseract.image_to_string(morph_image, lang='eng', config=config)

            # Clean up the OCR result
            ocr_result = "".join(ocr_result.split()).replace(":", "").replace("-", "")

            # Add OCR result above the rectangle
            cv2.putText(original_image, f'{ocr_result}', (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            print(f'OCR Result: {ocr_result}')

        except Exception as e:
            print("Error in license recognition:", e)

# Display the image with rectangles and OCR results
cv2.imshow('Original Image with Rectangles and OCR Results', original_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
