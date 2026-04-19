"""
EduManage - Student Profile Management System

Clean, modular implementation using Object-Oriented Programming principles.
Designed for clarity, maintainability, and practical academic use.

Featuring a modern GUI built with customtkinter (yes, *that* tkinter upgrade),
alongside matplotlib for visualization and pandas for structured data handling.

A “basic” project just with a slightly elevated definition of basic.
"""

import customtkinter as ctk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from datetime import datetime
import tkinter.simpledialog as tksd
import tkinter.messagebox as tkmb
import hashlib
import re
import calendar
import pandas as pd

# For PDF export (pip install reportlab)
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("reportlab not installed - PDF export will be disabled")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Main Class for UI
class EduManageApp:
    """Main app class - login and data stuff, kinda messy but works"""

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("EduManage - Student Profile System")
        self.root.geometry("1200x800")

        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)

        self.users_file = os.path.join(self.data_dir, "users.txt")
        self.passwords_file = os.path.join(self.data_dir, "passwords.txt")
        self.grades_file = os.path.join(self.data_dir, "grades.txt")
        self.eca_file = os.path.join(self.data_dir, "eca.txt")
        self.attendance_file = os.path.join(self.data_dir, "attendance.txt")

        self.load_data()  # will create demo if needed
        self.current_user = None
        self.current_role = None

        self.show_login_screen()

if __name__ == "__main__":
    print(" Starting EduManage")
    print("pip install customtkinter matplotlib pandas reportlab")
    app = EduManageApp()
    app.root.mainloop()