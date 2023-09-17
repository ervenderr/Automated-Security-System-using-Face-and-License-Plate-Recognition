from PIL import Image, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.tableview import Tableview
# from database import drivers_ref, vehicles_ref
import tkinter as tk
from tkinter import filedialog
from tkinter.filedialog import askopenfile

from register import create_driver


def registered_vehicle_tab(parent_tab):
    container_frame = ttk.Frame(parent_tab)
    container_frame.pack(fill=BOTH, expand=YES, padx=10)

    time_date_frame = ttk.Frame(container_frame)
    time_date_frame.pack(side=TOP, fill=BOTH, expand=NO, padx=5, pady=20)

    colors = ttk.Style().colors
    btn_style = ttk.Style().configure('TButton', font=('Helvetica', 13, "bold"))

    coldata = [
        {"text": "Picture", "stretch": True},
        {"text": "Name", "stretch": True},
        {"text": "Type", "stretch": True},
        {"text": "Phone", "stretch": True},
        {"text": "Vehicle", "stretch": False},
        {"text": "Plate number", "stretch": False},
        {"text": "Action", "stretch": False},
    ]

    rowdata = [
        ('Drivers picture', 'Erven', 'Faculty', '01853', 'picture', 'ABC123'),
        ('Drivers picture', 'Andre', 'Faculty', '01799', 'picture', 'QWE456'),
        ('Drivers picture', 'Beatrice', 'Student', '016783', 'picture', 'ASD789'),
    ]

    dt = Tableview(
        master=container_frame,
        coldata=coldata,
        rowdata=rowdata,
        paginated=True,
        searchable=True,
        bootstyle=PRIMARY,
        stripecolor=(colors.light, None),
        autoalign=True,
    )

    time_date_label1 = ttk.Label(time_date_frame, text="AASDADS",
                                width=50, font=("Arial", 20, "bold"),
                                anchor='w')
    create_new = ttk.Button(
            master=time_date_frame,
            text="➕ Create",
            command=create_driver,
            bootstyle=SUCCESS,
            style=btn_style,
    )

    time_date_label1.pack(side=LEFT, fill=BOTH, expand=YES)
    create_new.pack(side=RIGHT, fill=NONE, expand=NO)
    dt.pack(fill=BOTH, expand=YES, padx=10, pady=10)


