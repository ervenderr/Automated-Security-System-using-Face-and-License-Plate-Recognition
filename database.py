# database.py
import pyrebase
import firebase_admin
from firebase_admin import credentials, storage
import sqlite3

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': "wmsusecuritysystem.appspot.com",
})


firebaseConfig = {
  "apiKey": "AIzaSyACVRQD5XtQO75PbK0zgPHMpOIZK8AuYAI",
  "authDomain": "wmsusecuritysystem.firebaseapp.com",
  "databaseURL": "https://wmsusecuritysystem-default-rtdb.firebaseio.com",
  "projectId": "wmsusecuritysystem",
  "storageBucket": "wmsusecuritysystem.appspot.com",
  "messagingSenderId": "921680387635",
  "appId": "1:921680387635:web:c60c3daf091597e4d54d46",
  "measurementId": "G-DWPB6BJQZC"}

firebase = pyrebase.initialize_app(firebaseConfig)

pyre_storage = firebase.storage()
db = firebase.database()

# plate = "NBC1234"
# ids = '01853'
# plate_number = None
#
# driver_info = db.child(f'Drivers/{ids}').get().val()
# vehicle_data = db.child('Vehicles').get().val()
#
# if vehicle_data is not None:
#     for plate, vehicle_info in vehicle_data.items():
#         drivers = vehicle_info.get('drivers', {})
#         if str(ids) in drivers:
#             plate_number = vehicle_info['plate_number']
#             break
#
#
# if plate_number is not None:
#     print(f"The plate number associated with id_number {ids} is: {plate_number}")
# else:
#     print(f"No plate number found for id_number {ids}")

conn = sqlite3.connect('drivers.db')
c = conn.cursor()
# c.execute("SELECT * FROM daily_logs")
print(c.fetchall())
conn.commit()


