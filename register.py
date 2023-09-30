import datetime

import pytz
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from ttkbootstrap.tableview import Tableview

from database import *
from tkinter import filedialog


profile_icon = None
DEFAULT_PROFILE_ICON_PATH = "images/Profile_Icon.png"
DEFAULT_BG_PATH = "images/wmsubg.png"



def create_driver(parent_tab):
    def selectPic():

        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        date = datetime.date.today().strftime("%Y-%m-%d")
        global img, filename
        filename = filedialog.askopenfilename(initialdir="/images", title="Select Image",
                                              filetypes=(("png images", "*.png"), ("jpg images", "*.jpg")))
        if filename:
            img = Image.open(filename)
            img = img.resize((250, 250), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(img)
            driver_image_label.image = img
            driver_image_label.config(image=driver_image_label.image)
        else:
            img = None
            driver_image_label.image = default_profile_icon
            driver_image_label.config(image=driver_image_label.image)

    def update_time_date(label):
        ph_tz = pytz.timezone('Asia/Manila')
        current_time = datetime.datetime.now(tz=ph_tz).strftime("%a, %Y-%m-%d %I:%M:%S %p")
        label.config(text=current_time)
        parent_tab.after(1000, lambda: update_time_date(label))

    def daily_logs(plate_frame):

        colors = ttk.Style().colors

        coldata = [
            {"text": "Name", "stretch": True},
            {"text": "ID number", "stretch": True},
            {"text": "Plate number", "stretch": True},
            {"text": "Phone", "stretch": True},
            {"text": "Date", "stretch": True},
            {"text": "Time in", "stretch": True},
            {"text": "Time out", "stretch": True},
        ]

        rowdata = []

        # Specify a custom width for the Tableview (e.g., 800 pixels)
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
        dt.grid(row=1, column=0, rowspan=2, sticky="nsew")

        # Configure row and column weights for plate_frame
        plate_frame.grid_rowconfigure(0, weight=1)
        plate_frame.grid_rowconfigure(1, weight=1)
        plate_frame.grid_columnconfigure(0, weight=1)

    def save_driver():
        driver_id = id_entry.get()
        driver_name = name_entry.get()
        driver_phone = phone_entry.get()
        driver_plate = plate_entry.get()

        # Save driver's information
        driver_data = {
            'name': driver_name,
            'id_number': int(driver_id),
            'phone': int(driver_phone),
        }
        db.child('Drivers').child(driver_id).set(driver_data)

        # Check if the vehicle exists in Vehicles node
        vehicle_data = db.child('Vehicles').child(driver_plate).get().val()
        if vehicle_data is None:
            vehicle_data = {
                'plate_number': driver_plate,
                'drivers': {driver_id: True}
            }
        else:
            vehicle_data['drivers'][driver_id] = True
        db.child('Vehicles').child(driver_plate).set(vehicle_data)

        if driver_data:
            file = filename
            cloud_filename = f"driver images/{driver_id}.png"
            pyre_storage.child(cloud_filename).put(file)

        print("Driver Created")

    # Configure row and column weights
    parent_tab.grid_rowconfigure(0, weight=1)
    parent_tab.grid_columnconfigure(0, weight=1)
    parent_tab.grid_columnconfigure(1, weight=1)

    # Profile driver frame
    profile_driver_frame = ttk.Frame(parent_tab, width=200)
    profile_driver_frame.grid(row=0, column=1, sticky="nsew", padx=20)
    profile_driver_frame.grid_rowconfigure(0, weight=1)
    profile_driver_frame.grid_columnconfigure(0, weight=1)

    separator = ttk.Separator(parent_tab, orient=VERTICAL)
    separator.grid(row=0, column=2, rowspan=2, sticky="ns")

    # Daily logs table
    table_frame = ttk.Frame(parent_tab)
    table_frame.grid(row=0, column=3, sticky="nsew", padx=20, pady=20)
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    # time date
    time_date_frame = ttk.Frame(table_frame)
    time_date_frame.grid(row=0, column=0, sticky="nsew", pady=20)
    time_date_frame.grid_rowconfigure(0, weight=1)
    time_date_frame.grid_columnconfigure(0, weight=1)

    # Label to display the time and date
    time_date_label = ttk.Label(time_date_frame, text="",
                                width=50, font=("Arial", 20, "bold"),
                                anchor='center')

    # Center the label within the time_date_frame
    time_date_label.grid(row=0, column=0, sticky="nsew")

    # Start updating the time and date label
    update_time_date(time_date_label)

    daily_logs(table_frame)

    # Profile icon label
    default_profile_icon_image = Image.open(DEFAULT_PROFILE_ICON_PATH)
    default_profile_icon_image = default_profile_icon_image.resize((250, 250), Image.Resampling.LANCZOS)
    default_profile_icon = ImageTk.PhotoImage(default_profile_icon_image)

    # Replace profile_icon_label with driver_image_label
    driver_image_label = ttk.Label(profile_driver_frame, image=default_profile_icon)
    driver_image_label.pack(pady=(10, 30))

    instruction_text = "Driver Details: "
    instruction = ttk.Label(profile_driver_frame, text=instruction_text, width=50)
    instruction.pack(fill=X, pady=10)

    id_label = ttk.Label(profile_driver_frame, text="ID:")
    id_label.pack(padx=5, pady=5, fill=BOTH)
    id_entry = ttk.Entry(profile_driver_frame, font=('Helvetica', 13))
    id_entry.pack(padx=5, pady=5, fill=BOTH)

    name_label = ttk.Label(profile_driver_frame, text="Name:")
    name_label.pack(padx=5, pady=5, fill=BOTH)
    name_entry = ttk.Entry(profile_driver_frame, font=('Helvetica', 13))
    name_entry.pack(padx=5, pady=5, fill=BOTH)

    phone_label = ttk.Label(profile_driver_frame, text="Phone:")
    phone_label.pack(padx=5, pady=5, fill=BOTH)
    phone_entry = ttk.Entry(profile_driver_frame, font=('Helvetica', 13))
    phone_entry.pack(padx=5, pady=5, fill=BOTH)

    plate_label = ttk.Label(profile_driver_frame, text="Plate number:")
    plate_label.pack(padx=5, pady=5, fill=BOTH)
    plate_entry = ttk.Entry(profile_driver_frame, font=('Helvetica', 13))
    plate_entry.pack(padx=5, pady=5, fill=BOTH)

    vehicle_type_label = ttk.Label(profile_driver_frame, text="Vehicle type:")
    vehicle_type_label.pack(padx=5, pady=5, fill=BOTH)
    vehicle_type_label = ttk.Entry(profile_driver_frame, font=('Helvetica', 13))
    vehicle_type_label.pack(padx=5, pady=5, fill=BOTH)

    vehicle_color_label = ttk.Label(profile_driver_frame, text="Vehicle color:")
    vehicle_color_label.pack(padx=5, pady=5, fill=BOTH)
    vehicle_color_label = ttk.Entry(profile_driver_frame, font=('Helvetica', 13))
    vehicle_color_label.pack(padx=5, pady=5, fill=BOTH)

    insert_image_button = ttk.Button(profile_driver_frame, text="Insert Image", bootstyle=SUCCESS)
    insert_image_button.pack(padx=5, pady=10, side=LEFT)
    insert_image_button['command'] = selectPic

    save_button = ttk.Button(profile_driver_frame, text="Save Driver",
                             command=save_driver, bootstyle=SUCCESS)
    save_button.pack(padx=5, pady=10, side=LEFT)

