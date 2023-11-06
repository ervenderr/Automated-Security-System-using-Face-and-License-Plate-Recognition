# database.py
import datetime

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

def fetch_driver_vehicle():
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Define an SQL query to fetch the required data
    query = '''
    SELECT Drivers.id_number, Drivers.name, Drivers.phone,
           Vehicles.plate_number, Vehicles.vehicle_color, Vehicles.vehicle_type
    FROM Drivers
    JOIN DriverVehicleAssociation ON Drivers.id = DriverVehicleAssociation.driver_id
    JOIN Vehicles ON DriverVehicleAssociation.vehicle_id = Vehicles.id
    '''
    c.execute(query)
    data_logs = c.fetchall()
    conn.close()
    return data_logs


def fetch_all_logs():
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Fetch data from daily_logs, drivers, and vehicles tables
    c.execute('''
        SELECT d.name, d.type, dl.id_number, dl.plate_number, d.phone, dl.date, dl.time_in
        FROM daily_logs dl
        JOIN drivers d ON dl.id_number = d.id_number
        JOIN vehicles v ON dl.plate_number = v.plate_number
        ORDER BY time(dl.time_in) DESC
    ''')

    data_logs = c.fetchall()
    conn.close()
    return data_logs


def fetch_daily_logs():
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Get today's date as a string
    today = datetime.date.today().strftime('%Y-%m-%d')

    # Fetch data from daily_logs, drivers, and vehicles tables
    c.execute('''
        SELECT d.name, d.type, dl.id_number, dl.plate_number, d.phone, dl.date, dl.time_in
        FROM daily_logs dl
        JOIN drivers d ON dl.id_number = d.id_number
        JOIN vehicles v ON dl.plate_number = v.plate_number
        WHERE dl.date = ?
        ORDER BY time(dl.time_in) DESC
    ''', (today,))

    data_logs = c.fetchall()
    conn.close()
    return data_logs


def check_extracted_text_for_today(extracted_text):
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    today = datetime.datetime.now().date()
    c.execute('SELECT * FROM daily_logs WHERE plate_number=? AND is_registered=?',
              (extracted_text, 1))

    result = c.fetchone()
    conn.close()

    return result is not None


def insert_logs(name, type, id_number, plate_number, phone, date, time_in, time_out, time_in_status, is_registered):
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()
    c.execute('INSERT INTO daily_logs (name, type, id_number, plate_number, phone, date, time_in, time_out, '
              'time_in_status,'
              'is_registered)'
              'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
              (name, type, id_number, plate_number, phone, date, time_in, time_out, time_in_status, is_registered))

    conn.commit()
    conn.close()


def fetch_drivers_data(plate_number):
    # Connect to the SQLite database
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Query the "drivers" table to retrieve data for drivers authorized for the specified vehicle
    c.execute('''
        SELECT d.name, d.type, d.id_number, d.phone
        FROM drivers d
        JOIN driver_vehicle dv ON d.id_number = dv.driver_id
        WHERE dv.plate_number = ?
    ''', (plate_number,))

    drivers_data = c.fetchall()

    # Close the database connection
    conn.close()

    return drivers_data

def fetch_vehicles_data(id_number):

    # Connect to the SQLite database
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Query the "vehicles" table to retrieve vehicles associated with the specified driver
    c.execute('''
        SELECT v.plate_number, v.vehicle_type, v.vehicle_color
        FROM vehicles v
        JOIN driver_vehicle dv ON v.plate_number = dv.plate_number
        WHERE dv.driver_id = ?
    ''', (id_number,))

    vehicles_data = c.fetchall()

    # Close the database connection
    conn.close()

    return vehicles_data





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