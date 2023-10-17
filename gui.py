import pickle
import threading
from collections import Counter
from tkinter.font import nametofont

# import torch
import cv2
from tkinter import *

import face_recognition
from ttkbootstrap.scrolled import ScrolledFrame

# import face_recognition_process
import datetime
import pytz
import numpy as np
# import easyocr
import os
from ttkbootstrap.icons import Icon
from ultralytics import YOLO
from firebase_admin import db
import database
from history_logs import *
from register import create_driver
import queue
import re
# from pyfirmata import Arduino, SERVO, util
# from time import sleep
from PIL import Image, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import Style
from ttkbootstrap.dialogs import Messagebox
from database import *
import pytesseract
from unregistered_encoding import process_images


face_best_frame = None
face_best_frame_blur = float('inf')
frame_directory = "Images/frame_images"
os.makedirs(frame_directory, exist_ok=True)


def save_best_frame():
    if face_best_frame is not None:
        frame_rgb = cv2.cvtColor(face_best_frame, cv2.COLOR_BGR2RGB)
        frame_filename = os.path.join(frame_directory, "best_frame.jpg")
        cv2.imwrite(frame_filename, frame_rgb)





