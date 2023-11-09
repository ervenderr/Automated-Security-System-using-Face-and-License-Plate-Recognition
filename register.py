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
page_count = 0


def create_driver(parent_tab):
    def selectPic():

        global img, filename

        # Open a connection to the default camera
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Cannot open camera")
            return

        while True:
            ret, frame = cap.read()

            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            cv2.imshow('Capture Image', frame)

            # Capture an image when the 'Space' key is pressed
            if cv2.waitKey(1) & 0xFF == ord(' '):
                img = frame
                img = cv2.resize(img, (250, 250), interpolation=cv2.INTER_AREA)
                filename = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB for PIL
                img_pil = Image.fromarray(filename)
                img_pil_tk = ImageTk.PhotoImage(img_pil)
                driver_image_label.image = img_pil_tk
                driver_image_label.config(image=driver_image_label.image)
                break

            else:
                img = None
                driver_image_label.image = default_profile_icon
                driver_image_label.config(image=driver_image_label.image)

        cap.release()
        cv2.destroyAllWindows()

    def update_time_date(label):
        ph_tz = pytz.timezone('Asia/Manila')
        current_time = datetime.datetime.now(tz=ph_tz).strftime("%a, %Y-%m-%d %I:%M:%S %p")
        label.config(text=current_time)
        parent_tab.after(1000, lambda: update_time_date(label))

    colors = ttk.Style().colors

    drivers_data = fetch_all_driver()
    vehicles_data = fetch_all_vehicle()
    data_logs = fetch_drivers_and_vehicles()

    coldata = [
        {"text": "Name", "stretch": True},
        {"text": "Type", "stretch": True},
        {"text": "ID number", "stretch": True, "width": 150},
        {"text": "Phone", "stretch": True, "width": 150},
        {"text": "Authorized Vehicles", "stretch": True},
        {"text": "Date", "stretch": True},
    ]

    rowdata = []
    for driver_info in data_logs:
        driver_name, dtype, id_number, phone, authorized_vehicles, date = driver_info
        rowdata.append([driver_name, dtype, id_number, phone, authorized_vehicles, date])

    # table 2
    coldata2 = [
        {"text": "Plate number", "stretch": True},
        {"text": "Vehicle type", "stretch": True},
        {"text": "Vehicle color", "stretch": True},
        {"text": "Driver's ID", "stretch": True},
        {"text": "Date", "stretch": True},
    ]

    rowdata2 = []

    def save_driver():
        drivers_id = id_entry.get()
        drivers_name = name_entry.get()
        drivers_type = type_entry.get()
        driver_phone = phone_entry.get()
        driver_plate = plate_entry.get()
        driver_vehicle_type = vehicle_type_entry.get()
        driver_vehicle_color = vehicle_color_entry.get()

        # Save driver's information
        driver_data = {
            'name': drivers_name,
            'type': drivers_type,
            'id_number': int(drivers_id),
            'phone': int(driver_phone),
        }
        db.child('Drivers').child(drivers_id).set(driver_data)

        # Check if the vehicle exists in Vehicles node
        vehicle_data = db.child('Vehicles').child(driver_plate).get().val()
        if vehicle_data is None:
            vehicle_data = {
                'plate_number': driver_plate,
                'vehicle_color': driver_vehicle_color,
                'vehicle_type': driver_vehicle_type,
                'drivers': {drivers_id: True}
            }
        else:
            vehicle_data['drivers'][drivers_id] = True
        db.child('Vehicles').child(driver_plate).set(vehicle_data)

        if driver_data:
            # Convert the image to bytes
            _, buffer = cv2.imencode('.png', img)
            img_bytes = buffer.tobytes()

            cloud_filename = f"driver images/{drivers_id}.png"
            pyre_storage.child(cloud_filename).put(img_bytes)

        date = datetime.date.today().strftime("%Y-%m-%d")

        tree_view.insert_row(index=0,
                             values=[drivers_name, type, drivers_id, driver_phone, driver_plate, driver_vehicle_type,
                                     driver_vehicle_color, date])

        tree_view2.insert_row(index=0,
                              values=[driver_plate, driver_vehicle_color, driver_vehicle_type, drivers_id, date])

        tree_view.load_table_data()
        tree_view2.load_table_data()

        clear()

        EncodeGenerator.process_encodings()

        toast = ToastNotification(
            title="Success",
            message="YEHEY SUCCESS",
            duration=3000,
        )
        toast.show_toast()
        print("Driver Created")

    def clear():
        id_entry.delete(0, END)
        name_entry.delete(0, END)
        type_entry.delete(0, END)
        plate_entry.delete(0, END)
        phone_entry.delete(0, END)
        vehicle_type_entry.delete(0, END)
        vehicle_color_entry.delete(0, END)
        vehicle_drivers_entry.delete(0, END)

        driver_image_label.image = default_profile_icon
        driver_image_label.config(image=driver_image_label.image)

    def update_driver():

        drivers_id = id_entry.get()
        drivers_name = name_entry.get()
        drivers_type = type_entry.get()
        driver_phone = phone_entry.get()
        driver_plate = plate_entry.get()
        driver_vehicle_type = vehicle_type_entry.get()
        driver_vehicle_color = vehicle_color_entry.get()

        # Split input values by comma (assuming they are comma-separated)
        driver_plates = driver_plate.split(', ')
        vehicle_types = driver_vehicle_type.split(', ')
        vehicle_colors = driver_vehicle_color.split(', ')

        if (drivers_id and drivers_name and drivers_type and driver_phone) != '':
            # Save driver's information
            driver_data = {
                'name': drivers_name,
                'type': drivers_type,
                'id_number': int(drivers_id),
                'phone': int(driver_phone),
            }

            db.child('Drivers').child(drivers_id).set(driver_data)
            selected = tree_view.view.focus()
            print(f'selected {selected}')

            row_to_update = tree_view.get_row(iid=selected)

            # Update the values
            row_to_update.values = [
                name_entry.get(),
                type_entry.get(),
                id_entry.get(),
                phone_entry.get(),
                datetime.date.today().strftime("%Y-%m-%d")
            ]
            row_to_update.refresh()

            if driver_data and img is not None:
                # Convert the image to bytes
                _, buffer = cv2.imencode('.png', img)
                img_bytes = buffer.tobytes()

                cloud_filename = f"driver images/{drivers_id}.png"
                pyre_storage.child(cloud_filename).put(img_bytes)

        if (driver_plate and driver_vehicle_type and driver_vehicle_color) != '':
            # Iterate through the lists
            for i in range(len(driver_plates)):
                driver_plate_value = driver_plates[i]
                vehicle_type_value = vehicle_types[i]
                vehicle_color_value = vehicle_colors[i]

                # Check if the vehicle exists in the database
                vehicle_data = db.child('Vehicles').child(driver_plate_value).get().val()

                if not vehicle_data:
                    # Create a new vehicle entry
                    vehicle_data = {
                        'plate_number': driver_plate_value,
                        'vehicle_color': vehicle_color_value,
                        'vehicle_type': vehicle_type_value,
                        'drivers': {}
                    }

                # Add the driver to the vehicle's "drivers" field
                vehicle_data['drivers'][drivers_id] = True

                # Save the vehicle data in the database with the updated "drivers" field
                db.child('Vehicles').child(driver_plate_value).set(vehicle_data)

            selected2 = tree_view2.view.focus()
            print(f'selected2 {selected2}')

            # Get the row object
            row_to_update2 = tree_view2.get_row(iid=selected2)

            row_to_update2.values = [
                plate_entry.get(),
                vehicle_color_entry.get(),
                vehicle_type_entry.get(),
                vehicle_drivers_entry.get(),
                datetime.date.today().strftime("%Y-%m-%d")
            ]

            # Refresh the row
            row_to_update2.refresh()

        # Other steps like clearing entries, showing toast etc

        clear()

        toast = ToastNotification(
            title="Success",
            message="Driver Updated",
            duration=3000,
        )

        toast.show_toast()

        print("Driver Updated")

    def delete_driver():
        pass

    def selected_driver_row(e):

        id_entry.delete(0, END)
        name_entry.delete(0, END)
        type_entry.delete(0, END)
        # plate_entry.delete(0, END)
        phone_entry.delete(0, END)
        # vehicle_type_entry.delete(0, END)
        # vehicle_color_entry.delete(0, END)

        selected_indices = tree_view.view.selection()  # Get the selected indices
        print('selected_indices: ', selected_indices)

        selected = tree_view.view.focus()
        values = tree_view.view.item(selected, 'values')

        id_nums = values[2]
        if len(id_nums) < 5:
            # Add leading zeros to make it 5 characters long
            id_nums = id_nums.zfill(5)

        name_entry.insert(0, values[0])
        type_entry.insert(0, values[1])
        id_entry.insert(0, values[2])
        # plate_entry.insert(0, values[4])
        phone_entry.insert(0, values[3])
        # vehicle_type_entry.insert(0, values[5])
        # vehicle_color_entry.insert(0, values[6])

        print("id: ", id_nums)

        bucket = storage.bucket()
        blob = bucket.blob(f'driver images/{id_nums}.png')
        array = np.frombuffer(blob.download_as_string(), np.uint8)
        img_driver = cv2.imdecode(array, cv2.COLOR_BGR2RGB)

        driver_image = Image.fromarray(img_driver)
        driver_image = driver_image.resize((250, 250), Image.Resampling.LANCZOS)

        # Convert color channels from BGR to RGB
        driver_image = Image.merge("RGB", driver_image.split()[::-1])

        driver_image = ImageTk.PhotoImage(driver_image)

        driver_image_label.image = driver_image
        driver_image_label.config(image=driver_image_label.image)

    def selected_vehicle_row(e):

        vehicle_drivers_entry.delete(0, END)
        plate_entry.delete(0, END)
        vehicle_type_entry.delete(0, END)
        vehicle_color_entry.delete(0, END)

        selected_indices = tree_view2.view.selection()  # Get the selected indices
        print('selected_indices: ', selected_indices)

        selected = tree_view2.view.focus()
        values = tree_view2.view.item(selected, 'values')

        plate_nums = values[0]

        vehicle_drivers_entry.insert(0, values[3])
        plate_entry.insert(0, values[0])
        vehicle_type_entry.insert(0, values[1])
        vehicle_color_entry.insert(0, values[2])

        print("id: ", plate_nums)

    def remove_id():
        pass

    # Configure row and column weights
    parent_tab.grid_rowconfigure(0, weight=1)

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

    # Configure row and column weights for plate_frame
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_rowconfigure(1, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    registered_label_text = ttk.Label(table_frame, text="REGISTERED VEHICLE",
                                      width=50, font=("Arial", 20, "bold"))
    registered_label_text.grid(row=3, column=0, sticky="nsew", pady=20)

    tree_view2 = Tableview(
        master=table_frame,
        coldata=coldata2,
        rowdata=rowdata2,
        paginated=True,
        searchable=True,
        bootstyle=PRIMARY,
        stripecolor=None,
        autoalign=False,
    )
    tree_view2.grid(row=4, column=0, sticky="nsw")
    tree_view2.load_table_data()

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

    name_label = ttk.Label(profile_driver_frame, text="Name:")
    name_label.pack(padx=5, pady=5, fill=BOTH)
    name_entry = ttk.Entry(profile_driver_frame, font=('Helvetica', 13))
    name_entry.pack(padx=5, pady=5, fill=BOTH)

    type_label = ttk.Label(profile_driver_frame, text="Type:")
    type_label.pack(padx=5, pady=5, fill=BOTH)
    type_entry = ttk.Entry(profile_driver_frame, font=('Helvetica', 13))
    type_entry.pack(padx=5, pady=5, fill=BOTH)

    id_label = ttk.Label(profile_driver_frame, text="ID:")
    id_label.pack(padx=5, pady=5, fill=BOTH)
    id_entry = ttk.Entry(profile_driver_frame, font=('Helvetica', 13))
    id_entry.pack(padx=5, pady=5, fill=BOTH)

    phone_label = ttk.Label(profile_driver_frame, text="Phone:")
    phone_label.pack(padx=5, pady=5, fill=BOTH)
    phone_entry = ttk.Entry(profile_driver_frame, font=('Helvetica', 13))
    phone_entry.pack(padx=5, pady=5, fill=BOTH)

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

    vehicle_drivers = ttk.Label(profile_driver_frame, text="Authorized Drivers:")
    vehicle_drivers.pack(padx=5, pady=5, fill=BOTH)
    vehicle_drivers_entry = ttk.Entry(profile_driver_frame, font=('Helvetica', 13))
    vehicle_drivers_entry.pack(padx=5, pady=5, fill=BOTH)

    anchors = ttk.Style().configure('TButton', anchor='SW')

    insert_image_button = ttk.Button(profile_driver_frame, text="Insert Image", bootstyle=SUCCESS, style=anchors)
    insert_image_button.pack(padx=5, pady=(10), side=LEFT)
    insert_image_button['command'] = selectPic

    # Create a new frame for CRUD buttons
    crud_frame = ttk.LabelFrame(parent_tab, text='Actions')
    crud_frame.grid(row=1, column=3, sticky="nsew", padx=5, pady=5)
    crud_frame.grid_rowconfigure(0, weight=1)
    crud_frame.grid_columnconfigure(0, weight=1)

    # Daily logs table
    table_frame2 = ttk.Frame(parent_tab)

    instruction_text = "Driver Details: "
    instruction = ttk.Label(table_frame2, text=instruction_text, width=50)
    instruction.pack(fill=X, pady=10)

    pages = [table_frame, table_frame2]

    def profile_page():
        global page_count

        if not page_count > len(pages) - 2:
            for page in pages:
                page.grid_forget()

            page_count += 1
            page = pages[page_count]
            page.grid(row=0, column=3, sticky="nsew", padx=20, pady=20)
            table_frame2.grid_rowconfigure(0, weight=1)
            table_frame2.grid_columnconfigure(0, weight=1)

    # Add CRUD buttons
    create_button = ttk.Button(crud_frame, text="SAVE", command=save_driver, bootstyle=SUCCESS)
    take_photo = ttk.Button(crud_frame, text="TAKE A PHOTO", command=selectPic, bootstyle=SUCCESS)
    update_button = ttk.Button(crud_frame, text="UPDATE", command=update_driver, bootstyle=PRIMARY)
    clear_button = ttk.Button(crud_frame, text="CLEAR", command=clear, bootstyle=PRIMARY)
    delete_button = ttk.Button(crud_frame, text="DELETE", command=profile_page, bootstyle=DANGER)

    # Pack the buttons
    create_button.pack(side=LEFT, padx=10, pady=10)
    take_photo.pack(side=LEFT, padx=10, pady=10)
    update_button.pack(side=LEFT, padx=10, pady=10)
    clear_button.pack(side=LEFT, padx=10, pady=10)
    delete_button.pack(side=LEFT, padx=10, pady=10)

    style = ttk.Style()
    style.configure('Treeview', font=('Helvetica', 12), rowheight=40)

    tree_view.view.bind("<ButtonRelease-1>", selected_driver_row)
    tree_view2.view.bind("<ButtonRelease-1>", selected_vehicle_row)
