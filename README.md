# Automated Security System using Face and License Plate Recognition 🚀

## Overview 📖

This project is an Automated Security System designed to enhance security by integrating face recognition and automatic license plate recognition (ALPR). The system captures and processes images to identify authorized individuals and vehicles, making it ideal for environments such as universities.

![image](https://github.com/ervenderr/Automated-Security-System-using-Face-and-License-Plate-Recognition/assets/81071981/a2f2d39b-b116-41a2-88c9-2fcb44eb52ac)

## Features ✨

- **Face Recognition**: Utilizes the `face_recognition` library for identifying authorized personnel.
- **License Plate Recognition**: Implements YOLOv8 for object detection and Tesseract OCR for extracting license plate information.
- **GUI Interface**: Built using Tkinter for easy interaction and monitoring.
- **CRUD**: Drivers and Vehicles management system.

## Usage 🚀

1. **Run the system**:
    ```sh
    python ui.py
    ```

2. **Interface**:
    - The GUI will launch, providing options to start face recognition and license plate recognition.
    - Ensure your webcam is connected for live capture.

3. **Adding Authorized Personnel**:
    - Add images of authorized personnel in the `known_faces` directory.
    - Ensure the images are named appropriately (e.g., `name.jpg`).

4. **Monitoring**:
    - The system will display live feed and highlight recognized faces and license plates.
    - Unrecognized faces and plates will trigger alerts.

## Acknowledgments 🙏

- The `face_recognition` library for easy face detection and recognition.
- The YOLOv8 model for robust object detection.
- Tesseract OCR for reliable text extraction.
