# database.py
import pyrebase
import firebase_admin
from firebase_admin import credentials, storage

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

