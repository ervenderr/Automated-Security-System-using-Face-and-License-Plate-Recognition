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


def fetch_logs():
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()
    c.execute('SELECT name, id_number, plate_number, phone, date, time_in, time_out FROM daily_logs ORDER BY date DESC')
    data_logs = c.fetchall()
    conn.close()
    return data_logs


def insert_logs(name, id_number, plate_number, phone, date, time_in, time_out, time_in_status, is_registered):
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()
    c.execute('INSERT INTO daily_logs (name, id_number, plate_number, phone, date, time_in, time_out, time_in_status,'
              'is_registered)'
              'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
              (name, id_number, plate_number, phone, date, time_in, time_out, time_in_status, is_registered))

    conn.commit()
    conn.close()




# # Connect to the SQLite database
# conn = sqlite3.connect('drivers.db')
# c = conn.cursor()
#
# # Delete all rows from the "daily_logs" table
# c.execute('DELETE FROM daily_logs')
#
# # Commit the changes
# conn.commit()
#
# # Close the database connection
# conn.close()