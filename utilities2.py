# Train multiple images per person
# Find and recognize faces in an image using a SVC with scikit-learn

"""
Structure:
        <test_image>.jpg
        <train_dir>/
            <person_1>/
                <person_1_face-1>.jpg
                <person_1_face-2>.jpg
                .
                .
                <person_1_face-n>.jpg
           <person_2>/
                <person_2_face-1>.jpg
                <person_2_face-2>.jpg
                .
                .
                <person_2_face-n>.jpg
            .
            .
            <person_n>/
                <person_n_face-1>.jpg
                <person_n_face-2>.jpg
                .
                .
                <person_n_face-n>.jpg
"""

import face_recognition
import joblib
from sklearn import svm
import os
import time

# Training the SVC classifier

# The training data would be all the face encodings from all the known images and the labels are their names
encodings = []
names = []

# # Training directory
# train_dir = os.listdir(r'C:\Users\Ervender\PycharmProjects\Thesis-Optimizing-WMSU-Security-System\testing\test_dir')
#
# # Loop through each person in the training directory
# for person in train_dir:
#     pix = os.listdir(r'C:\Users\Ervender\PycharmProjects\Thesis-Optimizing-WMSU-Security-System\testing\test_dir\\' + person)
#
#     # Loop through each training image for the current person
#     for person_img in pix:
#         # Get the face encodings for the face in each image file
#         face = face_recognition.load_image_file(r'C:\Users\Ervender\PycharmProjects\Thesis-Optimizing-WMSU-Security-System\testing\test_dir\\' + person + "/" + person_img)
#         face_bounding_boxes = face_recognition.face_locations(face)
#
#         #If training image contains exactly one face
#         if len(face_bounding_boxes) == 1:
#             face_enc = face_recognition.face_encodings(face)[0]
#             # Add face encoding for current image with corresponding label (name) to the training data
#             encodings.append(face_enc)
#             names.append(person)
#         else:
#             print(person + "/" + person_img + " was skipped and can't be used for training")
#
#
# # Create and train the SVC classifier
# clf = svm.SVC(gamma='scale')
# clf.fit(encodings, names)
#
# joblib.dump(clf, 'trained_classifier.joblib')
clf = joblib.load('trained_classifier.joblib')

start = time.time()

# Load the test image with unknown faces into a numpy array
test_image = face_recognition.load_image_file('testing/test_image.jpg')

# Find all the faces in the test image using the default HOG-based model
face_locations = face_recognition.face_locations(test_image)
no = len(face_locations)
print("Number of faces detected: ", no)

ground_truth_labels = ['Abdullah_Gul']

# Predict all the faces in the test image using the trained classifier
predicted_labels = []
confidence = None
print("Found:")
for i in range(no):
    test_image_enc = face_recognition.face_encodings(test_image)[i]
    name = clf.predict([test_image_enc])
    confidence = clf.decision_function([test_image_enc])
    predicted_labels.append(name[0])
    print(*name)

print(f'confidense: {confidence}')


# Calculate accuracy
correct_predictions = sum([1 for pred, truth in zip(predicted_labels, ground_truth_labels) if pred == truth])
total_predictions = len(ground_truth_labels)
accuracy = (correct_predictions / total_predictions) * 100
end = time.time()
print(accuracy)
print("License plate recognition time: ", end - start)