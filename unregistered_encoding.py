import cv2
import face_recognition_process
import pickle
import os


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
            encode = face_recognition.face_encodings(img)[0]
            encode_list.append(encode)

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


