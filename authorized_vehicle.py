import base64
import datetime

import cv2
import numpy as np
import pytz
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap import Style
from ttkbootstrap.toast import ToastNotification

import EncodeGenerator
from database import *
from tkinter import filedialog

profile_icon = None
DEFAULT_PROFILE_ICON_PATH = "images/Profile_Icon.png"
DEFAULT_BG_PATH = "images/wmsubg.png"

img = None
filename = None


def authorized_vehicle(parent_tab, authorized_id):

    def selectPic():

        pass

    def update_time_date(label):
        pass

    colors = ttk.Style().colors

    authorized_vehicles = fetch_vehicles_data(authorized_id)

    coldata = [
        {"text": "Plate number", "stretch": True},
        {"text": "Vehicle type", "stretch": True},
        {"text": "Color", "stretch": True, "width": 150},
    ]

    rowdata = []

    # Populate rowdata with data from the database
    for vehicle_info in authorized_vehicles:
        plate_number, vehicle_type, vehicle_color = vehicle_info
        rowdata.append([plate_number, vehicle_type, vehicle_color])

    def save_driver():
        pass

    def clear():
        plate_entry.delete(0, END)
        vehicle_type_entry.delete(0, END)
        vehicle_color_entry.delete(0, END)


    def update_driver():
        pass

    def delete_driver():
        pass

    def selected_driver_row(e):

        plate_entry.delete(0, END)
        vehicle_type_entry.delete(0, END)
        vehicle_color_entry.delete(0, END)

        selected_indices = tree_view.view.selection()  # Get the selected indices
        print('selected_indices: ', selected_indices)

        selected = tree_view.view.focus()
        values = tree_view.view.item(selected, 'values')

        plate_nums = values[0]
        if len(plate_nums) < 5:
            # Add leading zeros to make it 5 characters long
            plate_nums = plate_nums.zfill(5)

        plate_entry.insert(0, values[0])
        vehicle_type_entry.insert(0, values[1])
        vehicle_color_entry.insert(0, values[2])

        print("plate: ", plate_nums)

    def selected_vehicle_row(e):
        pass

    def remove_id():
        pass

    # Configure row and column weights
    parent_tab.grid_rowconfigure(0, weight=1)
    parent_tab.grid_columnconfigure(0, weight=1)
    parent_tab.grid_columnconfigure(1, weight=1)

    # Profile driver frame
    profile_driver_frame = ttk.Frame(parent_tab, width=200)
    profile_driver_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
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

    registered_label_text = ttk.Label(time_date_frame, text="REGISTERED DRIVER AND VEHICLE",
                                      width=50, font=("Arial", 20, "bold"))

    # Center the label within the time_date_frame
    time_date_label.grid(row=0, column=0, sticky="ew")
    registered_label_text.grid(row=1, column=0, sticky="nsew")

    # Start updating the time and date label
    update_time_date(time_date_label)

    # Specify a custom width for the Tableview (e.g., 800 pixels)
    tree_view = Tableview(
        master=table_frame,
        coldata=coldata,
        rowdata=rowdata,
        paginated=True,
        searchable=True,
        bootstyle=PRIMARY,
        stripecolor=None,
        autoalign=True,
    )
    tree_view.grid(row=1, column=0, rowspan=2, sticky="nsew")
    tree_view.load_table_data()

    instruction_text2 = "Vehicle Details: "
    instruction2 = ttk.Label(profile_driver_frame, text=instruction_text2)
    instruction2.pack(fill=X, pady=(20, 5))

    plate_label = ttk.Label(profile_driver_frame, text="Plate number:")
    plate_label.pack(padx=5, pady=5, fill=BOTH)
    plate_entry = ttk.Entry(profile_driver_frame, font=('Helvetica', 13))
    plate_entry.pack(padx=5, pady=5, fill=BOTH)

    vehicle_type_label = ttk.Label(profile_driver_frame, text="Vehicle type:")
    vehicle_type_label.pack(padx=5, pady=5, fill=BOTH)
    vehicle_type_entry = ttk.Entry(profile_driver_frame, font=('Helvetica', 13))
    vehicle_type_entry.pack(padx=5, pady=5, fill=BOTH)

    vehicle_color_label = ttk.Label(profile_driver_frame, text="Vehicle color:")
    vehicle_color_label.pack(padx=5, pady=5, fill=BOTH)
    vehicle_color_entry = ttk.Entry(profile_driver_frame, font=('Helvetica', 13))
    vehicle_color_entry.pack(padx=5, pady=5, fill=BOTH)

    anchors = ttk.Style().configure('TButton', anchor='SW')

    # Create a new frame for CRUD buttons
    crud_frame = ttk.Frame(parent_tab)
    crud_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
    crud_frame.grid_rowconfigure(0, weight=1)
    crud_frame.grid_columnconfigure(0, weight=1)

    # Add CRUD buttons
    clear_button = ttk.Button(crud_frame, text="CLEAR", command=clear, bootstyle=PRIMARY)

    # Pack the buttons
    clear_button.pack(side=LEFT, padx=10, pady=10)

    style = ttk.Style()
    style.configure('Treeview', font=('Helvetica', 12), rowheight=40)

    tree_view.view.bind("<ButtonRelease-1>", selected_driver_row)
