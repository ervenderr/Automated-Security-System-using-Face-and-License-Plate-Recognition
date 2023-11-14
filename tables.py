import datetime
import sqlite3
from tkinter.font import nametofont

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview

import database

tree_view = None
tree_view_logs = None


def daily_logs(plate_frame):
    global tree_view

    colors = ttk.Style().colors

    custom_style = ttk.Style()
    custom_style.configure("Custom.Treeview", font=("Helvetica", 12))

    coldata = [
        {"text": "Name", "stretch": False},
        {"text": "Type", "stretch": False},
        {"text": "ID number", "stretch": False},
        {"text": "Plate number", "stretch": False},
        {"text": "Phone", "stretch": False},
        {"text": "Date", "stretch": False},
        {"text": "Time in", "stretch": False},
    ]

    rowdata = [list(row) for row in database.fetch_daily_logs()]

    table_view = Tableview(
        master=plate_frame,
        coldata=coldata,
        rowdata=rowdata,
        paginated=True,
        searchable=True,
        stripecolor=None,
        autoalign=True,
        bootstyle=PRIMARY,
    )
    default_font = nametofont("TkDefaultFont")
    default_font.configure(size=10)
    plate_frame.option_add("*Font", default_font)

    table_view.pack(fill=BOTH, expand=YES, padx=10, pady=5)


def driver_logs_summarized(table_frame2, id_number):
    global tree_view_logs

    colors = ttk.Style().colors

    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Get today's date as a string
    today = datetime.date.today().strftime('%Y-%m-%d')

    # Fetch data from daily_logs, drivers, and vehicles tables
    c.execute('''
            SELECT 
                dl.date,
                dl.plate_number,
                COUNT(CASE WHEN dl.time_in IS NOT NULL THEN 1 END) AS entry_count,
                COUNT(CASE WHEN dl.time_out IS NOT NULL THEN 1 END) AS exit_count
            FROM daily_logs dl
            JOIN drivers d ON dl.id_number = d.id_number
            WHERE dl.id_number = ?
            ORDER BY dl.date DESC
        ''', (id_number,))

    data_logs = c.fetchall()
    conn.close()

    custom_style = ttk.Style()
    custom_style.configure("Custom.Treeview", font=("Helvetica", 12))

    coldata_logs = [
        {"text": "Date", "stretch": True},
        {"text": "Vehicle", "stretch": True},
        {"text": "Entry Count", "stretch": True, "width": 150},
        {"text": "Exit Count", "stretch": True, "width": 150},
    ]

    rowdata_logs = [list(row) for row in data_logs]

    # Specify a custom width for the Tableview (e.g., 800 pixels)
    tree_view_logs = Tableview(
        master=table_frame2,
        coldata=coldata_logs,
        rowdata=rowdata_logs,
        paginated=True,
        searchable=True,
        bootstyle=PRIMARY,
        stripecolor=None,
        autoalign=True,
    )

    logs_label_text = ttk.Label(table_frame2, text="HISTORY LOGS",
                                width=50, font=("Arial", 20, "bold"))

    logs_label_text.grid(row=3, column=0, sticky="ew")
    tree_view_logs.grid(row=4, column=0, sticky="ew", pady=10, )

    tree_view_logs.load_table_data()


def driver_authorized_vehicles(table_frame2, id_number):

    colors = ttk.Style().colors

    vehicles = database.fetch_vehicles_data(id_number)
    print(f'vehicles: {vehicles}')

    custom_style = ttk.Style()
    custom_style.configure("Custom.Treeview", font=("Helvetica", 12))

    coldata_logs = [
        {"text": "Plate number", "stretch": True},
        {"text": "Vehicle Type", "stretch": True},
        {"text": "Vehicle Color", "stretch": True, "width": 150},
        {"text": "Date ", "stretch": True, "width": 150},
    ]

    rowdata_vehicles = [list(row) for row in database.fetch_vehicles_data(id_number)]

    # Specify a custom width for the Tableview (e.g., 800 pixels)
    tree_view_vehicles = Tableview(
        master=table_frame2,
        coldata=coldata_logs,
        rowdata=rowdata_vehicles,
        paginated=True,
        searchable=True,
        bootstyle=PRIMARY,
        stripecolor=None,
        autoalign=True,
    )

    registered_label_text = ttk.Label(table_frame2, text="AUTHORIZED DRIVER",
                                      width=50, font=("Arial", 20, "bold"))

    registered_label_text.grid(row=1, column=0, sticky="ew")
    registered_label_text.grid_rowconfigure(1, weight=1)
    registered_label_text.grid_columnconfigure(1, weight=1)

    tree_view_vehicles.grid(row=2, column=0, sticky="ew", pady=10, )
    tree_view_vehicles.grid_rowconfigure(1, weight=1)
    tree_view_vehicles.grid_columnconfigure(1, weight=1)

    tree_view_vehicles.load_table_data()

    export_vehicles = tree_view_vehicles

    return export_vehicles
