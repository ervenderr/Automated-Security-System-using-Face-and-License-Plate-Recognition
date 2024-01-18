# database.py
import datetime
import sqlite3
from prettytable import PrettyTable
import pytz


# cred = credentials.Certificate("serviceAccountKey.json")
# firebase_admin.initialize_app(cred, {
#     'storageBucket': "wmsusecuritysystem.appspot.com",
# })
#
# firebaseConfig = {
#     "apiKey": "AIzaSyACVRQD5XtQO75PbK0zgPHMpOIZK8AuYAI",
#     "authDomain": "wmsusecuritysystem.firebaseapp.com",
#     "databaseURL": "https://wmsusecuritysystem-default-rtdb.firebaseio.com",
#     "projectId": "wmsusecuritysystem",
#     "storageBucket": "wmsusecuritysystem.appspot.com",
#     "messagingSenderId": "921680387635",
#     "appId": "1:921680387635:web:c60c3daf091597e4d54d46",
#     "measurementId": "G-DWPB6BJQZC"}
#
# firebase = pyrebase.initialize_app(firebaseConfig)
#
# pyre_storage = firebase.storage()
# db = firebase.database()


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

def fetch_drivers_and_vehicles():
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # SQL query to fetch driver information and associated vehicles
    c.execute('''
        SELECT d.name, d.type, d.id_number, d.phone, GROUP_CONCAT(v.plate_number, ', ') AS authorized_vehicles, d.date
        FROM drivers d
        JOIN driver_vehicle dv ON d.id_number = dv.driver_id
        JOIN vehicles v ON dv.plate_number = v.plate_number
        GROUP BY d.id_number
    ''')

    drivers_and_vehicles_data = c.fetchall()

    conn.close()

    return drivers_and_vehicles_data


def fetch_all_logs():
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Fetch data from daily_logs, drivers, and vehicles tables
    c.execute('''
        SELECT 
            COALESCE(d.name, 'Visitor_' || dl.plate_number) AS name,
            COALESCE(d.type, 'Visitor') AS type,
            dl.id_number,
            d.phone,
            dl.plate_number,
            dl.date,
            dl.time_in,
            dl.time_out
        FROM daily_logs dl
        LEFT JOIN drivers d ON dl.id_number = d.id_number
        LEFT JOIN vehicles v ON dl.plate_number = v.plate_number
        ORDER BY dl.date DESC, time(dl.time_in) ASC
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
        SELECT 
            COALESCE(d.name, 'Visitor_' || dl.plate_number) AS name,
            COALESCE(d.type, 'Visitor') AS type,
            dl.id_number,
            dl.plate_number,
            d.phone,
            dl.date,
            dl.time_in
        FROM daily_logs dl
        LEFT JOIN drivers d ON dl.id_number = d.id_number
        LEFT JOIN vehicles v ON dl.plate_number = v.plate_number
        WHERE dl.date = ?
        ORDER BY time(dl.time_in) ASC
    ''', (today,))

    data_logs = c.fetchall()
    conn.close()
    return data_logs


def fetch_indi_logs(date, id_number):
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Fetch data from daily_logs, drivers, and vehicles tables
    c.execute('''
        SELECT 
            dl.plate_number,
            dl.time_in,
            dl.time_out
        FROM daily_logs dl
        LEFT JOIN drivers d ON dl.id_number = d.id_number
        LEFT JOIN vehicles v ON dl.plate_number = v.plate_number
        WHERE dl.date = ? AND dl.id_number = ?
        ORDER BY time(dl.time_in) DESC
    ''', (date, id_number))

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


def fetch_all_driver():
    # Connect to the SQLite database
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Query the "drivers" table to retrieve data for drivers authorized for the specified vehicle
    c.execute('''
        SELECT d.name, d.type, d.id_number, d.phone
        FROM drivers d
    ''')

    drivers_data = c.fetchall()

    # Close the database connection
    conn.close()

    return drivers_data


def fetch_all_vehicle():
    # Connect to the SQLite database
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Query the "vehicles" table to retrieve vehicles associated with the specified driver
    c.execute('''
            SELECT v.plate_number, v.vehicle_type, v.vehicle_color
            FROM vehicles v
        ''')

    vehicles_data = c.fetchall()

    # Close the database connection
    conn.close()

    return vehicles_data


def fetch_driver(id_number):
    # Connect to the SQLite database
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Query the "drivers" table to retrieve data for drivers authorized for the specified vehicle
    c.execute('''
        SELECT d.name, d.type, d.id_number, d.phone
        FROM drivers d
        WHERE d.id_number = ?
    ''', (id_number,))

    drivers_data = c.fetchall()

    # Close the database connection
    conn.close()

    return drivers_data


def fetch_vehicle(plate_number):
    # Connect to the SQLite database
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Query the "vehicles" table to retrieve vehicles associated with the specified driver
    c.execute('''
            SELECT v.plate_number, v.vehicle_type, v.vehicle_color
            FROM vehicles v
            WHERE v.plate_number = ?
        ''', (plate_number,))

    vehicles_data = c.fetchall()

    # Close the database connection
    conn.close()

    return vehicles_data


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
        SELECT v.plate_number, v.vehicle_type, v.vehicle_color, v.date
        FROM vehicles v
        JOIN driver_vehicle dv ON v.plate_number = dv.plate_number
        WHERE dv.driver_id = ?
    ''', (id_number,))

    vehicles_data = c.fetchall()

    # Close the database connection
    conn.close()

    return vehicles_data


def are_associated(driver_id, plate_number):
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Query the "driver_vehicle" table to check if the given ID and plate number are associated
    c.execute("SELECT * FROM driver_vehicle WHERE driver_id = ? AND plate_number = ?;", (driver_id, plate_number))
    association = c.fetchone()

    conn.close()

    return association is not None


# INSERT QUERIES:
ph_tz = pytz.timezone('Asia/Manila')
datess = datetime.date.today().strftime("%a, %b-%d-%Y")
current_time = datetime.datetime.now(tz=ph_tz).strftime("%I:%M %p")


def insert_logs(id_number, plate_number, date, time_in, time_out, time_in_status, is_registered):
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()
    c.execute('INSERT INTO daily_logs (id_number, plate_number, date, time_in, time_out, '
              'time_in_status,'
              'is_registered)'
              'VALUES (?, ?, ?, ?, ?, ?, ?)',
              (id_number, plate_number, date, time_in, time_out, time_in_status, is_registered))

    conn.commit()
    conn.close()

print(datess)

# insert_logs(111111, 'JAW9341', datess, current_time,
#                                  current_time, 1, 1)

def update_timeout(id_number, plate_number, new_timeout):
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()
    c.execute("UPDATE drivers SET date = ? WHERE date = ? AND id_number = ?",
              (new_timeout, id_number, plate_number))
    conn.commit()
    conn.close()

# update_timeout('2023-11-21', 111111, datess)
# update_timeout('2023-11-22', 232421, datess)
# update_timeout('2023-11-22', 656565, datess)

def delete(driver_id, plate_number):
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Corrected DELETE statement
    c.execute("DELETE FROM driver_vehicle WHERE driver_id = ? AND plate_number = ?;", (driver_id, plate_number))

    conn.commit()
    conn.close()



ids = ''
plate = ''
delete(ids, plate)
#
#
# import sqlite3
#
def delete(driver_id):
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Corrected DELETE statement
    c.execute("DELETE FROM vehicles WHERE plate_number = ?;", (driver_id,))

    conn.commit()
    conn.close()

# Example usage
ids = ''
delete(ids)

def deleted(driver_id):
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Corrected DELETE statement
    c.execute("DELETE FROM drivers WHERE id_number = ?;", (driver_id,))

    conn.commit()
    conn.close()

# Example usage
ids = ''
deleted(ids)

conn = sqlite3.connect('drivers.db')
c = conn.cursor()

# Retrieve and display the "drivers" table
c.execute("SELECT * FROM daily_logs;")
driver_rows = c.fetchall()

driver_table = PrettyTable(
    ['ewan', 'id_number', 'plate_number', 'date', 'time_in', 'time_out', 'time_in_status', 'is_registered'])
driver_table.align = "l"  # Left-align the data

for row in driver_rows:
    driver_table.add_row(row)

# Retrieve and display the "vehicles" table
c.execute("SELECT * FROM vehicles;")
vehicle_rows = c.fetchall()

vehicle_table = PrettyTable(["plate_number", "vehicle_color", "vehicle_type", "date"])
vehicle_table.align = "l"  # Left-align the data

for row in vehicle_rows:
    vehicle_table.add_row(row)

# Retrieve and display the "driver_vehicle" table
c.execute("SELECT * FROM driver_vehicle;")
driver_vehicle_rows = c.fetchall()

driver_vehicle_table = PrettyTable(["driver_id", "plate_number"])
driver_vehicle_table.align = "l"  # Left-align the data

for row in driver_vehicle_rows:
    driver_vehicle_table.add_row(row)

c.execute("SELECT * FROM daily_logs;")
daily_logs = c.fetchall()

print(daily_logs)

# Print the tables
print("Drivers Table:")
print(driver_table)

print("\nVehicles Table:")
print(vehicle_table)

print("\nDriver_Vehicle Table:")
print(driver_vehicle_table)


#
# def deletelogs(driver_id, plates):
#     conn = sqlite3.connect('drivers.db')
#     c = conn.cursor()
#
#     # Corrected DELETE statement
#     c.execute("DELETE FROM daily_logs WHERE date = ? AND plate_number = ?;", (driver_id,plates))
#
#     conn.commit()
#     conn.close()
#
#
# # Example usage
# ids = '2023-11-18'
# plate = 'JAW9341'
# deletelogs(ids,plate)
