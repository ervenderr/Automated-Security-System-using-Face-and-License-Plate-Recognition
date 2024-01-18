import cv2
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.icons import Icon
from ttkbootstrap.tableview import Tableview
from ttkbootstrap import Style
from ttkbootstrap.toast import ToastNotification
import EncodeGenerator
import database
from database import *

profile_icon = None
DEFAULT_PROFILE_ICON_PATH = "images/Profile_Icon.png"
DEFAULT_BG_PATH = "images/wmsubg.png"

conn = sqlite3.connect('drivers.db')
c = conn.cursor()

date = datetime.date.today().strftime("%Y-%m-%d")
ph_tz = pytz.timezone('Asia/Manila')
current_time = datetime.datetime.now(tz=ph_tz).strftime("%H:%M:%S")

captured_image = None
copied_img_file = None
update_count = 0
current_state = True


def history_logs(parent_tab):
    def hist_selectPic():
        global captured_image

        # Open a connection to the default camera
        cap = cv2.VideoCapture(1)

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
                captured_image = frame
                images = cv2.resize(captured_image, (200, 200), interpolation=cv2.INTER_AREA)
                filename = cv2.cvtColor(images, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB for PIL
                img_pil = Image.fromarray(filename)
                img_pil_tk = ImageTk.PhotoImage(img_pil)
                driver_image_label.image = img_pil_tk
                driver_image_label.config(image=driver_image_label.image)
                break

            else:
                images = None
                driver_image_label.image = default_profile_icon
                driver_image_label.config(image=driver_image_label.image)

        cv2.destroyAllWindows()

    def update_time_date(label):
        ph_tz = pytz.timezone('Asia/Manila')
        current_time = datetime.datetime.now(tz=ph_tz).strftime("%a, %b-%d-%Y %I:%M:%S %p")
        label.config(text=current_time)
        parent_tab.after(1000, lambda: update_time_date(label))

    coldata = [
        {"text": "Name", "stretch": True},
        {"text": "Category", "stretch": True},
        {"text": "ID number", "stretch": True, "width": 150},
        {"text": "Phone", "stretch": True},
        {"text": "Plate number", "stretch": True, "width": 150},
        {"text": "Date", "stretch": True, },
        {"text": "Time in", "stretch": True, },
        {"text": "Time out", "stretch": True, },
    ]

    rowdata = [list(row) for row in database.fetch_all_logs()]

    def hist_save_driver():
        drivers_id = id_entry.get()
        drivers_type = type_entry.get()
        drivers_name = name_entry.get()
        driver_phone = phone_entry.get()
        driver_plate = plate_entry.get()
        driver_vehicle_type = vehicle_type_entry.get()
        driver_vehicle_color = vehicle_color_entry.get()

        if drivers_name != '' and drivers_id != '' and drivers_type != '' and driver_phone != '':

            # # Save driver's information
            # # Check if the driver with the given ID already exists in the database
            # existing_driver = fetch_driver(drivers_id)
            #
            # if existing_driver:
            #     # Driver already exists, update the information
            #     c.execute('UPDATE drivers SET name=?, type=?, phone=?, date=? WHERE id_number=?',
            #               (drivers_name, drivers_type, driver_phone, drivers_id, date))
            # else:
            #     # Driver doesn't exist, insert a new record
            #     c.execute('INSERT INTO drivers (id_number, name, type, phone, date) VALUES (?, ?, ?, ?, ?)',
            #               (drivers_id, drivers_name, drivers_type, driver_phone, date))
            #
            # # Check if the vehicle exists in Vehicles table
            # vehicle_data = fetch_vehicle(driver_plate)
            #
            # if vehicle_data is None:
            #     # Vehicle doesn't exist, insert a new record
            #     vehicle_data = {
            #         'plate_number': driver_plate,
            #         'vehicle_color': driver_vehicle_color,
            #         'vehicle_type': driver_vehicle_type,
            #     }
            #     c.execute('INSERT INTO vehicles (plate_number, vehicle_color, vehicle_type) VALUES (?, ?, ?)',
            #               (driver_plate, driver_vehicle_color, driver_vehicle_type))
            #
            # # Save the association between the driver and the vehicle in driver_vehicle table
            # c.execute('SELECT * FROM driver_vehicle WHERE driver_id = ? AND plate_number = ?',
            #           (drivers_id, driver_plate))
            # existing_association = c.fetchone()
            #
            # if existing_association:
            #     # Update the existing record if the association already exists
            #     c.execute('UPDATE driver_vehicle SET plate_number = ? WHERE driver_id = ?',
            #               (driver_plate, drivers_id))
            # elif drivers_id != '' and driver_plate != '':
            #     # Insert a new record if the association doesn't exist
            #     c.execute('INSERT INTO driver_vehicle (driver_id, plate_number) VALUES (?, ?)',
            #               (drivers_id, driver_plate))
            #
            # # Commit the changes and close the connection
            # conn.commit()
            # conn.close()
            #
            # if captured_image is not None and drivers_id != 'None':
            #     # Convert frame to PIL image
            #     filename = f'Images/registered driver/{drivers_id}.png'
            #     file_image = cv2.cvtColor(captured_image, cv2.COLOR_BGR2RGB)
            #     pil_image = Image.fromarray(file_image)
            #
            #     # Save image
            #     pil_image.save(filename)
            #     print('pil_image', copied_img_file)

            selected = tree_view.view.focus()
            values = tree_view.view.item(selected, 'values')
            print(f'selected {selected}')

            row_to_update = tree_view.get_row(iid=selected)

            ph_tz = pytz.timezone('Asia/Manila')
            datess = datetime.date.today().strftime("%Y-%m-%d")
            current_time = datetime.datetime.now(tz=ph_tz).strftime("%I:%M %p")

            # Update the values
            row_to_update.values = [
                name_entry.get(),
                type_entry.get(),
                id_entry.get(),
                phone_entry.get(),
                values[4],
                values[5],
                values[6],
                values[7]
            ]
            tree_view.load_table_data()

            EncodeGenerator.process_encodings()

            clear()

            toast = ToastNotification(
                title="Success",
                message="DRIVER UPDATED",
                duration=3000,
            )
            toast.show_toast()
            print("Driver Created")

        else:

            Messagebox.ok("Driver details Cannot be Empty", 'INPUT ERROR',
                          icon=Icon.error)
            print('messad')

    def clear():
        id_text.configure(text='')
        name_text.configure(text='')
        type_text.configure(text='')
        plate_text.configure(text='')
        phone_text.configure(text='')
        vehicle_type_text.configure(text='')
        vehicle_color_text.configure(text='')

        id_entry.delete(0, END)
        name_entry.delete(0, END)
        type_entry.delete(0, END)
        plate_entry.delete(0, END)
        phone_entry.delete(0, END)
        vehicle_type_entry.delete(0, END)
        vehicle_color_entry.delete(0, END)

        driver_image_label.image = default_profile_icon
        driver_image_label.config(image=driver_image_label.image)
        tree_view.load_table_data()

    def update_driver():
        pass

    def delete_driver():
        tree_view.export_all_records()

    def selected_row(e):
        global driver_image
        global copied_img_file
        id_entry.delete(0, END)
        name_entry.delete(0, END)
        type_entry.delete(0, END)
        plate_entry.delete(0, END)
        phone_entry.delete(0, END)
        vehicle_type_entry.delete(0, END)
        vehicle_color_entry.delete(0, END)

        logs_data = fetch_all_logs()
        print("Name:", logs_data[0])

        # Iterate through the data and print the name
        for log_entry in logs_data:
            print("Name:", log_entry[0])

        selected_indices = tree_view.view.selection()  # Get the selected indices
        print('selected_indices: ', selected_indices)

        selected = tree_view.view.focus()
        values = tree_view.view.item(selected, 'values')

        id_nums = values[2]

        if len(id_nums) < 5:
            # Add leading zeros to make it 5 characters long
            id_nums = id_nums.zfill(5)

        plate_nums = values[4]

        print(f'id_nums: {id_nums}')
        print(f'plate_nums: {plate_nums}')

        driver_info = fetch_driver(id_nums)
        vehicle_info = fetch_vehicle(plate_nums)

        print(driver_info)
        print(vehicle_info)

        if driver_info is not None:

            name_text.configure(text=values[0])
            type_text.configure(text=values[1])
            id_text.configure(text=values[2])
            phone_text.configure(text=values[3])

            name_entry.insert(0, values[0])
            type_entry.insert(0, values[1])
            id_entry.insert(0, values[2])
            phone_entry.insert(0, values[3])

            if id_nums != '0None':
                file_path = f'Images/registered driver/{id_nums}.png'
            else:
                file_path = f'Images/unregistered driver/{plate_nums}.jpg'

            non_driver_image = Image.open(file_path)

            copied_img_file = non_driver_image.copy()

            driver_image = non_driver_image.resize((200, 200), Image.Resampling.LANCZOS)

            driver_image = ImageTk.PhotoImage(driver_image)

            driver_image_label.image = driver_image
            driver_image_label.config(image=driver_image_label.image)
            print(driver_image)

        if plate_nums != '0None':
            for log_entry in vehicle_info:
                plate_text.configure(text=log_entry[0])
                vehicle_type_text.configure(text=log_entry[1])
                vehicle_color_text.configure(text=log_entry[2])

                plate_entry.insert(0, log_entry[0])
                vehicle_type_entry.insert(0, log_entry[1])
                vehicle_color_entry.insert(0, log_entry[2])

        if plate_nums == '0None':
            plate_entry.insert(0, values[3])
            plate_text.configure(text=values[3])

        driver_image_label.config(image=driver_image)
        driver_image_label.image = driver_image

    # Configure row and column weights
    parent_tab.grid_rowconfigure(0, weight=1)
    parent_tab.grid_columnconfigure(0, weight=1)
    parent_tab.grid_columnconfigure(1, weight=1)

    # Profile driver frame
    profile_driver_frame = ttk.Frame(parent_tab, width=200)
    profile_driver_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
    profile_driver_frame.grid_rowconfigure(0, weight=1)
    profile_driver_frame.grid_columnconfigure(0, weight=1)

    # Frame for driver_image_label
    image_frame = ttk.Frame(profile_driver_frame)
    image_frame.pack(pady=(10, 0))

    profile_frame = ttk.Frame(profile_driver_frame)
    profile_frame.pack(pady=(10, 0))

    profile_frame2 = ttk.Frame(profile_driver_frame)

    update_pages = [profile_frame, profile_frame2]

    def update_drivers():
        global current_state, update_count

        # profile_frame.pack_forget()

        if not update_count > len(update_pages) - 2:
            for page in update_pages:
                page.pack_forget()

            update_count += 1
            page = update_pages[update_count]
            page.pack(pady=(10, 0))

            # driver_details(profile_frame2)

        current_state = True
        print(current_state)

    def list_profile_page():
        global update_count

        if not update_count == 2:
            for page in update_pages:
                page.grid_forget()
                profile_frame2.pack_forget()

            update_count -= 1
            page = update_pages[update_count]
            page.grid(row=0, column=3, sticky="nsew", padx=20, pady=20)
            table_frame.grid_rowconfigure(0, weight=1)
            table_frame.grid_columnconfigure(0, weight=1)

            profile_frame.pack(pady=(10, 0))

        clear()

    def apply_date_range_filter():
        start_date = filter_search.entry.get()
        end_date = filter_search2.entry.get()

        # print(start_date, end_date)


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

    filter_frame = ttk.Frame(time_date_frame)
    filter_frame.grid(row=2, column=0, sticky="nsew", pady=20)

    # Label to display the time and date
    time_date_label = ttk.Label(time_date_frame, text="",
                                width=50, font=("Arial", 20, "bold"),
                                anchor='center')

    registered_label_text = ttk.Label(time_date_frame, text="HISTORY LOGS",
                                      width=50, font=("Arial", 20, "bold"))

    filter_label = ttk.Label(filter_frame, text="Date range:")
    filter_label.grid(row=0, column=0, sticky="nsew")

    filter_date_str = 'Sun, Dec-03-2023'
    filter_date = datetime.datetime.strptime(filter_date_str, '%a, %b-%d-%Y')

    filter_search = ttk.DateEntry(master=filter_frame, dateformat='%a, %b-%d-%Y', startdate=filter_date,
                                  firstweekday=2)
    filter_search.grid(row=1, column=0, sticky="nw")

    filter_to = ttk.Label(filter_frame, text="TO", font=("Arial", 13, "bold"))
    filter_to.grid(row=1, column=1, sticky="nw", padx=5)

    filter_search2 = ttk.DateEntry(master=filter_frame, dateformat='%a, %b-%d-%Y', startdate=filter_date,
                                   firstweekday=2)
    filter_search2.grid(row=1, column=2, sticky="nw")

    filter_to = ttk.Button(filter_frame, text="Apply", command=apply_date_range_filter, bootstyle=SUCCESS)
    filter_to.grid(row=1, column=3, sticky="nw", padx=5)

    # Center the label within the time_date_frame
    time_date_label.grid(row=0, column=0, sticky="nsew")
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
        stripecolor=(),
        autoalign=True,
    )
    tree_view.grid(row=1, column=0, rowspan=2, sticky="nsew")
    tree_view.load_table_data()

    # Configure row and column weights for plate_frame
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_rowconfigure(1, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    # Profile icon label
    default_profile_icon_image = Image.open(DEFAULT_PROFILE_ICON_PATH)
    default_profile_icon_image = default_profile_icon_image.resize((200, 200), Image.Resampling.LANCZOS)
    default_profile_icon = ImageTk.PhotoImage(default_profile_icon_image)

    # Replace profile_icon_label with driver_image_label
    driver_image_label = ttk.Label(image_frame, image=default_profile_icon)
    driver_image_label.pack(pady=(10, 30))

    instruction_text = "Driver Details: "
    instruction = ttk.Label(profile_frame, text=instruction_text, width=50)
    instruction.pack(fill=X, pady=10)

    name_label = ttk.Label(profile_frame, text="Name:")
    name_label.pack(padx=5, pady=5, fill=BOTH)
    name_text = ttk.Label(profile_frame, font=('Helvetica', 15, 'bold'), foreground='#20374C',
                          borderwidth=0, relief="solid", background='#ffffff', padding=(5, 1))
    name_text.pack(padx=5, pady=5, fill=BOTH)

    type_label = ttk.Label(profile_frame, text="Category:")
    type_label.pack(padx=5, pady=5, fill=BOTH)
    category = ["Staff", "Faculty", "Independents", "Graduate Students"]  # Replace with your options
    type_text = ttk.Label(profile_frame, font=('Helvetica', 15, 'bold'), foreground='#20374C',
                          borderwidth=0, relief="solid", background='white', padding=3)
    type_text.pack(padx=5, pady=5, fill=BOTH)

    id_label = ttk.Label(profile_frame, text="ID:")
    id_label.pack(padx=5, pady=5, fill=BOTH)
    id_text = ttk.Label(profile_frame, font=('Helvetica', 15, 'bold'), foreground='#20374C',
                        borderwidth=0, relief="solid", background='white', padding=3)
    id_text.pack(padx=5, pady=5, fill=BOTH)

    phone_label = ttk.Label(profile_frame, text="Phone:")
    phone_label.pack(padx=5, pady=5, fill=BOTH)
    phone_text = ttk.Label(profile_frame, font=('Helvetica', 15, 'bold'), foreground='#20374C',
                           borderwidth=0, relief="solid", background='white', padding=3)
    phone_text.pack(padx=5, pady=5, fill=BOTH)

    instruction_text2 = "Vehicle Details: "
    instruction2 = ttk.Label(profile_frame, text=instruction_text2)
    instruction2.pack(fill=X, pady=(20, 5))

    plate_label = ttk.Label(profile_frame, text="Plate number:")
    plate_label.pack(padx=5, pady=5, fill=BOTH)
    plate_text = ttk.Label(profile_frame, font=('Helvetica', 15, 'bold'), foreground='#20374C',
                           borderwidth=0, relief="solid", background='white', padding=3)
    plate_text.pack(padx=5, pady=5, fill=BOTH)

    vehicle_type_label = ttk.Label(profile_frame, text="Vehicle type:")
    vehicle_type_label.pack(padx=5, pady=5, fill=BOTH)
    vehicle_type_text = ttk.Label(profile_frame, font=('Helvetica', 15, 'bold'), foreground='#20374C',
                                  borderwidth=0, relief="solid", background='white', padding=3)
    vehicle_type_text.pack(padx=5, pady=5, fill=BOTH)

    vehicle_color_label = ttk.Label(profile_frame, text="Vehicle color:")
    vehicle_color_label.pack(padx=5, pady=5, fill=BOTH)
    vehicle_color_text = ttk.Label(profile_frame, font=('Helvetica', 15, 'bold'), foreground='#20374C',
                                   borderwidth=0, relief="solid", background='white', padding=3)
    vehicle_color_text.pack(padx=5, pady=5, fill=BOTH)

    # Create a new frame for CRUD buttons
    crud_frame = ttk.LabelFrame(parent_tab, text='Actions')
    crud_frame.grid(row=1, column=3, sticky="nsew", padx=5, pady=5)
    crud_frame.grid_rowconfigure(0, weight=1)
    crud_frame.grid_columnconfigure(0, weight=1)

    # Add CRUD buttons
    create_button = ttk.Button(crud_frame, text="SAVE", command=hist_save_driver, bootstyle=SUCCESS)
    take_photo = ttk.Button(crud_frame, text="TAKE A PHOTO", command=hist_selectPic, bootstyle=SUCCESS)
    clear_button = ttk.Button(crud_frame, text="CLEAR", command=clear, bootstyle=PRIMARY)
    delete_button = ttk.Button(crud_frame, text="PRINT", command=delete_driver, bootstyle=DANGER)

    # Pack the buttons
    create_button.pack(side=LEFT, padx=10, pady=10)
    take_photo.pack(side=LEFT, padx=10, pady=10)
    clear_button.pack(side=LEFT, padx=10, pady=10)
    delete_button.pack(side=LEFT, padx=10, pady=10)

    instruction_text = "Driver Detailss: "
    instruction = ttk.Label(profile_frame2, text=instruction_text, width=50)
    instruction.pack(fill=X, pady=10)

    name_label = ttk.Label(profile_frame2, text="Name:")
    name_label.pack(padx=5, pady=5, fill=BOTH)
    name_entry = ttk.Entry(profile_frame2, font=('Helvetica', 13))
    name_entry.pack(padx=5, pady=5, fill=BOTH)

    type_label = ttk.Label(profile_frame2, text="Category:")
    type_label.pack(padx=5, pady=5, fill=BOTH)
    category = ["Staff", "Faculty", "Independents", "Graduate Students"]  # Replace with your options
    type_entry = ttk.Combobox(master=profile_frame2, font=('Helvetica', 13), values=category)
    type_entry.pack(padx=5, pady=5, fill=BOTH)

    id_label = ttk.Label(profile_frame2, text="ID:")
    id_label.pack(padx=5, pady=5, fill=BOTH)
    id_entry = ttk.Entry(profile_frame2, font=('Helvetica', 13))
    id_entry.pack(padx=5, pady=5, fill=BOTH)

    phone_label = ttk.Label(profile_frame2, text="Phone:")
    phone_label.pack(padx=5, pady=5, fill=BOTH)
    phone_entry = ttk.Entry(profile_frame2, font=('Helvetica', 13))
    phone_entry.pack(padx=5, pady=5, fill=BOTH)

    instruction_text2 = "Vehicle Details: "
    instruction2 = ttk.Label(profile_frame2, text=instruction_text2)
    instruction2.pack(fill=X, pady=(20, 5))

    plate_label = ttk.Label(profile_frame2, text="Plate number:")
    plate_label.pack(padx=5, pady=5, fill=BOTH)
    plate_entry = ttk.Entry(profile_frame2, font=('Helvetica', 13))
    plate_entry.pack(padx=5, pady=5, fill=BOTH)

    vehicle_type_label = ttk.Label(profile_frame2, text="Vehicle type:")
    vehicle_type_label.pack(padx=5, pady=5, fill=BOTH)
    vehicle_type_entry = ttk.Entry(profile_frame2, font=('Helvetica', 13))
    vehicle_type_entry.pack(padx=5, pady=5, fill=BOTH)

    vehicle_color_label = ttk.Label(profile_frame2, text="Vehicle color:")
    vehicle_color_label.pack(padx=5, pady=5, fill=BOTH)
    vehicle_color_entry = ttk.Entry(profile_frame2, font=('Helvetica', 13))
    vehicle_color_entry.pack(padx=5, pady=5, fill=BOTH)

    take_photo['command'] = hist_selectPic

    tree_view.view.bind("<ButtonRelease-1>", selected_row)

