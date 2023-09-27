import pickle
import threading
import torch
import cv2
from tkinter import *
import face_recognition
import datetime
import pytz
import numpy as np
import easyocr
import os
from ultralytics import YOLO
from firebase_admin import db
from history_logs import *
from register import *
import queue
import re
from pyfirmata import Arduino, SERVO, util
from time import sleep

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

        self.face_recognition_enabled = False
        self.license_recognition_enabled = False
        self.tab_frames = []
        self.cap = None
        self.face_cam = None
        self.data_from_db = None
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
        self.counter = 0
        self.id = -1
        self.driver_info = None
        self.vehicle_info = None

        # load encoding file
        self.file = open('Encode_file.p', 'rb')
        self.encode_with_ids = pickle.load(self.file)
        self.file.close()
        self.encode_list_known, self.driver_ids = self.encode_with_ids

        # Create the navigation bar
        self.nav_bar = ttk.Notebook(self)
        self.nav_bar.pack(fill=BOTH, expand=YES, padx=5)

        # Home Tab
        home_tab = ttk.Frame(self.nav_bar)
        self.nav_bar.add(home_tab, text="Home")
        self.tab_frames.append(home_tab)

        # Logs Tab
        logs_tab = ttk.Frame(self.nav_bar)
        self.nav_bar.add(logs_tab, text="History Logs")
        self.tab_frames.append(logs_tab)

        self.nav_bar.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # # registered Tab
        # registered_tab = ttk.Frame(self.nav_bar)
        # self.nav_bar.add(registered_tab, text="Registered Vehicle")

        # registration Tab
        registration_tab = ttk.Frame(self.nav_bar)
        self.nav_bar.add(registration_tab, text="Driver Registration")
        self.tab_frames.append(registration_tab)

        self.setup_home_tab(home_tab)
        self.setup_logs_tab(logs_tab)
        self.setup_register_tab(registration_tab)

        self.face_recognized = True
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
            self.face_recognition_enabled = True
            self.license_recognition_enabled = True
        else:
            # Disable face recognition and license plate recognition for other tabs
            self.face_recognition_enabled = False
            self.license_recognition_enabled = False

    def setup_home_tab(self, home_tab):
        # Container frame for camera feeds and driver details
        container_frame = ttk.Frame(home_tab)
        container_frame.grid(row=0, column=0, columnspan=5, sticky="nsew")
        home_tab.grid_rowconfigure(0, weight=1)
        home_tab.grid_columnconfigure(0, weight=1)

        # Frame for the cameras
        camera_frame = ttk.Frame(container_frame)
        camera_frame.grid(row=0, column=3, sticky="nsew", padx=20, pady=20)
        camera_frame.grid_rowconfigure(0, weight=1)
        camera_frame.grid_columnconfigure(1, weight=1)  # Allow the center column to expand

        # Frame for time and date
        time_date_frame = ttk.Frame(camera_frame)
        time_date_frame.grid(row=1, column=0, sticky="nsew", pady=20)
        time_date_frame.grid_rowconfigure(0, weight=1)
        time_date_frame.grid_columnconfigure(0, weight=1)
        self.border_style = Style(theme="superhero")

        # Frame for displaying plate number
        plate_frame = ttk.Frame(camera_frame, borderwidth=1, relief=RIDGE)
        plate_frame.grid(row=3, column=0, sticky="nsew", pady=20)
        plate_frame.grid_rowconfigure(0, weight=1)
        plate_frame.grid_columnconfigure(0, weight=1)

        # Panedwindow to split the two camera feeds horizontally
        camera_paned_window = ttk.Panedwindow(camera_frame, orient=HORIZONTAL)
        camera_paned_window.grid(row=2, column=0, sticky="nsew", pady=20)
        camera_paned_window.grid_rowconfigure(0, weight=1)
        camera_paned_window.grid_columnconfigure(0, weight=1)

        # Single frame for both camera feeds side by side
        camera_container = ttk.Frame(camera_paned_window)
        camera_paned_window.add(camera_container)

        # Label to display the time and date
        time_date_label = ttk.Label(time_date_frame, text="",
                                    width=50, font=("Arial", 20, "bold"),
                                    anchor='center')

        # Center the label within the time_date_frame
        time_date_label.grid(row=0, column=0, sticky="nsew")

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

        self.start_camera_feed(0, self.camera_label1)
        # Start the second camera feed (camera_id=1)
        self.start_camera_feed(1, self.camera_label2)

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
        image_container.pack(pady=10)

        # Profile icon label
        profile_icon_path = "images/Profile_Icon.png"  # Replace with the path to your profile icon image
        profile_icon_image = Image.open(profile_icon_path)
        profile_icon_image = profile_icon_image.resize((250, 250), Image.Resampling.LANCZOS)
        self.profile_icon = ImageTk.PhotoImage(profile_icon_image)

        # Replace profile_icon_label with driver_image_label
        self.driver_image_label = ttk.Label(profile_driver_frame, image=self.profile_icon, justify=CENTER)
        self.driver_image_label.pack(pady=(10, 30))

        instruction_text = "Driver Details: "
        instruction = ttk.Label(profile_driver_frame, text=instruction_text)
        instruction.pack(fill=X, pady=10)

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
            if self.face_recognition_enabled and camera_id == 0:
                face_cam = frame
                face_photo = ImageTk.PhotoImage(image=Image.fromarray(face_cam))
                camera_label.configure(image=face_photo, borderwidth=1, relief="solid")

                try:
                    current_face = face_recognition.face_locations(face_cam)
                    current_encode = face_recognition.face_encodings(face_cam, current_face)

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

            if self.counter != 0:
                if self.counter == 1 and self.face_recognized:
                    self.driver_info = db.child(f'Drivers/{self.id}').get().val()
                    print(self.driver_info)

                    bucket = storage.bucket()
                    blob = bucket.blob(f'driver images/{self.id}.png')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    self.img_driver = cv2.imdecode(array, cv2.COLOR_BGR2RGB)

                    self.counter += 1
                    self.update_driver_details()

        # Convert the frame to a PhotoImage (compatible with tkinter) and display it
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        camera_label.configure(image=photo)
        camera_label.image = photo

        # Repeat the update after a delay
        camera_label.after(30, self.update_camera, cap, camera_label, camera_id)

    def process_face_recognition(self, current_encode, current_face, face_cam, camera_label):

        with self.face_lock:  # Use the lock to ensure thread safety
            for encode_face, face_location in zip(current_encode, current_face):
                top, right, bottom, left = face_location
                matches = face_recognition.compare_faces(self.encode_list_known, encode_face)
                face_dis = face_recognition.face_distance(self.encode_list_known, encode_face)

                match_index = np.argmin(face_dis)
                if matches[match_index]:
                    self.id = self.driver_ids[match_index]
                    cv2.rectangle(face_cam, (left, top), (right, bottom), (0, 255, 0), 2)  # Draw green bbox

                    if self.counter == 0:
                        text = "Waiting for recognition..."
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
                        self.counter = 1

                    # Set the face_recognized flag to True when the face is recognized
                    self.face_recognized = True
                    self.camera_border_color2 = "#00ff00"
                    self.border_style.configure("face_border.TLabel", bordercolor=self.camera_border_color2,
                                                borderwidth=4)

                else:
                    cv2.rectangle(face_cam, (left, top), (right, bottom), (255, 0, 0), 3)  # Draw red bbox
                    self.camera_border_color2 = "#ff0000"
                    self.border_style.configure("face_border.TLabel", bordercolor=self.camera_border_color2,
                                                borderwidth=4)
                    print("Unauthorized")

    def start_computation_thread(self):
        computation_thread = threading.Thread(target=self.run_model_computation, args=(self.license_cam,))
        computation_thread.start()

    def run_model_computation(self, license_cam):
        print("")
        results = lpr_model(license_cam)[0]

        object_detected = False  # Flag to track if any object was detected in the frame

        for result in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result

            if score > threshold:
                object_detected = True  # Set the flag to True for valid detection
                cv2.rectangle(self.license_cam, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

                if self.counter == 0:

                    # Extract the license plate region
                    license_plate_region = license_cam[int(y1):int(y2), int(x1):int(x2)]

                    # Preprocess the license plate region for better OCR accuracy
                    gray_plate = cv2.cvtColor(license_plate_region, cv2.COLOR_BGR2GRAY)

                    # Apply histogram equalization to enhance contrast
                    enhanced_plate = cv2.equalizeHist(gray_plate)

                    # Apply median filtering for noise reduction
                    denoised_plate = cv2.medianBlur(enhanced_plate, 3)

                    blurred_plate = cv2.GaussianBlur(denoised_plate, (5, 5), 0)
                    threshold_plate = cv2.adaptiveThreshold(blurred_plate, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                            cv2.THRESH_BINARY_INV, 11, 2)

                    # Convert BGR to RGB for EasyOCR
                    license_plate_rgb = cv2.cvtColor(threshold_plate, cv2.COLOR_GRAY2RGB)

                    try:
                        # Perform OCR on the license plate region using EasyOCR
                        ocr_results = reader.readtext(license_plate_rgb)

                        # Extracted text from EasyOCR
                        extracted_text = ' '.join([result[1] for result in ocr_results])

                        # Remove special characters and keep only letters and numbers
                        extracted_text = re.sub(r'[^a-zA-Z0-9]', '', extracted_text)

                        # Convert the text to uppercase
                        extracted_text = extracted_text.upper()

                        extracted_text = f'{extracted_text[:3]}{extracted_text[3:7]}'

                        # Display the extracted text
                        print("EXTRACTED TEXT: ", extracted_text)

                        vehicle_data = db.child('Vehicles').get().val()

                        if extracted_text in vehicle_data:
                            self.vehicle_info = db.child(f'Vehicles/{extracted_text}').get().val()

                            print(f"License plate {extracted_text} is in the vehicles data.")
                            self.license_recognized = True
                            self.camera_border_color2 = "#00ff00"
                            self.border_style.configure("license_border.TLabel", bordercolor=self.camera_border_color2,
                                                        borderwidth=4)

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
        button_container.pack(fill=X, expand=YES, pady=(15, 10))

        btn_style = ttk.Style().configure('TButton', font=('Helvetica', 13))

        cancel_btn = ttk.Button(
            master=button_container,
            text="Cancel",
            command=self.on_cancel,
            bootstyle=DANGER,
            style=btn_style
        )
        cancel_btn.grid(row=0, column=0, padx=5)

        submit_btn = ttk.Button(
            master=button_container,
            text="Clock In",
            command=self.clock_in,
            bootstyle=SUCCESS,
            style=btn_style
        )
        submit_btn.grid(row=0, column=1, padx=5)

    # def rotateservo(self, pin, angle):
    #     board.digital[pin].write(angle)
    #     sleep(0.015)

    def clock_in(self):

        # self.plate = "NONE"
        #
        # logs_data = (
        #     self.driver_name.get(), self.id_number.get(), self.phone.get(), self.plate, self.date, self.time_in,
        #     self.time_out)
        #
        # c.execute("INSERT INTO daily_logs VALUES (?, ?, ?, ?, ?, ?, ?)", logs_data)
        # conn.commit()
        #
        self.counter = 0

        self.driver_info = None
        self.img_driver = None
        self.vehicle_info = None

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

        self.driver_image_label.configure(image=self.profile_icon)
        self.driver_image_label.image = self.profile_icon

        self.camera_border_color2 = "white"
        self.border_style.configure("face_border.TLabel", bordercolor=self.camera_border_color2,
                                    borderwidth=4)

        self.update_driver_details()

        toast = ToastNotification(
            title="Success",
            message="YEHEY SUCCESS",
            duration=3000,
        )

        toast.show_toast()

        # for i in range(0, 360):
        #     self.rotateservo(pin, i)

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

        coldata = [
            {"text": "Name", "stretch": False},
            {"text": "ID number", "stretch": False},
            {"text": "Plate number", "stretch": False},
            {"text": "Phone", "stretch": False},
            {"text": "Date", "stretch": False},
            {"text": "Time in", "stretch": False},
            {"text": "Time out", "stretch": False},
        ]

        c.execute("SELECT * FROM daily_logs")
        self.data_from_db = c.fetchall()

        rowdata = [list(row) for row in self.data_from_db]

        dt = Tableview(
            master=plate_frame,
            coldata=coldata,
            rowdata=rowdata,
            paginated=True,
            searchable=True,
            bootstyle=PRIMARY,
            stripecolor=(colors.light, None),
            autoalign=True,
        )

        dt.pack(fill=BOTH, expand=YES, padx=10, pady=10)


if __name__ == "__main__":
    app = ttk.Window("WMSU Security System", "superhero", resizable=(True, True))
    app.geometry("1400x700+350+100")
    app.grid_rowconfigure(0, weight=1)  # Make the main window expand vertically
    app.grid_columnconfigure(0, weight=1)

    s_system = SSystem(app)  # Create an instance of SSystem

    # Start the processing thread on the instance
    s_system.start_computation_thread()
    app.mainloop()