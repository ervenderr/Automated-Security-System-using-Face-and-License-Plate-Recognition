import tkinter as tk
from tkinter import ttk


root = tk.Tk()

style = ttk.Style()
style.configure("My.Treeview", rowheight=35)

treeview_test = ttk.Treeview(root, style="My.Treeview")
treeview_test.pack()

treeview_test.insert(parent="", index=tk.END, text="First row")
treeview_test.insert(parent="", index=tk.END, text="Second row")

root.mainloop()