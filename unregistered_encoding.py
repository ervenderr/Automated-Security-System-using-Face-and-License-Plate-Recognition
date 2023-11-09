import cv2
import face_recognition
import pickle
import os

from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.icons import Icon


def process_images():
    # Define the folder path where your images are stored
    folderPath = 'Images/unregistered driver'  # Update this to the local folder path
    pathList = os.listdir(folderPath)

    # Initialize lists to store images and associated IDs
    imgList = []
    studentIds = []

    # Iterate through the files in the folder
    for path in pathList:
        # Read the image
        img = cv2.imread(os.path.join(folderPath, path))

        # Append the image to the list
        imgList.append(img)

        # Extract the ID from the file name (assuming file name is the ID)
        studentIds.append(os.path.splitext(path)[0])

    # Function to find face encodings
    def find_encodings(images_list):
        encode_list = []
        for img in images_list:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_encodings = face_recognition.face_encodings(img)

            if len(face_encodings) > 0:
                # If there are face encodings, append the first one to the list
                encode_list.append(face_encodings[0])
            else:
                # Handle the case where no face was detected in the image
                okay = Messagebox.ok("ENCODING ERROR", 'ERROR', icon=Icon.info)

                if okay is None:
                    print("OK CLICKED")

        return encode_list

    try:
        print("Encoding Started ...")
        encodeListKnown = find_encodings(imgList)
        encodeListKnownWithIds = [encodeListKnown, studentIds]
        print("Encoding Complete")

        # Save the encodings to a pickle file
        with open("unregistered_driver.p", 'wb') as file:
            pickle.dump(encodeListKnownWithIds, file)
        print("File Saved")

    except Exception as e:
        print(f"An error occurred during encoding: {str(e)}")

