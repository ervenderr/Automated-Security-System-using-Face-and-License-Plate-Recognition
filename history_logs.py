import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.validation import add_regex_validation



def history_logs_tab(parent_tab):
    container_frame = ttk.Frame(parent_tab)
    container_frame.pack(fill=BOTH, expand=YES)

    colors = ttk.Style().colors

    coldata = [
        {"text": "Name", "stretch": True},
        {"text": "ID number", "stretch": False},
        {"text": "Plate number", "stretch": False},
        {"text": "Date", "stretch": False},
        {"text": "Time in", "stretch": False},
        {"text": "Time out", "stretch": False},
    ]

    rowdata = [
        ('Erven', '01853', 'ABC123', '2023-8-8', '7:00 AM', '5:00 PM'),
        ('Andre', '01799', 'QWE456', '2023-8-8', '7:00 AM', '5:00 PM'),
        ('Beatrice', '016783', 'ASD789', '2023-8-8', '7:00 AM', '5:00 PM'),
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
    dt.pack(fill=BOTH, expand=YES, padx=10, pady=10)
