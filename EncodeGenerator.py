import cv2
import face_recognition
import pickle
import os
from PIL import Image, ImageTk
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from database import *


def process_encodings():
    # Fetch the list of file paths in the Firebase Storage bucket
    bucket = storage.bucket()
    blobs = bucket.list_blobs(prefix="driver images/")
    path_list = [blob.name.split("/")[-1] for blob in blobs if blob.name.endswith(".jpg") or blob.name.endswith(".png")]

    img_list = []
    driver_ids = []

    for path in path_list:
        blob = bucket.blob(f"driver images/{path}")
        image_data = blob.download_as_bytes()

        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

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

    file = open("registered_encode_file.p", 'wb')
    pickle.dump(encode_with_ids, file)
    file.close()
    print("file saved")
