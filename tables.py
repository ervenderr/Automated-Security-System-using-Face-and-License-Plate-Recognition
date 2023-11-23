import datetime
import sqlite3
from tkinter.font import nametofont

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview

import database

tree_view_logs = None
table_views = None
all_table_logs = None


def driver_logs_summarized(table_frame2, id_number):
    global export_logs

    colors = ttk.Style().colors

    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()

    # Get today's date as a string
    today = datetime.date.today().strftime('%Y-%m-%d')

    # Fetch data from daily_logs, drivers, and vehicles tables
    c.execute('''
        SELECT
            dl.date,
            COALESCE(SUM(CASE WHEN dl.time_in IS NOT NULL THEN 1 ELSE 0 END), 0) AS entry_count,
            COALESCE(SUM(CASE WHEN dl.time_out IS NOT NULL THEN 1 ELSE 0 END), 0) AS exit_count
        FROM daily_logs dl
        JOIN drivers d ON dl.id_number = d.id_number
        WHERE dl.id_number = ?
        GROUP BY dl.date
        ORDER BY dl.date DESC
    ''', (id_number,))

    data_logs = c.fetchall()
    conn.close()

    coldata_logs = [
        {"text": "Date", "stretch": True},
        {"text": "Entry Count", "stretch": True},
        {"text": "Exit Count", "stretch": True},
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

    export_logs = tree_view_logs

    tree_view_logs.view.tag_configure('TButton', background='darkblue', foreground='white')

    for item in tree_view_logs.view.get_children():
        # Extracting the corresponding row data for the current item
        row_index = tree_view_logs.view.index(item)
        row_data = rowdata_logs[row_index]

        # Fetching individual logs for the current date and id_number
        indi_logs = database.fetch_indi_logs(row_data[0], id_number)

        # Inserting the children with time_in and time_out values
        for indi_log in indi_logs:
            tree_view_logs.view.insert(item, 'end', values=(indi_log[0], indi_log[1], indi_log[2]), tags=('TButton',))

    return export_logs


def driver_authorized_vehicles(table_frame2, id_number):
    global export_vehicles

    colors = ttk.Style().colors

    vehicles = database.fetch_vehicles_data(id_number)
    print(f'vehicles: {vehicles}')

    coldata_logs = [
        {"text": "Plate number", "stretch": True},
        {"text": "Vehicle Type", "stretch": True},
        {"text": "Vehicle Color", "stretch": True},
        {"text": "Date ", "stretch": True},
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

    registered_label_text = ttk.Label(table_frame2, text="AUTHORIZED VEHICLES",
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


def on_row_click(event):
    selected_item = export_vehicles.view.selection()[0]

    # Lookup time values for row
    date = tree_view_logs.item(selected_item)['values'][0]
    times = fetch_times(date)

    # Create label to display times
    time_label = ttk.Label(tree_view_logs, text="\n".join(times))

    # Set as row detail
    tree_view_logs.set_row_detail(selected_item, time_label)


# Fetch time values
def fetch_times(date):
    conn = sqlite3.connect('drivers.db')
    c = conn.cursor()
    times = []

    c.execute("""SELECT time_in, time_out, plate_number 
              FROM daily_logs 
              WHERE date = ?""", (date,))

    for row in c.fetchall():
        times.append(row[0])
        times.append(row[1])
        times.append(row[2])

    return times


def all_logs(table_frame):

    global all_table_logs

    colors = ttk.Style().colors

    coldata = [
        {"text": "Name", "stretch": True},
        {"text": "Category", "stretch": True},
        {"text": "ID number", "stretch": True, "width": 150},
        {"text": "Plate number", "stretch": True},
        {"text": "Phone", "stretch": True, "width": 150},
        {"text": "Date", "stretch": True, },
        {"text": "Time in", "stretch": True, },
        {"text": "Time out", "stretch": True, },
    ]

    rowdata = [list(row) for row in database.fetch_all_logs()]

    all_table_view = Tableview(
        master=table_frame,
        coldata=coldata,
        rowdata=rowdata,
        paginated=True,
        searchable=True,
        bootstyle=PRIMARY,
        stripecolor=(),
        autoalign=True,
    )
    all_table_view.grid(row=1, column=0, rowspan=2, sticky="nsew")
    all_table_view.load_table_data()

    all_table_logs = all_table_view