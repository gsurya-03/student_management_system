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

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def load_data(self):
        """load or create defaults - including demo if no data"""
        if not os.path.exists(self.users_file) or os.path.getsize(self.users_file) == 0:
            self.create_demo_data()
        else:
            self.users = self.safe_load(self.users_file, {})
            self.passwords = self.safe_load(self.passwords_file, {})
            self.grades = self.safe_load(self.grades_file, {})
            self.eca = self.safe_load(self.eca_file, {})
            self.attendance = self.safe_load(self.attendance_file, {})

        # make sure students have data
        for username, info in self.users.items():
            if info.get("role") == "student":
                self.grades.setdefault(username, {"Math": 0, "Physics": 0, "Chemistry": 0, "Biology": 0, "English": 0})
                self.eca.setdefault(username, [])
                self.attendance.setdefault(username, [])

    def create_demo_data(self):
        """Create demo accounts when no data exists"""
        print("Creating demo accounts because no data found...")
        self.users = {
            "admin": {"full_name": "Administrator", "role": "admin", "email": "admin@edumanage.com"},
            "teacher1": {"full_name": "Teacher One", "role": "teacher", "email": "teacher1@edumanage.com"},
            "student1": {"full_name": "Student One", "role": "student", "email": "student1@edumanage.com"}
        }
        self.passwords = {
            "admin": self.hash_password("admin123"),
            "teacher1": self.hash_password("teacher123"),
            "student1": self.hash_password("student123")
        }
        self.grades = {
            "student1": {"Math": 85, "Physics": 78, "Chemistry": 92, "Biology": 88, "English": 90}
        }
        self.eca = {
            "student1": [
                {"activity": "Basketball", "description": "School team captain", "date": "2025-01-15", "points": 15},
                {"activity": "Debate Club", "description": "National winner", "date": "2025-02-20", "points": 18}
            ]
        }
        self.attendance = {
            "student1": [
                {"date": "2025-04-01", "status": "Present"},
                {"date": "2025-04-02", "status": "Absent"}
            ]
        }

        print("Demo accounts created! Use:")
        print("   admin / admin123")
        print("   teacher1 / teacher123")
        print("   student1 / student123")

    def safe_load(self, filename: str, default_data: dict):
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            self.safe_save(filename, default_data)
            return default_data
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            self.safe_save(filename, default_data)
            return default_data

    def safe_save(self, filename: str, data: dict):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def save_data(self):
        self.safe_save(self.users_file, self.users)
        self.safe_save(self.passwords_file, self.passwords)
        self.safe_save(self.grades_file, self.grades)
        self.safe_save(self.eca_file, self.eca)
        self.safe_save(self.attendance_file, self.attendance)

    def is_strong_password(self, password: str) -> bool:
        if len(password) < 8:
            return False
        if not (re.search(r"[A-Z]", password) and re.search(r"[a-z]", password) and re.search(r"\d", password)):
            return False
        return True

    def show_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        frame = ctk.CTkFrame(self.root, corner_radius=20)
        frame.pack(pady=100, padx=200, fill="both", expand=True)

        ctk.CTkLabel(frame, text="🎓 EduManage", font=ctk.CTkFont(size=32, weight="bold")).pack(pady=30)
        ctk.CTkLabel(frame, text="Student Profile Management System",
                     font=ctk.CTkFont(size=16)).pack(pady=10)

        self.username_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=300)
        self.username_entry.pack(pady=12, padx=40)

        self.password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=300)
        self.password_entry.pack(pady=12, padx=40)

        ctk.CTkButton(frame, text="Login", width=300, command=self.handle_login).pack(pady=30)

        ctk.CTkLabel(frame, text="Demo Accounts:\nadmin / admin123\nteacher1 / teacher123\nstudent1 / student123",
                     text_color="gray", justify="center").pack(pady=10)

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username in self.passwords and self.passwords[username] == self.hash_password(password):
            self.current_user = username
            self.current_role = self.users[username]["role"]
            tkmb.showinfo("Success", f"Welcome, {self.users[username]['full_name']}!")

            if self.current_role == "admin":
                AdminDashboard(self.root, self).show()
        else:
            tkmb.showerror("Error", "Invalid username or password!")

    def logout(self):
        if tkmb.askyesno("Logout", "Are you sure you want to logout?"):
            self.current_user = None
            self.current_role = None
            self.show_login_screen()


#  ADMIN DASHBOARD 
class AdminDashboard:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app
        self.main_frame = None

    def show(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_sidebar()
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.show_dashboard()

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        ctk.CTkLabel(sidebar, text="EduManage", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30)
        ctk.CTkButton(sidebar, text="Dashboard", command=self.show_dashboard, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Manage Users", command=self.show_manage_users, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Manage Grades", command=self.show_manage_grades, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Manage ECA", command=self.show_manage_eca, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Analytics", command=self.show_analytics, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Export to PDF", command=self.export_pdf, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Logout", command=self.main_app.logout, fg_color="red", height=40).pack(side="bottom", pady=30, padx=20, fill="x")

    def clear_main_frame(self):
        if self.main_frame:
            for widget in self.main_frame.winfo_children():
                widget.destroy()

    def show_dashboard(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Admin Dashboard", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=30)
        if self.main_app.grades:
            subjects = ["Math", "Physics", "Chemistry", "Biology", "English"]
            avgs = []
            for sub in subjects:
                total = sum(self.main_app.grades[s].get(sub, 0) for s in self.main_app.grades)
                count = len([s for s in self.main_app.grades if sub in self.main_app.grades[s]])
                avgs.append(round(total / count, 1) if count > 0 else 0)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(subjects, avgs, color="#00ffaa")
            ax.set_title("Overall Average Performance")
            ax.set_ylabel("Average Score")
            ax.set_ylim(0, 100)
            canvas = FigureCanvasTkAgg(fig, self.main_frame)
            canvas.get_tk_widget().pack(pady=20, fill="both", expand=True)
            canvas.draw()

    def show_manage_users(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Manage Users", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        ctk.CTkButton(self.main_frame, text="+ Add New User", command=self.add_new_user).pack(pady=10)
        for username, info in list(self.main_app.users.items()):
            frame = ctk.CTkFrame(self.main_frame)
            frame.pack(pady=8, padx=80, fill="x")
            ctk.CTkLabel(frame, text=f"{username} — {info['full_name']} ({info['role']})").pack(side="left", padx=20)
            if username != "admin":
                ctk.CTkButton(frame, text="Delete", fg_color="red", width=80,
                              command=lambda u=username: self.delete_user(u)).pack(side="right", padx=10)

    def add_new_user(self):
        username = tksd.askstring("Add User", "Username:", parent=self.root)
        if not username or username in self.main_app.users:
            tkmb.showerror("Error", "Username already exists or is empty")
            return
        name = tksd.askstring("Add User", "Full Name:", parent=self.root)
        role = tksd.askstring("Add User", "Role (student/teacher/admin):", initialvalue="student", parent=self.root)
        email = tksd.askstring("Add User", "Email:", parent=self.root)
        pwd = tksd.askstring("Add User", "Password:", parent=self.root)
        if name and role and email and pwd:
            role = role.lower()
            self.main_app.users[username] = {"full_name": name, "role": role, "email": email}
            self.main_app.passwords[username] = self.main_app.hash_password(pwd)
            if role == "student":
                self.main_app.grades[username] = {"Math": 0, "Physics": 0, "Chemistry": 0, "Biology": 0, "English": 0}
                self.main_app.eca[username] = []
                self.main_app.attendance[username] = []
            self.main_app.save_data()
            tkmb.showinfo("Success", f"User {username} added!")
            self.show_manage_users()

    def delete_user(self, username):
        if tkmb.askyesno("Confirm", f"Delete user {username}?"):
            del self.main_app.users[username]
            self.main_app.passwords.pop(username, None)
            self.main_app.grades.pop(username, None)
            self.main_app.eca.pop(username, None)
            self.main_app.attendance.pop(username, None)
            self.main_app.save_data()
            self.show_manage_users()

    # Admin can view grades 
    def show_manage_grades(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="All Students Grades", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        for student in [u for u in self.main_app.users if self.main_app.users[u]["role"] == "student"]:
            ctk.CTkLabel(self.main_frame, text=f"{student} - {self.main_app.users[student]['full_name']}", 
                         font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10, anchor="w", padx=50)
            grades = self.main_app.grades.get(student, {})
            for sub, mark in grades.items():
                ctk.CTkLabel(self.main_frame, text=f"   {sub}: {mark}/100").pack(anchor="w", padx=100)


    def show_manage_eca(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Manage ECA", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        for student in [u for u in self.main_app.users if self.main_app.users[u]["role"] == "student"]:
            ctk.CTkButton(self.main_frame, text=f"Add ECA for {student}",
                          command=lambda s=student: self.add_eca(s)).pack(pady=8)

    def add_eca(self, student):
        activity = tksd.askstring("Add ECA", "Activity:", parent=self.root)
        desc = tksd.askstring("Add ECA", "Description:", parent=self.root)
        date = tksd.askstring("Add ECA", "Date (yyyy-mm-dd):", parent=self.root)
        if activity and desc and date:
            if student not in self.main_app.eca:
                self.main_app.eca[student] = []
            self.main_app.eca[student].append({"activity": activity, "description": desc, "date": date})
            self.main_app.save_data()
            tkmb.showinfo("Success", "ECA added!")

if __name__ == "__main__":
    print(" Starting EduManage")
    print("pip install customtkinter matplotlib pandas reportlab")
    app = EduManageApp()
    app.root.mainloop()