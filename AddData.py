import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://wmsusecuritysystem-default-rtdb.firebaseio.com/"
})

ref = db.reference('Drivers')

data = {
    '321654':
        {
            'name': "Elon Musk",
            'id_number': 321654,
            'phone': 9817068891,
            'plate_number': "ABC 123",
            'date': "2023-8-8",
            'time_in': "06:00 AM",
            'time_out': "05:00 PM",
        },

    '852741':
        {
            'name': "Some Girl",
            'id_number': 852741,
            'phone': 987456123,
            'plate_number': "EFG 456",
            'date': "2023-8-8",
            'time_in': "06:02 AM",
            'time_out': "05:04 PM",
        },

    '963852':
        {
            'name': "Erven Idjad",
            'id_number': 963852,
            'phone': 9817068891,
            'plate_number': "HIJ 789",
            'date': "2023-8-8",
            'time_in': "06:10 AM",
            'time_out': "05:14 PM",
        },
}

for key,value in data.items():
    ref.child(key).set(value)
