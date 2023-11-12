from tkinter.font import nametofont

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview

import database


def daily_logs(plate_frame):

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