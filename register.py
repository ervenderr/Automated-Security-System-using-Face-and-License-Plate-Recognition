from PIL import Image, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import Style
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.tableview import Tableview
from database import *
import tkinter as tk
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from io import BytesIO

profile_icon = None
DEFAULT_PROFILE_ICON_PATH = "images/Profile_Icon.png"


def create_driver(parent_tab):
    def selectPic():
        global img, filename
        filename = filedialog.askopenfilename(initialdir="/images", title="Select Image",
                                              filetypes=(("png images", "*.png"), ("jpg images", "*.jpg")))
        if filename:
            img = Image.open(filename)
            img = img.resize((150, 150), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(img)
            driver_image_label.image = img
            driver_image_label.config(image=driver_image_label.image)
        else:
            img = None
            driver_image_label.image = default_profile_icon
            driver_image_label.config(image=driver_image_label.image)

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


    container_frame = ttk.Frame(parent_tab, width=20)
    container_frame.pack(fill=BOTH, expand=YES)

    # Frame for the profile icon and driver details form
    profile_driver_frame = ttk.Frame(container_frame, width=20, borderwidth=2, relief='solid')
    profile_driver_frame.pack(side=TOP, fill=Y, expand=YES, padx=5, pady=10)

    # Create a container for profile icon and driver's image
    image_container = ttk.Frame(profile_driver_frame, width=20)
    image_container.pack(pady=10)

    # Profile icon label
    default_profile_icon_image = Image.open(DEFAULT_PROFILE_ICON_PATH)
    default_profile_icon_image = default_profile_icon_image.resize((150, 150), Image.Resampling.LANCZOS)
    default_profile_icon = ImageTk.PhotoImage(default_profile_icon_image)

    # Replace profile_icon_label with driver_image_label
    driver_image_label = ttk.Label(profile_driver_frame, image=default_profile_icon)
    driver_image_label.pack(pady=10)

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

    insert_image_button = ttk.Button(profile_driver_frame, text="Insert Image", bootstyle=SUCCESS)
    insert_image_button.pack(padx=5, pady=10, side=LEFT)
    insert_image_button['command'] = selectPic

    save_button = ttk.Button(profile_driver_frame, text="Save Driver",
                             command=save_driver, bootstyle=SUCCESS)
    save_button.pack(padx=5, pady=10, side=LEFT)


def create_form_entry(container, label, variable):
    form_field_container = ttk.Frame(container, width=20)
    form_field_container.pack(fill=X, pady=5)

    form_field_label = ttk.Label(master=form_field_container, text=label, width=15, font=('Helvetica', 10))
    form_field_label.grid(row=0, column=0, padx=12, pady=(0, 5), sticky="w")

    form_input = ttk.Entry(master=form_field_container, font=('Helvetica', 13))
    form_input.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="ew")

    # Make the columns of form_field_container expand relative to the container's width
    form_field_container.grid_columnconfigure(0, weight=1)  # Set weight for column 0

    # add_regex_validation(form_input, r'^[a-zA-Z0-9_]*$')

    return form_input
