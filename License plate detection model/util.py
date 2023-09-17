import os
import cv2
from ultralytics import YOLO
import pytesseract
from PIL import Image
import easyocr

# Load the YOLO model
model_path = os.path.join('.', 'runs', 'detect', 'train', 'weights', 'last.pt')
model = YOLO(model_path)

reader = easyocr.Reader(['en'])

# Set up camera capture
cap = cv2.VideoCapture(0)  # Use camera index 0 (default webcam)

# Define a threshold for object detection confidence
detection_threshold = 0.5

# Directory to save detected frames
output_dir = 'detected_frames'
os.makedirs(output_dir, exist_ok=True)

# Initialize pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Maximum number of saved frames
max_saved_frames = 5
saved_frames = []

license_plate_dir = 'license_plate_regions'
os.makedirs(license_plate_dir, exist_ok=True)

threshold = 0.5
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Perform object detection
    results = model(frame)[0]
    object_detected = False  # Flag to track if any object was detected in the frame

    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result

        if score > threshold:
            object_detected = True  # Set the flag to True for valid detection
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)

            # Extract the license plate region
            license_plate_region = frame[int(y1):int(y2), int(x1):int(x2)]

            # Preprocess the license plate region for better OCR accuracy
            gray_plate = cv2.cvtColor(license_plate_region, cv2.COLOR_BGR2GRAY)
            blurred_plate = cv2.GaussianBlur(gray_plate, (5, 5), 0)
            threshold_plate = cv2.adaptiveThreshold(blurred_plate, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                    cv2.THRESH_BINARY_INV, 11, 2)

            # Convert BGR to RGB for EasyOCR
            license_plate_rgb = cv2.cvtColor(threshold_plate, cv2.COLOR_GRAY2RGB)

            # Perform OCR on the license plate region using EasyOCR
            ocr_results = reader.readtext(license_plate_rgb)

            # Extracted text from EasyOCR
            extracted_text = ' '.join([result[1] for result in ocr_results])

            # Display the extracted text
            cv2.putText(frame, extracted_text, (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

    # Save the frame if an object was detected
    if object_detected:
        if len(saved_frames) >= max_saved_frames:
            oldest_frame = saved_frames.pop(0)
            # os.remove(oldest_frame)  # Delete the oldest saved frame

        frame_filename = os.path.join(output_dir, f"detected_frame_{len(saved_frames):04d}.jpg")
        cv2.imwrite(frame_filename, frame)
        saved_frames.append(frame_filename)
        print(f"Saved detected frame: {frame_filename}")

        # Save the license plate region
        license_plate_filename = os.path.join(license_plate_dir, f"license_plate_{len(saved_frames):04d}.jpg")
        cv2.imwrite(license_plate_filename, license_plate_region)
        print(f"Saved license plate region: {license_plate_filename}")

    # Display the frame
    cv2.imshow('Object Detection', frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()