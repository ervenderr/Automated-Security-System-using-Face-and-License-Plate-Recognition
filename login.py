from tkinter import messagebox
import ttkbootstrap as ttk
import tkinter as tk
from PIL import Image, ImageTk
import subprocess


class LoginUI(ttk.Window):
    def __init__(self):
        super().__init__(themename='superhero')

        self.title("Login")
        self.geometry("800x500")

        # Load the background image
        self.bg_image = Image.open('Images/bg.png')
        self.bg_image = ImageTk.PhotoImage(self.bg_image)

        label1 = tk.Label(self, image=self.bg_image)
        label1.place(x=0, y=0, relwidth=1, relheight=1)

        # Create a container frame for the login form
        self.container = ttk.Frame(self)
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        # Create a frame for the login form inside the container
        login_frame = ttk.Frame(self.container)
        login_frame.pack(padx=20, pady=20)

        ttk.Label(login_frame, text="USERNAME").grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.username = ttk.Entry(login_frame, width=30)
        self.username.grid(row=1, column=0, pady=(0, 10))

        ttk.Label(login_frame, text="PASSWORD").grid(row=2, column=0, sticky='w', pady=(0, 5))
        self.password = ttk.Entry(login_frame, show="*", width=30)
        self.password.grid(row=3, column=0, pady=(0, 15))

        self.submit_button = ttk.Button(login_frame, text="Login", command=self.login, bootstyle='danger')
        self.submit_button.grid(row=4, column=0, columnspan=2)

    def run_main_py(self):
        self.destroy()
        subprocess.run(["python", "ui.py"])

    def login(self):
        # Get username and password from entry fields
        username = self.username.get()
        password = self.password.get()

        print(username, password)

        # Validate login
        if self.validate_login(username, password):
            # Hide the login form container
            self.container.destroy()

            # Display "LOADING" label
            loading_label = ttk.Label(self, text="LOADING...")
            loading_label.place(relx=0.5, rely=0.5, anchor="center")

            # Run main.py after a brief delay (optional)
            self.after(1000, self.run_main_py)

        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def validate_login(self, username, password):
        valid_username = "a"
        valid_password = "a"

        if username == valid_username and password == valid_password:
            return True
        else:
            return False