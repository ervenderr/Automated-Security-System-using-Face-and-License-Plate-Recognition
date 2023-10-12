import pickle
import threading
from collections import Counter
from tkinter.font import nametofont

# import torch
import cv2
from tkinter import *

import face_recognition
from ttkbootstrap.scrolled import ScrolledFrame

import face_recognition_process
import datetime
import pytz
import numpy as np
import easyocr
import os
from ttkbootstrap.icons import Icon
from ultralytics import YOLO
from firebase_admin import db
import database
from history_logs import *
from register import create_driver
import queue
import re
# from pyfirmata import Arduino, SERVO, util
# from time import sleep
from PIL import Image, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import Style
from ttkbootstrap.dialogs import Messagebox
from database import *
import pytesseract
# from unregistered_encoding import process_images

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

reader = easyocr.Reader(['en'], gpu=True)
# Load the YOLO model
model_path = os.path.join('.', 'runs', 'detect', 'train', 'weights', 'last.pt')
lpr_model = YOLO(model_path)
threshold = 0.5

frame_queue = queue.Queue()


# port = 'COM6'
# pin = 10
# board = Arduino(port)
#
# board.digital[pin].mode = SERVO


class SSystem(ttk.Frame):
    def __init__(self, master_window):

        self.current_tab_index = -1
        self.license_recognition_enabled_exit = None
        self.face_recognition_enabled_exit = None
        self.camera_label2 = None
        self.camera_label1 = None
        self.profile_icon_exit = None
        self.table_view = None
        self.most_common_license = None
        self.license_frame_counter = 0
        self.face_frame_counter = 0
        self.collected_licenses = []
        self.extracted_text = None
        self.vehicle_data = None
        self.matched = False
        self.face_recognition_enabled = False
        self.license_recognition_enabled = False
        self.tab_frames = []
        self.cap = None
        self.face_cam = None
        self.data_from_db = None

        self.face_best_frame = None
        self.face_best_frame_blur = float('inf')
        self.frame_directory = "Images/frame_images"
        os.makedirs(self.frame_directory, exist_ok=True)

        master_window.attributes('-fullscreen', True)
        master_window.bind('<Escape>', lambda event: master_window.attributes('-fullscreen', False))

        super().__init__(master_window, padding=(20, 10))
        self.grid(row=0, column=0, sticky="nsew")  # Make the main frame expand in all directions

        # Configure row and column weights for the main window
        master_window.grid_rowconfigure(0, weight=1)
        master_window.grid_columnconfigure(0, weight=1)

        self.border_style = None
        self.plate_recognized = None
        self.results = None
        self.license_cam = None
        self.driver_image_label = None
        self.master_window = master_window

        self.camera_id1 = 2
        self.camera_id2 = 1

        self.driver_name = ttk.StringVar(value="")
        self.id_number = ttk.StringVar(value="")
        self.phone = ttk.StringVar(value="")
        self.plate = ttk.StringVar(value="")
        self.vehicle_type = ttk.StringVar(value="")
        self.vehicle_color = ttk.StringVar(value="")
        self.plate = ttk.StringVar(value="")
        current_time = datetime.datetime.now().strftime("%H:%M:%S")  # Current time
        self.time_in = current_time
        self.time_out = current_time
        self.date = self.date = datetime.date.today().strftime("%Y-%m-%d")
        self.profile_icon_path = ""
        self.data = []
        self.img_driver = []
        self.colors = master_window.style.colors
        self.face_counter = 0
        self.license_counter = 0
        self.id = -1
        self.driver_info = None
        self.vehicle_info = None

        # load encoding file
        file = open('Encode_file.p', 'rb')
        encode_with_ids = pickle.load(file)
        file.close()
        self.encode_list_known, self.driver_ids = encode_with_ids

        # Create the navigation bar
        self.nav_bar = ttk.Notebook(self)
        self.nav_bar.pack(fill=BOTH, expand=YES, padx=5)

        # Home Tab

        vehicle = PhotoImage(file=r'Images/menu.png')

        home_tab = ttk.Frame(self.nav_bar)
        self.nav_bar.add(home_tab, text="ENTRY", image=vehicle, compound='right')
        self.tab_frames.append(home_tab)

        scrolled_frame = ScrolledFrame(home_tab, width=1400, height=700, autohide=True, bootstyle='dark round')
        scrolled_frame.pack(fill=BOTH, expand=True)
        scrolled_frame.rowconfigure(0, weight=1)
        scrolled_frame.columnconfigure(0, weight=1)

        # Exit Tab
        exit_tab = ttk.Frame(self.nav_bar)
        self.nav_bar.add(exit_tab, text="EXIT", image=vehicle, compound='right')
        self.tab_frames.append(exit_tab)

        scrolled_exit_frame = ScrolledFrame(exit_tab, width=1400, height=700, autohide=True, bootstyle='dark round')
        scrolled_exit_frame.pack(fill=BOTH, expand=True)
        scrolled_exit_frame.rowconfigure(0, weight=1)
        scrolled_exit_frame.columnconfigure(0, weight=1)

        # Logs Tab
        logs_tab = ttk.Frame(self.nav_bar)
        self.nav_bar.add(logs_tab, text="HISTORY LOGS")
        self.tab_frames.append(logs_tab)

        self.nav_bar.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # registration Tab
        registration_tab = ttk.Frame(self.nav_bar)
        self.nav_bar.add(registration_tab, text="DRIVERS")
        self.tab_frames.append(registration_tab)

        self.setup_home_tab(scrolled_frame)
        self.setup_exit_tab(scrolled_exit_frame)
        self.setup_logs_tab(logs_tab)
        self.setup_register_tab(registration_tab)

        self.face_recognized = False
        self.license_recognized = False
        self.authorization_timer = None

        # Create variables to track the camera border colors
        self.camera_border_color1 = "black"  # Default color
        self.camera_border_color2 = "black"  # Default color

        self.face_lock = threading.Lock()

    def on_tab_change(self, event):
        current_tab_index = self.nav_bar.index(self.nav_bar.select())

        print(current_tab_index)

        # Check if the "Home" tab is selected, enable face recognition
        if current_tab_index == 0:
            self.face_recognition_enabled = False
            self.license_recognition_enabled = False

            self.face_recognition_enabled_exit = False
            self.license_recognition_enabled_exit = False

        elif current_tab_index == 1:
            self.face_recognition_enabled = False
            self.license_recognition_enabled = False

            self.face_recognition_enabled_exit = False
            self.license_recognition_enabled_exit = False

        else:
            # Disable face recognition and license plate recognition for other tabs
            self.face_recognition_enabled = False
            self.license_recognition_enabled = False
            self.face_recognition_enabled_exit = False
            self.license_recognition_enabled_exit = False

    def setup_home_tab(self, scrolled_frame):
        # Container frame for camera feeds and driver details
        container_frame = ttk.Frame(scrolled_frame)
        container_frame.grid(row=0, column=0, columnspan=5, sticky="nsew")
        scrolled_frame.grid_rowconfigure(0, weight=1)
        scrolled_frame.grid_columnconfigure(0, weight=1)

        # Frame for the cameras
        camera_frame = ttk.Frame(container_frame)
        camera_frame.grid(row=0, column=3, sticky="nsew", padx=20, pady=10)
        camera_frame.grid_rowconfigure(0, weight=1)
        camera_frame.grid_columnconfigure(1, weight=1)  # Allow the center column to expand

        # Frame for time and date
        time_date_frame = ttk.Frame(camera_frame)
        time_date_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        time_date_frame.grid_rowconfigure(0, weight=1)
        time_date_frame.grid_columnconfigure(0, weight=1)
        self.border_style = Style(theme="superhero")

        # Frame for displaying plate number
        plate_frame = ttk.LabelFrame(camera_frame, text='Daily logs', borderwidth=1, relief=RIDGE)
        plate_frame.grid(row=3, column=0, sticky="nsew", pady=10)
        plate_frame.grid_rowconfigure(0, weight=1)
        plate_frame.grid_columnconfigure(0, weight=1)

        # Panedwindow to split the two camera feeds horizontally
        camera_paned_window = ttk.Panedwindow(camera_frame, orient=HORIZONTAL)
        camera_paned_window.grid(row=2, column=0, sticky="nsew", pady=10)
        camera_paned_window.grid_rowconfigure(0, weight=1)
        camera_paned_window.grid_columnconfigure(0, weight=1)

        # Single frame for both camera feeds side by side
        camera_container = ttk.Frame(camera_paned_window)
        camera_paned_window.add(camera_container)

        # Label to display the time and date
        time_date_label = ttk.Label(time_date_frame, text="", font=("Helvetica", 20, "bold"), anchor='center')

        # Center the label within the time_date_frame
        time_date_label.grid(row=0, column=0, sticky="nsew")

        # Label to display the time and date
        entrans_label = ttk.Label(time_date_frame, text="ENTRANCE", font=("Helvetica", 30, "bold"), anchor='center')

        # Center the label within the time_date_frame
        entrans_label.grid(row=1, column=0, sticky="nsew")

        # Start updating the time and date label
        self.update_time_date(time_date_label)

        self.daily_logs(plate_frame)

        self.camera_border_color1 = 'white'
        self.camera_border_color2 = 'white'

        self.border_style.configure("face_border.TLabel", bordercolor=self.camera_border_color1)
        self.border_style.configure("license_border.TLabel", bordercolor=self.camera_border_color2)

        # Label to display the first camera feed
        self.camera_label1 = ttk.Label(camera_container, borderwidth=3, relief="solid", style="face_border.TLabel")
        self.camera_label1.pack(side=LEFT, padx=(0, 10))

        # Label to display the second camera feed
        self.camera_label2 = ttk.Label(camera_container, borderwidth=3, relief="solid", style="license_border.TLabel")
        self.camera_label2.pack(side=RIGHT)

        # self.start_camera_feed(2, self.camera_label1)
        # self.start_camera_feed(0, self.camera_label2)

        # Separator line between camera feeds and driver details
        separator = ttk.Separator(container_frame, orient=VERTICAL)
        separator.grid(row=0, column=4, sticky="nsew", padx=20)
        separator.grid_rowconfigure(0, weight=1)
        separator.grid_columnconfigure(0, weight=1)

        # Frame for the profile icon and driver details form
        profile_driver_frame = ttk.Frame(container_frame)
        profile_driver_frame.grid(row=0, column=5, sticky="nsew", padx=(0, 15))
        profile_driver_frame.grid_rowconfigure(0, weight=1)

        container_frame.grid_columnconfigure(5, weight=1)

        # Create a container for profile icon and driver's image
        image_container = ttk.Frame(profile_driver_frame)
        image_container.pack(pady=5)

        # Profile icon label
        profile_icon_path = "images/Profile_Icon.png"  # Replace with the path to your profile icon image
        profile_icon_image = Image.open(profile_icon_path)
        profile_icon_image = profile_icon_image.resize((250, 250), Image.Resampling.LANCZOS)
        self.profile_icon = ImageTk.PhotoImage(profile_icon_image)

        # Replace profile_icon_label with driver_image_label
        self.driver_image_label = ttk.Label(profile_driver_frame, image=self.profile_icon, justify=CENTER)
        self.driver_image_label.pack(pady=(5, 5))

        instruction_text = "Driver Details: "
        instruction = ttk.Label(profile_driver_frame, text=instruction_text)
        instruction.pack(fill=X, pady=5)

        form_entry_labels = ["Name: ", "ID number: ", "Plate number: ", "Phone: ", "Vehicle type: ", "Vehicle color: "]
        form_entry_vars = [self.driver_name, self.id_number, self.plate, self.phone, self.vehicle_type,
                           self.vehicle_color]

        for i, (label, var) in enumerate(zip(form_entry_labels, form_entry_vars)):
            self.create_form_entry(profile_driver_frame, label, var)

        self.create_buttonbox(profile_driver_frame)

    def setup_exit_tab(self, scrolled_exit_frame):
        # Container frame for camera feeds and driver details
        container_frame = ttk.Frame(scrolled_exit_frame)
        container_frame.grid(row=0, column=0, columnspan=5, sticky="nsew")
        scrolled_exit_frame.grid_rowconfigure(0, weight=1)
        scrolled_exit_frame.grid_columnconfigure(0, weight=1)

        # Frame for the cameras
        camera_frame = ttk.Frame(container_frame)
        camera_frame.grid(row=0, column=3, sticky="nsew", padx=20, pady=10)
        camera_frame.grid_rowconfigure(0, weight=1)
        camera_frame.grid_columnconfigure(1, weight=1)  # Allow the center column to expand

        # Frame for time and date
        time_date_frame = ttk.Frame(camera_frame)
        time_date_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        time_date_frame.grid_rowconfigure(0, weight=1)
        time_date_frame.grid_columnconfigure(0, weight=1)
        self.border_style = Style(theme="superhero")

        # Frame for displaying plate number
        plate_frame = ttk.LabelFrame(camera_frame, text='Daily logs', borderwidth=1, relief=RIDGE)
        plate_frame.grid(row=3, column=0, sticky="nsew", pady=10)
        plate_frame.grid_rowconfigure(0, weight=1)
        plate_frame.grid_columnconfigure(0, weight=1)

        # Panedwindow to split the two camera feeds horizontally
        camera_paned_window = ttk.Panedwindow(camera_frame, orient=HORIZONTAL)
        camera_paned_window.grid(row=2, column=0, sticky="nsew", pady=10)
        camera_paned_window.grid_rowconfigure(0, weight=1)
        camera_paned_window.grid_columnconfigure(0, weight=1)

        # Single frame for both camera feeds side by side
        camera_container = ttk.Frame(camera_paned_window)
        camera_paned_window.add(camera_container)

        # Label to display the time and date
        time_date_label = ttk.Label(time_date_frame, text="",font=("Arial", 20, "bold"), anchor='center')

        # Center the label within the time_date_frame
        time_date_label.grid(row=0, column=0, sticky="nsew")

        entrans_label = ttk.Label(time_date_frame, text="EXIT", font=("Helvetica", 30, "bold"), anchor='center')

        # Center the label within the time_date_frame
        entrans_label.grid(row=1, column=0, sticky="nsew")

        # Start updating the time and date label
        self.update_time_date(time_date_label)

        self.daily_logs(plate_frame)

        self.camera_border_color1 = 'white'
        self.camera_border_color2 = 'white'

        self.border_style.configure("face_border.TLabel", bordercolor=self.camera_border_color1)
        self.border_style.configure("license_border.TLabel", bordercolor=self.camera_border_color2)

        # Label to display the first camera feed
        self.camera_label1 = ttk.Label(camera_container, borderwidth=3, relief="solid", style="face_border.TLabel")
        self.camera_label1.pack(side=LEFT, padx=(0, 10))

        # Label to display the second camera feed
        self.camera_label2 = ttk.Label(camera_container, borderwidth=3, relief="solid", style="license_border.TLabel")
        self.camera_label2.pack(side=RIGHT)

        self.start_camera_feed(2, self.camera_label1)
        self.start_camera_feed(0, self.camera_label2)

        # Separator line between camera feeds and driver details
        separator = ttk.Separator(container_frame, orient=VERTICAL)
        separator.grid(row=0, column=4, sticky="nsew", padx=20)
        separator.grid_rowconfigure(0, weight=1)
        separator.grid_columnconfigure(0, weight=1)

        # Frame for the profile icon and driver details form
        profile_driver_frame = ttk.Frame(container_frame)
        profile_driver_frame.grid(row=0, column=5, sticky="nsew", padx=(0, 15))
        profile_driver_frame.grid_rowconfigure(0, weight=1)

        container_frame.grid_columnconfigure(5, weight=1)

        # Create a container for profile icon and driver's image
        image_container = ttk.Frame(profile_driver_frame)
        image_container.pack(pady=5)

        # Profile icon label
        profile_icon_path = "images/Profile_Icon.png"  # Replace with the path to your profile icon image
        profile_icon_image = Image.open(profile_icon_path)
        profile_icon_image = profile_icon_image.resize((250, 250), Image.Resampling.LANCZOS)
        self.profile_icon_exit = ImageTk.PhotoImage(profile_icon_image)

        # Replace profile_icon_label with driver_image_label
        self.driver_image_label = ttk.Label(profile_driver_frame, image=self.profile_icon, justify=CENTER)
        self.driver_image_label.pack(pady=(5, 5))

        instruction_text = "Driver Details: "
        instruction = ttk.Label(profile_driver_frame, text=instruction_text)
        instruction.pack(fill=X, pady=5)

        form_entry_labels = ["Name: ", "ID number: ", "Plate number: ", "Phone: ", "Vehicle type: ", "Vehicle color: "]
        form_entry_vars = [self.driver_name, self.id_number, self.plate, self.phone, self.vehicle_type,
                           self.vehicle_color]

        for i, (label, var) in enumerate(zip(form_entry_labels, form_entry_vars)):
            self.create_form_entry(profile_driver_frame, label, var)

        self.create_buttonbox(profile_driver_frame)

    def update_time_date(self, label):
        ph_tz = pytz.timezone('Asia/Manila')
        current_time = datetime.datetime.now(tz=ph_tz).strftime("%a, %Y-%m-%d %I:%M:%S %p")
        label.config(text=current_time)
        self.master_window.after(1000, lambda: self.update_time_date(label))

    def update_driver_details(self):
        if self.driver_info is not None and self.img_driver is not None and self.vehicle_info is not None:
            self.driver_name.set(self.driver_info.get("name", ""))
            self.id_number.set(self.driver_info.get("id_number", ""))
            self.phone.set(self.driver_info.get("phone", ""))
            self.plate.set(self.vehicle_info.get("plate_number", ""))
            self.vehicle_type.set(self.vehicle_info.get("vehicle_type", ""))
            self.vehicle_color.set(self.vehicle_info.get("vehicle_color", ""))

            # Display the driver's image
            driver_image = Image.fromarray(self.img_driver)
            driver_image = driver_image.resize((250, 250), Image.Resampling.LANCZOS)

            # Convert color channels from BGR to RGB
            driver_image = Image.merge("RGB", driver_image.split()[::-1])

            driver_image = ImageTk.PhotoImage(driver_image)
            self.driver_image_label.configure(image=driver_image)
            self.driver_image_label.image = driver_image  # Keep a reference to avoid garbage collection

            self.face_recognition_enabled = False
            self.license_recognition_enabled = False

            threading.Timer(3, self.clock_in).start()

        elif self.most_common_license is not None and self.img_driver is not None and self.id_number is None:

            visitor = f"Visitor_{self.most_common_license}"

            self.driver_name.set(visitor)
            self.plate.set(self.most_common_license)

            # Display the driver's image
            driver_image = Image.fromarray(self.img_driver)
            driver_image = driver_image.resize((250, 250), Image.Resampling.LANCZOS)

            driver_image = ImageTk.PhotoImage(driver_image)
            self.driver_image_label.configure(image=driver_image)
            self.driver_image_label.image = driver_image  # Keep a reference to avoid garbage collection

            self.face_recognition_enabled = False
            self.license_recognition_enabled = False

    def setup_logs_tab(self, parent_tab):
        history_logs_tab(parent_tab)

    def setup_register_tab(self, parent_tab):
        create_driver(parent_tab)

    def start_camera_feed(self, camera_id, camera_label):
        # Open the camera with the specified camera_id
        self.cap = cv2.VideoCapture(camera_id)

        # Continuously read frames from the camera and display them on the GUI
        self.update_camera(self.cap, camera_label, camera_id)

    def update_camera(self, cap, camera_label, camera_id):
        ret, frame = cap.read()

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            # Resize frame for display

            # Perform face recognition on the second camera feed (camera_id=1)
            if self.face_recognition_enabled and camera_id == 2:
                face_cam = frame
                face_photo = ImageTk.PhotoImage(image=Image.fromarray(face_cam))
                camera_label.configure(image=face_photo, borderwidth=1, relief="solid")

                try:
                    current_face = face_recognition.face_locations(face_cam)
                    current_encode = face_recognition.face_encodings(face_cam, current_face)
                    print("ENCODING 1")

                    # Multithreading for face recognition
                    face_thread = threading.Thread(
                        target=self.process_face_recognition,
                        args=(current_encode, current_face, face_cam, camera_label)
                    )
                    face_thread.start()

                except Exception as e:
                    print("Error in face recognition:", e)

            if self.license_recognition_enabled and camera_id == 0:
                self.license_cam = frame

                self.start_computation_thread()

            if (self.face_counter and self.license_counter) != 0:

                if ((self.face_counter and self.license_counter) == 1 and self.face_recognized and
                        self.license_recognized):

                    print("id: ", self.id)
                    print("extracted_text : ", self.extracted_text)

                    self.driver_info = db.child(f'Drivers/{self.id}').get().val()
                    self.vehicle_info = db.child(f'Vehicles/{self.extracted_text}').get().val()
                    print(self.driver_info)

                    bucket = storage.bucket()
                    blob = bucket.blob(f'driver images/{self.id}.png')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    self.img_driver = cv2.imdecode(array, cv2.COLOR_BGR2RGB)

                    self.face_counter += 1
                    self.license_counter += 1

                    print("id: ", self.id)
                    print("vinfo: ", self.vehicle_info)

                    if self.id in self.vehicle_info['drivers'] and self.vehicle_info['drivers'][self.id]:
                        self.update_driver_details()
                    else:
                        self.not_match()
                        print("NOT MATCH")

                elif ((self.face_counter and self.license_counter) == 1
                      and not (self.license_recognized and self.face_recognized)):

                    self.face_recognition_enabled = False
                    self.license_recognition_enabled = False

                    unregistered_profile = Image.open("Images/frame_images/best_frame.jpg")
                    self.img_driver = np.array(unregistered_profile)

                    self.update_driver_details()
                    print("Not registered")

        elif ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            # Resize frame for display

            # Perform face recognition on the second camera feed (camera_id=1)
            if self.face_recognition_enabled_exit and camera_id == 2:
                face_cam = frame
                face_photo = ImageTk.PhotoImage(image=Image.fromarray(face_cam))
                camera_label.configure(image=face_photo, borderwidth=1, relief="solid")

                try:
                    current_face = face_recognition.face_locations(face_cam)
                    current_encode = face_recognition.face_encodings(face_cam, current_face)
                    print("ENCODING 2")

                    # Multithreading for face recognition
                    face_thread = threading.Thread(
                        target=self.process_face_recognition,
                        args=(current_encode, current_face, face_cam, camera_label)
                    )
                    face_thread.start()

                except Exception as e:
                    print("Error in face recognition:", e)

            if self.license_recognition_enabled_exit and camera_id == 0:
                self.license_cam = frame

                self.start_computation_thread()

            if (self.face_counter and self.license_counter) != 0:

                if ((self.face_counter and self.license_counter) == 1 and self.face_recognized and
                        self.license_recognized):

                    print("id: ", self.id)
                    print("extracted_text : ", self.extracted_text)

                    self.driver_info = db.child(f'Drivers/{self.id}').get().val()
                    self.vehicle_info = db.child(f'Vehicles/{self.extracted_text}').get().val()
                    print(self.driver_info)

                    bucket = storage.bucket()
                    blob = bucket.blob(f'driver images/{self.id}.png')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    self.img_driver = cv2.imdecode(array, cv2.COLOR_BGR2RGB)

                    self.face_counter += 1
                    self.license_counter += 1

                    print("id: ", self.id)
                    print("vinfo: ", self.vehicle_info)

                    if self.id in self.vehicle_info['drivers'] and self.vehicle_info['drivers'][self.id]:
                        self.update_driver_details()
                    else:
                        self.not_match()
                        print("NOT MATCH")

                elif ((self.face_counter and self.license_counter) == 1
                      and not (self.license_recognized and self.face_recognized)):

                    self.face_recognition_enabled_exit = False
                    self.license_recognition_enabled_exit = False

                    unregistered_profile = Image.open("Images/frame_images/best_frame.jpg")
                    self.img_driver = np.array(unregistered_profile)

                    self.update_driver_details()
                    print("Not registered")

        # Convert the frame to a PhotoImage (compatible with tkinter) and display it
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        camera_label.configure(image=photo)
        camera_label.image = photo

        # Repeat the update after a delay
        camera_label.after(30, self.update_camera, cap, camera_label, camera_id)

    def process_face_recognition(self, current_encode, current_face, face_cam, camera_label):
        print("ENCODINGSS")
        with self.face_lock:  # Use the lock to ensure thread safety
            for encode_face, face_location in zip(current_encode, current_face):
                print("ENCODING")
                top, right, bottom, left = face_location
                matches = face_recognition.compare_faces(self.encode_list_known, encode_face)
                face_dis = face_recognition.face_distance(self.encode_list_known, encode_face)

                match_index = np.argmin(face_dis)
                if matches[match_index] and self.face_frame_counter <= 5:
                    self.id = self.driver_ids[match_index]
                    cv2.rectangle(face_cam, (left, top), (right, bottom), (0, 255, 0), 2)  # Draw green bbox

                    if self.face_counter == 0:
                        text = "Waiting for license recognition..."
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        font_scale = 0.5
                        font_color = (255, 255, 255)  # White color
                        line_thickness = 1

                        # Calculate the text size to position it above the bounding box
                        text_size = cv2.getTextSize(text, font, font_scale, line_thickness)[0]
                        text_x = left + (right - left - text_size[0]) // 2
                        text_y = top - 10

                        cv2.putText(face_cam, text, (text_x, text_y), font, font_scale, font_color,
                                    line_thickness, cv2.LINE_AA)
                        cv2.waitKey(1)

                        self.face_counter = 1

                    # Set the face_recognized flag to True when the face is recognized
                    self.face_recognized = True
                    self.camera_border_color2 = "#00ff00"
                    self.border_style.configure("face_border.TLabel", bordercolor=self.camera_border_color2,
                                                borderwidth=4)

                else:
                    cv2.rectangle(face_cam, (left, top), (right, bottom), (255, 0, 0), 3)  # Draw red bbox

                    current_frame = face_cam.copy()

                    # Calculate blur level (you can use different methods)
                    blur = cv2.Laplacian(current_frame, cv2.CV_64F).var()

                    # Check if the current frame is less blurred than the best frame
                    if blur < self.face_best_frame_blur and self.face_frame_counter == 6:
                        self.face_best_frame_blur = blur
                        self.face_best_frame = current_frame

                        self.save_best_frame()

                        self.face_recognized = False
                        self.face_counter = 1

                        self.camera_border_color2 = "#ff0000"
                        self.border_style.configure("face_border.TLabel", bordercolor=self.camera_border_color2,
                                                    borderwidth=4)

                    self.face_frame_counter += 1

                    print("Unauthorized")
                    print("face_counter: ", self.face_frame_counter)

    def save_best_frame(self):
        if self.face_best_frame is not None:
            frame_rgb = cv2.cvtColor(self.face_best_frame, cv2.COLOR_BGR2RGB)
            frame_filename = os.path.join(self.frame_directory, "best_frame.jpg")
            cv2.imwrite(frame_filename, frame_rgb)

    def start_computation_thread(self):
        computation_thread = threading.Thread(target=self.run_model_computation, args=(self.license_cam,))
        computation_thread.start()

    def run_model_computation(self, license_cam):
        # print("")
        results = lpr_model(license_cam)[0]

        object_detected = False  # Flag to track if any object was detected in the frame

        for result in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result

            if score > threshold:
                object_detected = True  # Set the flag to True for valid detection
                cv2.rectangle(self.license_cam, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                print("lcounter: ", self.license_counter)

                if self.license_counter == 0 and self.license_frame_counter <= 5:
                    # Extract the license plate region
                    license_plate_region = license_cam[int(y1):int(y2), int(x1):int(x2)]

                    try:
                        resize_test_license_plate = cv2.resize(
                            license_plate_region, None, fx=2, fy=2,
                            interpolation=cv2.INTER_CUBIC)

                        grayscale_resize_test_license_plate = cv2.cvtColor(
                            resize_test_license_plate, cv2.COLOR_BGR2GRAY)

                        gaussian_blur_license_plate = cv2.GaussianBlur(
                            grayscale_resize_test_license_plate, (5, 5), 0)

                        config = ('--oem 3 -l eng --psm 6 -c '
                                  'tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                        ocr_result = pytesseract.image_to_string(gaussian_blur_license_plate, lang='eng',
                                                                 config=config)

                        # Cleaning up the result
                        ocr_result = "".join(ocr_result.split()).replace(":", "").replace("-", "")

                        extracted_text = f'{ocr_result[:3]}{ocr_result[3:7]}'

                        # Display the extracted text
                        print("EXTRACTED TEXT: ", extracted_text)

                        vehicle_data = db.child('Vehicles').get().val()

                        if extracted_text in vehicle_data:

                            self.extracted_text = extracted_text

                            print(f"License plate {extracted_text} is in the vehicles data.")
                            self.license_recognized = True
                            self.camera_border_color2 = "#00ff00"
                            self.border_style.configure("license_border.TLabel", bordercolor=self.camera_border_color2,
                                                        borderwidth=4)
                            cv2.rectangle(self.license_cam, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

                            self.license_counter = 1

                        else:
                            pattern = r'[A-Z]{3}\d{4}'

                            print("counter: ", self.license_frame_counter)

                            if self.license_frame_counter == 5:

                                pattern = r'[A-Z]{3}\d{4}'
                                filtered_licenses = []

                                for licenses in self.collected_licenses:
                                    if re.match(pattern, licenses):
                                        filtered_licenses.append(licenses)

                                print("Collected licenses:", filtered_licenses)

                                license_counts = Counter(filtered_licenses)
                                self.most_common_license = license_counts.most_common(1)[0][0]

                                print("Most common license plate:", self.most_common_license)

                                self.camera_border_color2 = "#ff0000"
                                self.border_style.configure("license_border.TLabel",
                                                            bordercolor=self.camera_border_color2,
                                                            borderwidth=4)
                                self.license_counter = 1
                                self.license_recognized = False

                            elif re.match(pattern, extracted_text):
                                self.collected_licenses.append(extracted_text)

                                self.license_frame_counter += 1

                    except Exception as e:
                        print("Error in license recognition:", e)

                # Convert the license_cam image to PhotoImage for display
                photo = ImageTk.PhotoImage(image=Image.fromarray(self.license_cam))
                self.camera_label2.configure(image=photo)
                self.camera_label2.image = photo

        # Schedule the GUI update method in the main thread
        frame_queue.put(self.license_cam)

    def display_frame_with_rectangles(self):
        try:
            # Retrieve the latest frame from the queue
            self.license_cam = frame_queue.get_nowait()
        except queue.Empty:
            pass
        # Repeat the update after a delay (e.g., 30ms)
        self.master_window.after(30, self.display_frame_with_rectangles)

    def create_form_entry(self, container, label, variable):

        form_field_container = ttk.Frame(container)
        form_field_container.pack(fill=X, pady=5)

        entry_style = ttk.Style()
        entry_style.map("TEntry", foreground=[("disabled", "white")])
        entry_var = variable

        form_field_label = ttk.Label(master=form_field_container, text=label, width=15)
        form_field_label.grid(row=0, column=0, padx=12, pady=(0, 5), sticky="w")

        form_input = ttk.Entry(master=form_field_container, textvariable=entry_var,
                               font=('Helvetica', 13), state='disabled')
        form_input.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="ew")

        # Make the columns of form_field_container expand relative to the container's width
        form_field_container.grid_columnconfigure(0, weight=1)  # Set weight for column 0

        add_regex_validation(form_input, r'^[a-zA-Z0-9_]*$')

        return form_input

    def create_buttonbox(self, container):
        button_container = ttk.Frame(container)
        button_container.pack(fill=X, expand=YES, pady=(10, 5))
        button_container.columnconfigure(0, weight=1)

        btn_style = ttk.Style().configure('TButton', font=('Helvetica', 13))

        cancel_btn = ttk.Button(
            master=button_container,
            text="CANCEL",
            command=self.on_cancel,
            bootstyle=DANGER,
            style=btn_style
        )
        cancel_btn.grid(row=2, column=0, pady=(0, 10), sticky="ew")

        submit_btn = ttk.Button(
            master=button_container,
            text="CLOCK IN",
            command=self.reset,
            bootstyle=SUCCESS,
            style=btn_style
        )
        submit_btn.grid(row=0, column=0, pady=(0, 10), sticky="ew")

        mark_visitor = ttk.Button(
            master=button_container,
            text="MARK AS VISITOR",
            command=self.clock_in,
            bootstyle=PRIMARY,
            style=btn_style
        )
        mark_visitor.grid(row=1, column=0, pady=(0, 10), sticky="ew")

    # def rotateservo(self, pin, angle):
    #     board.digital[pin].write(angle)
    #     sleep(0.015)

    def reset(self):

        self.license_recognition_enabled = False
        self.face_recognition_enabled = False
        self.face_counter = 0
        self.license_counter = 0

        # self.reset_encodings()

        toast = ToastNotification(
            title="Success",
            message="YEHEY SUCCESS",
            duration=3000,
        )
        toast.show_toast()

        self.driver_info = None
        self.img_driver = None
        self.vehicle_info = None

        self.license_recognized = False
        self.face_recognized = False

        # Reset driver's image to default (profile_icon)
        profile_icon_path = "images/Profile_Icon.png"
        profile_icon_image = Image.open(profile_icon_path)
        profile_icon_image = profile_icon_image.resize((250, 250), Image.Resampling.LANCZOS)
        self.img_driver = np.array(profile_icon_image)

        # Explicitly reset the GUI elements to their default values
        self.driver_name.set("")
        self.id_number.set("")
        self.phone.set("")
        self.plate.set("")
        self.vehicle_type.set("")
        self.vehicle_color.set("")

        self.driver_image_label.configure(image=self.profile_icon)
        self.driver_image_label.image = self.profile_icon

        self.camera_border_color2 = "white"
        self.border_style.configure("face_border.TLabel", bordercolor=self.camera_border_color2,
                                    borderwidth=4)

        self.border_style.configure("license_border.TLabel", bordercolor=self.camera_border_color2,
                                    borderwidth=4)

        self.update_driver_details()

        threading.Timer(20, self.reset_counters).start()

        print("TIME IS UP!")
        # self.face_counter = 0
        # self.license_counter = 0
        # self.license_frame_counter = 0
        #
        # self.license_recognition_enabled = True
        # self.face_recognition_enabled = True

        # for i in range(0, 360):
        #     self.rotateservo(pin, i)

        # self.plate = "NONE"
        #
        # logs_data = (
        #     self.driver_name.get(), self.id_number.get(), self.phone.get(), self.plate, self.date, self.time_in,
        #     self.time_out)
        #
        # c.execute("INSERT INTO daily_logs VALUES (?, ?, ?, ?, ?, ?, ?)", logs_data)
        # conn.commit()
        #

    def reset_counters(self):
        self.license_frame_counter = 0
        self.license_frame_counter = 0
        self.license_recognition_enabled = True
        self.face_recognition_enabled = True

    def on_cancel(self):
        if self.cap is not None:
            self.cap.release()
        self.quit()

    def create_table(self):
        return

    def register_driver(self):
        return

    def daily_logs(self, plate_frame):

        colors = ttk.Style().colors

        custom_style = ttk.Style()
        custom_style.configure("Custom.Treeview", font=("Helvetica", 12))

        coldata = [
            {"text": "Name", "stretch": False},
            {"text": "ID number", "stretch": False},
            {"text": "Plate number", "stretch": False},
            {"text": "Phone", "stretch": False},
            {"text": "Date", "stretch": False},
            {"text": "Time in", "stretch": False},
            {"text": "Time out", "stretch": False},
        ]

        rowdata = [list(row) for row in database.fetch_logs()]

        self.table_view = Tableview(
            master=plate_frame,
            coldata=coldata,
            rowdata=rowdata,
            paginated=True,
            searchable=True,
            stripecolor=None,
            autoalign=True,
            bootstyle=PRIMARY,
        )
        self.table_view.load_table_data()
        default_font = nametofont("TkDefaultFont")
        default_font.configure(size=10)
        plate_frame.option_add("*Font", default_font)

        self.table_view.pack(fill=BOTH, expand=YES, padx=10, pady=5)

    def not_match(self):

        self.matched = False
        self.license_recognition_enabled = False
        self.face_recognition_enabled = False

        self.face_counter = 0
        self.license_counter = 0

        self.driver_info = None
        self.img_driver = None
        self.vehicle_info = None

        self.license_recognized = False
        self.face_recognized = False

        # Reset driver's image to default (profile_icon)
        profile_icon_path = "images/Profile_Icon.png"
        profile_icon_image = Image.open(profile_icon_path)
        profile_icon_image = profile_icon_image.resize((250, 250), Image.Resampling.LANCZOS)
        self.img_driver = np.array(profile_icon_image)

        # Explicitly reset the GUI elements to their default values
        self.driver_name.set("")
        self.id_number.set("")
        self.phone.set("")
        self.plate.set("")
        self.vehicle_type.set("")
        self.vehicle_color.set("")

        self.driver_image_label.configure(image=self.profile_icon)
        self.driver_image_label.image = self.profile_icon

        self.camera_border_color2 = "white"
        self.border_style.configure("face_border.TLabel", bordercolor=self.camera_border_color2,
                                    borderwidth=4)

        self.border_style.configure("license_border.TLabel", bordercolor=self.camera_border_color2,
                                    borderwidth=4)

        self.update_driver_details()

        okay = Messagebox.ok("Driver and license plate don't match", 'ERROR', icon=Icon.info)

        if okay is None:
            print("OK CLICKED")
            self.reset_counters()

    def clock_in(self):

        id_number_value = self.id_number.get()
        phone_value = self.phone.get()
        driver_name_value = self.driver_name.get()
        plate_value = self.plate.get()

        if self.most_common_license is not None and self.img_driver is not None and self.id_number is None:

            id_number_value = None
            phone_value = None
            time_in_status = 0
            is_registered = 1

            database.insert_logs(driver_name_value, id_number_value, plate_value, phone_value, self.date, self.time_in,
                                 None, time_in_status, is_registered)

            self.table_view.insert_row(index=0,
                                       values=[driver_name_value, self.id_number, plate_value, self.phone, self.date,
                                               self.time_in, None, time_in_status, is_registered])

            filename = f"Images/unregistered driver/{self.most_common_license}.jpg"
            pyre_storage.child(filename).put(self.img_driver)

        elif self.driver_info is not None and self.img_driver is not None and self.vehicle_info is not None:

            time_in_status = 0
            is_registered = 0

            database.insert_logs(driver_name_value, id_number_value, plate_value, phone_value, self.date, self.time_in,
                                 None, time_in_status, is_registered)

            self.table_view.insert_row(index=0,
                                       values=[driver_name_value, id_number_value, plate_value, phone_value, self.date,
                                               self.time_in, None, time_in_status, is_registered])

            self.table_view.load_table_data()
            print("Inserted")

        else:
            style = Style()
            style.configure('TMessagebox', font=('Helvetica', 16))
            okay = Messagebox.ok("NO DATA FOUND", 'ERROR', icon=Icon.error, style=style)

            if okay is None:
                print("OK CLICKED")

        self.table_view.load_table_data()
        self.reset()
        print("Inserted")

    def reset_encodings(self):
        # load encoding file
        file = open('unregistered_driver.p', 'rb')
        encode_with_ids = pickle.load(file)
        file.close()
        self.encode_list_known, self.driver_ids = encode_with_ids


if __name__ == "__main__":
    app = ttk.Window("WMSU Security System", "superhero", resizable=(True, True))
    app.geometry("1400x700+350+100")
    app.grid_rowconfigure(0, weight=1)  # Make the main window expand vertically
    app.grid_columnconfigure(0, weight=1)

    s_system = SSystem(app)  # Create an instance of SSystem

    # Start the processing thread on the instance
    s_system.start_computation_thread()
    app.mainloop()
