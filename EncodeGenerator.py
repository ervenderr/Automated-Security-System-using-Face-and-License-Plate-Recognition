import cv2
import face_recognition
import pickle
import os


def process_encodings():
    # Assuming your local storage path is "Images/registered driver"
    local_storage_path = "Images/registered driver"

    # Fetch the list of file paths in the local storage directory
    path_list = [file for file in os.listdir(local_storage_path) if file.endswith(".jpg") or file.endswith(".png")]

    img_list = []
    driver_ids = []

    for path in path_list:
        image_path = os.path.join(local_storage_path, path)

        img = cv2.imread(image_path)
        img_list.append(img)
        driver_ids.append(os.path.splitext(path)[0])

    def find_encodings(img_list):
        encode_list = []

        for img in img_list:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            encode = face_recognition.face_encodings(img)[0]
            encode_list.append(encode)

        return encode_list

    encode_list_known = find_encodings(img_list)
    encode_with_ids = [encode_list_known, driver_ids]
    print("complete")

    file_path = "registered_encode_file.p"
    with open(file_path, 'wb') as file:
        pickle.dump(encode_with_ids, file)

    print(f"File saved to {file_path}")


