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
        print("🛠️ Creating demo accounts because no data found...")
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

        self.safe_save(self.users_file, self.users)
        self.safe_save(self.passwords_file, self.passwords)
        self.safe_save(self.grades_file, self.grades)
        self.safe_save(self.eca_file, self.eca)
        self.safe_save(self.attendance_file, self.attendance)

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
            elif self.current_role == "teacher":
                TeacherDashboard(self.root, self).show()
            else:
                StudentDashboard(self.root, self).show()
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

    # Admin Analytics with ECA Graph 
    def show_analytics(self):
        self.clear_main_frame()

        # Make main frame scrollable
        scroll_frame = ctk.CTkScrollableFrame(self.main_frame, corner_radius=0)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(scroll_frame, text="Performance Analytics", 
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        # Overall Grade Chart
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
            canvas = FigureCanvasTkAgg(fig, scroll_frame)
            canvas.get_tk_widget().pack(pady=20, fill="both", expand=True)
            canvas.draw()

        # ECA Graph
        ctk.CTkLabel(scroll_frame, text="ECA Points Overview", 
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(30,10))

        students = [u for u in self.main_app.users if self.main_app.users[u]["role"] == "student"]
        totals = [sum(e.get("points", 0) for e in self.main_app.eca.get(s, [])) for s in students]
        names = students

        fig2, ax2 = plt.subplots(figsize=(10, 5))
        ax2.bar(names, totals, color="#ffaa00")
        ax2.set_title("Total ECA Points per Student")
        ax2.set_ylabel("Points")
        canvas2 = FigureCanvasTkAgg(fig2, scroll_frame)
        canvas2.get_tk_widget().pack(pady=20, fill="both", expand=True)
        canvas2.draw()

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

    def export_pdf(self):
        if not PDF_AVAILABLE:
            tkmb.showerror("Error", "Install reportlab for PDF export")
            return
        try:
            path = f"EduManage_Teacher_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            c = canvas.Canvas(path, pagesize=letter)
            y = 750

            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, y, "=== EduManage Report (Teacher) ===")
            y -= 40

            c.setFont("Helvetica", 12)
            c.drawString(100, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            y -= 30

            # Teacher Info
            teacher_name = self.main_app.users[self.main_app.current_user]['full_name']
            c.drawString(100, y, f"Teacher: {teacher_name}")
            y -= 40

            # Student List with Full Names
            c.drawString(100, y, "STUDENTS IN CLASS:")
            y -= 25

            student_list = [u for u in self.main_app.users if self.main_app.users[u]["role"] == "student"]
            for username in student_list:
                full_name = self.main_app.users[username].get("full_name", username)
                c.drawString(120, y, f"• {full_name} ({username})")
                y -= 20
                if y < 100:   # New page if needed
                    c.showPage()
                    y = 750

            # Class Average Grades
            y -= 10
            c.drawString(100, y, "CLASS AVERAGE GRADES:")
            y -= 25
            subjects = ["Math", "Physics", "Chemistry", "Biology", "English"]
            for sub in subjects:
                total = sum(self.main_app.grades.get(s, {}).get(sub, 0) for s in self.main_app.grades)
                count = len(self.main_app.grades)
                avg = round(total / count, 1) if count > 0 else 0
                c.drawString(120, y, f"{sub}: {avg}/100")
                y -= 22

            # Individual Student Grades (with Names)
            y -= 15
            c.drawString(100, y, "INDIVIDUAL STUDENT GRADES:")
            y -= 30

            for username in student_list:
                full_name = self.main_app.users[username].get("full_name", username)
                grades = self.main_app.grades.get(username, {})
                
                c.drawString(120, y, f"{full_name} ({username}):")
                y -= 20
                
                if grades:
                    for sub in ["Math", "Physics", "Chemistry", "Biology", "English"]:
                        mark = grades.get(sub, 0)
                        c.drawString(140, y, f"   {sub}: {mark}/100")
                        y -= 18
                else:
                    c.drawString(140, y, "   No grades recorded")
                    y -= 18
                
                y -= 8  # Extra spacing between students
                if y < 100:
                    c.showPage()
                    y = 750

            c.save()
            tkmb.showinfo("Success", f"PDF saved successfully!\n{path}")
        except Exception as e:
            tkmb.showerror("Error", f"PDF export failed: {str(e)}")


#  TEACHER DASHBOARD 
class TeacherDashboard:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app
        self.main_frame = None
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.calendar_buttons = []

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
        ctk.CTkButton(sidebar, text="Subject Scores", command=self.show_subject_scores, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Attendance Calendar", command=self.show_attendance_calendar, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Assign Grades", command=self.assign_grades, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Manage ECA + Points", command=self.manage_eca, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="ECA Graph", command=self.show_eca_graph, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Attendance Stats (pandas)", command=self.show_attendance_stats, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Export to PDF", command=self.export_pdf, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="View Students", command=self.show_all_students, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Logout", command=self.main_app.logout, fg_color="red", height=40).pack(side="bottom", pady=30, padx=20, fill="x")

    def clear_main_frame(self):
        if self.main_frame:
            for widget in self.main_frame.winfo_children():
                widget.destroy()

    def show_dashboard(self):
        self.clear_main_frame()
        name = self.main_app.users[self.main_app.current_user]['full_name']
        ctk.CTkLabel(self.main_frame, text=f"Welcome, {name} (Teacher)", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=30)

    def show_subject_scores(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Subject Wise Average Scores", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        subjects = ["Math", "Physics", "Chemistry", "Biology", "English"]
        avgs = []
        for sub in subjects:
            total = sum(self.main_app.grades.get(s, {}).get(sub, 0) for s in self.main_app.grades)
            count = len(self.main_app.grades)
            avgs.append(round(total / count, 1) if count > 0 else 0)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(subjects, avgs, color="#00d4ff")
        ax.set_title("Average Scores by Subject")
        ax.set_ylim(0, 100)
        canvas = FigureCanvasTkAgg(fig, self.main_frame)
        canvas.get_tk_widget().pack(pady=20, fill="both", expand=True)
        canvas.draw()

    def show_all_students(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="All Students", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        for username, info in self.main_app.users.items():
            if info["role"] == "student":
                frame = ctk.CTkFrame(self.main_frame)
                frame.pack(pady=8, padx=80, fill="x")
                ctk.CTkLabel(frame, text=f"{username} — {info['full_name']}").pack(side="left", padx=20)

    def show_attendance_calendar(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text=f"Attendance Calendar - {calendar.month_name[self.current_month]} {self.current_year}",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)

        cal_frame = ctk.CTkFrame(self.main_frame)
        cal_frame.pack(pady=10)

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            ctk.CTkLabel(cal_frame, text=day, width=60).grid(row=0, column=i, padx=2, pady=2)

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        self.calendar_buttons = []
        row = 1
        for week in cal:
            for day in week:
                if day == 0:
                    ctk.CTkLabel(cal_frame, text="").grid(row=row, column=week.index(day), padx=2, pady=2)
                else:
                    btn = ctk.CTkButton(cal_frame, text=str(day), width=60, height=60,
                                        command=lambda d=day: self.mark_attendance_on_date(d))
                    btn.grid(row=row, column=week.index(day), padx=2, pady=2)
                    self.calendar_buttons.append(btn)
            row += 1

        ctk.CTkButton(self.main_frame, text="← Previous Month", command=self.prev_month).pack(side="left", padx=20, pady=10)
        ctk.CTkButton(self.main_frame, text="Next Month →", command=self.next_month).pack(side="right", padx=20, pady=10)

    def prev_month(self):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.show_attendance_calendar()

    def next_month(self):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.show_attendance_calendar()

    def mark_attendance_on_date(self, day):
        date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
        mark_win = ctk.CTkToplevel(self.root)
        mark_win.title(f"Mark Attendance - {date_str}")
        mark_win.geometry("600x500")

        ctk.CTkLabel(mark_win, text=f"Mark attendance for {date_str}", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        for student in [u for u in self.main_app.users if self.main_app.users[u]["role"] == "student"]:
            frame = ctk.CTkFrame(mark_win)
            frame.pack(pady=5, padx=20, fill="x")
            ctk.CTkLabel(frame, text=f"{student} - {self.main_app.users[student]['full_name']}").pack(side="left", padx=20)

            ctk.CTkButton(frame, text="Present", fg_color="green", width=100,
                          command=lambda s=student, d=date_str: self.save_attendance_date(s, d, "Present", mark_win)).pack(side="right", padx=5)
            ctk.CTkButton(frame, text="Absent", fg_color="red", width=100,
                          command=lambda s=student, d=date_str: self.save_attendance_date(s, d, "Absent", mark_win)).pack(side="right", padx=5)

    def save_attendance_date(self, student, date, status, window):
        if student not in self.main_app.attendance:
            self.main_app.attendance[student] = []
        self.main_app.attendance[student] = [a for a in self.main_app.attendance[student] if a["date"] != date]
        self.main_app.attendance[student].append({"date": date, "status": status})
        self.main_app.save_data()
        tkmb.showinfo("Success", f"{student} marked {status} on {date}")
        window.destroy()

    def manage_eca(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Manage ECA + Points for Students", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        for student in [u for u in self.main_app.users if self.main_app.users[u]["role"] == "student"]:
            frame = ctk.CTkFrame(self.main_frame)
            frame.pack(pady=12, padx=60, fill="x")
            ctk.CTkLabel(frame, text=f"{student} - {self.main_app.users[student]['full_name']}").pack(pady=5)
            ctk.CTkButton(frame, text="Add ECA Activity + Points",
                          command=lambda s=student: self.add_eca_with_points(s)).pack(pady=8)

    def add_eca_with_points(self, student):
        activity = tksd.askstring("ECA", "Activity Name:", parent=self.root)
        desc = tksd.askstring("ECA", "Description:", parent=self.root)
        points = tksd.askstring("ECA", "Points (0-20):", initialvalue="10", parent=self.root)
        date = tksd.askstring("ECA", "Date (yyyy-mm-dd):", parent=self.root)
        try:
            points = int(points)
        except:
            points = 0
        if activity and desc and date:
            if student not in self.main_app.eca:
                self.main_app.eca[student] = []
            self.main_app.eca[student].append({"activity": activity, "description": desc, "date": date, "points": points})
            self.main_app.save_data()
            tkmb.showinfo("Done", f"ECA with {points} points added for {student}!")

    def show_eca_graph(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="ECA Points Graph (All Students)", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        students = [u for u in self.main_app.users if self.main_app.users[u]["role"] == "student"]
        totals = [sum(e.get("points", 0) for e in self.main_app.eca.get(s, [])) for s in students]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(students, totals, color="#ffaa00")
        ax.set_title("Total ECA Points per Student")
        canvas = FigureCanvasTkAgg(fig, self.main_frame)
        canvas.get_tk_widget().pack(pady=20, fill="both", expand=True)
        canvas.draw()

    def show_attendance_stats(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Attendance Stats (Current Month) - Pandas + Matplotlib",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        students = [u for u in self.main_app.users if self.main_app.users[u]["role"] == "student"]
        data = []
        for s in students:
            records = self.main_app.attendance.get(s, [])
            this_month = [r for r in records if r["date"].startswith(f"{self.current_year}-{self.current_month:02d}")]
            total_days = len(this_month)
            present = sum(1 for r in this_month if r["status"] == "Present")
            perc = round((present / total_days * 100), 1) if total_days > 0 else 0
            data.append({"Student": s, "Total Days": total_days, "Present": present, "Attendance %": perc})

        if not data:
            ctk.CTkLabel(self.main_frame, text="No attendance data yet").pack()
            return

        df = pd.DataFrame(data)
        print("=== Pandas Attendance DF ===")
        print(df)

        fig, ax = plt.subplots(figsize=(10, len(students)*0.6 + 2))
        ax.axis('off')
        table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.8)
        ax.set_title("Monthly Attendance Summary")
        canvas = FigureCanvasTkAgg(fig, self.main_frame)
        canvas.get_tk_widget().pack(pady=20, fill="both", expand=True)
        canvas.draw()

    def assign_grades(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Assign / Update Grades", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        subjects = ["Math", "Physics", "Chemistry", "Biology", "English"]
        for student in [u for u in self.main_app.users if self.main_app.users[u]["role"] == "student"]:
            frame = ctk.CTkFrame(self.main_frame)
            frame.pack(pady=12, padx=60, fill="x")
            ctk.CTkLabel(frame, text=f"{student} — {self.main_app.users[student]['full_name']}", font=ctk.CTkFont(weight="bold")).pack(pady=5)
            entries = {}
            row = ctk.CTkFrame(frame)
            row.pack(fill="x", pady=5)
            for sub in subjects:
                ctk.CTkLabel(row, text=sub, width=90).pack(side="left", padx=8)
                entry = ctk.CTkEntry(row, width=70)
                entry.insert(0, str(self.main_app.grades.get(student, {}).get(sub, 0)))
                entry.pack(side="left", padx=5)
                entries[sub] = entry

            def save_grades(s=student, e=entries):
                for sub, ent in e.items():
                    try:
                        mark = int(ent.get())
                        self.main_app.grades[s][sub] = max(0, min(100, mark))
                    except ValueError:
                        pass
                self.main_app.save_data()
                tkmb.showinfo("Success", f"Grades saved for {s}")

            ctk.CTkButton(frame, text="Save Grades", command=save_grades).pack(pady=8)

    def export_pdf(self):
        if not PDF_AVAILABLE:
            tkmb.showerror("Error", "Install reportlab for PDF export")
            return
        try:
            path = f"EduManage_Teacher_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            c = canvas.Canvas(path, pagesize=letter)
            y = 750

            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, y, "=== EduManage Report (Teacher) ===")
            y -= 40

            c.setFont("Helvetica", 12)
            c.drawString(100, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            y -= 30

            # Teacher Info
            teacher_name = self.main_app.users[self.main_app.current_user]['full_name']
            c.drawString(100, y, f"Teacher: {teacher_name}")
            y -= 40

            # Student List with Full Names
            c.drawString(100, y, "STUDENTS IN CLASS:")
            y -= 25

            student_list = [u for u in self.main_app.users if self.main_app.users[u]["role"] == "student"]
            for username in student_list:
                full_name = self.main_app.users[username].get("full_name", username)
                c.drawString(120, y, f"• {full_name} ({username})")
                y -= 20
                if y < 100:   # New page if needed
                    c.showPage()
                    y = 750

            # Class Average Grades
            y -= 10
            c.drawString(100, y, "CLASS AVERAGE GRADES:")
            y -= 25
            subjects = ["Math", "Physics", "Chemistry", "Biology", "English"]
            for sub in subjects:
                total = sum(self.main_app.grades.get(s, {}).get(sub, 0) for s in self.main_app.grades)
                count = len(self.main_app.grades)
                avg = round(total / count, 1) if count > 0 else 0
                c.drawString(120, y, f"{sub}: {avg}/100")
                y -= 22

            # Individual Student Grades (with Names)
            y -= 15
            c.drawString(100, y, "INDIVIDUAL STUDENT GRADES:")
            y -= 30

            for username in student_list:
                full_name = self.main_app.users[username].get("full_name", username)
                grades = self.main_app.grades.get(username, {})
                
                c.drawString(120, y, f"{full_name} ({username}):")
                y -= 20
                
                if grades:
                    for sub in ["Math", "Physics", "Chemistry", "Biology", "English"]:
                        mark = grades.get(sub, 0)
                        c.drawString(140, y, f"   {sub}: {mark}/100")
                        y -= 18
                else:
                    c.drawString(140, y, "   No grades recorded")
                    y -= 18
                
                y -= 8  # Extra spacing between students
                if y < 100:
                    c.showPage()
                    y = 750

            c.save()
            tkmb.showinfo("Success", f"PDF saved successfully!\n{path}")
        except Exception as e:
            tkmb.showerror("Error", f"PDF export failed: {str(e)}")


#  STUDENT DASHBOARD 
class StudentDashboard:
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
        ctk.CTkButton(sidebar, text="Profile", command=self.show_profile, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="My Grades", command=self.show_my_grades, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="My ECA", command=self.show_my_eca, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="My Attendance", command=self.show_my_attendance, height=40).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Logout", command=self.main_app.logout, fg_color="red", height=40).pack(side="bottom", pady=30, padx=20, fill="x")

    def clear_main_frame(self):
        if self.main_frame:
            for widget in self.main_frame.winfo_children():
                widget.destroy()

    def show_dashboard(self):
        self.clear_main_frame()
        user = self.main_app.users[self.main_app.current_user]
        ctk.CTkLabel(self.main_frame, text=f"Welcome back, {user['full_name']}!", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=30)
        grades = self.main_app.grades.get(self.main_app.current_user, {})
        if grades:
            fig, ax = plt.subplots(figsize=(8, 4))
            subjects = list(grades.keys())
            marks = list(grades.values())
            ax.bar(subjects, marks, color="#00d4ff")
            ax.set_title("Your Academic Performance")
            ax.set_ylim(0, 100)
            canvas = FigureCanvasTkAgg(fig, self.main_frame)
            canvas.get_tk_widget().pack(pady=20, padx=40, fill="both", expand=True)
            canvas.draw()

    def show_profile(self):
        self.clear_main_frame()
        current_username = self.main_app.current_user
        user = self.main_app.users[current_username]
        ctk.CTkLabel(self.main_frame, text="Account Settings", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(pady=20, padx=100, fill="x")
        ctk.CTkLabel(frame, text="Full Name").pack(pady=(10,2), anchor="w")
        name_entry = ctk.CTkEntry(frame, width=350)
        name_entry.insert(0, user.get("full_name", ""))
        name_entry.pack(pady=5)
        ctk.CTkLabel(frame, text="Email").pack(pady=(10,2), anchor="w")
        email_entry = ctk.CTkEntry(frame, width=350)
        email_entry.insert(0, user.get("email", ""))
        email_entry.pack(pady=5)
        ctk.CTkLabel(frame, text="Current Password (required only if changing password)").pack(pady=(15,2), anchor="w")
        old_pass = ctk.CTkEntry(frame, show="*", width=350)
        old_pass.pack(pady=5)
        ctk.CTkLabel(frame, text="New Password (leave blank to keep current)").pack(pady=(10,2), anchor="w")
        new_pass = ctk.CTkEntry(frame, show="*", width=350)
        new_pass.pack(pady=5)

        def save_changes():
            new_name = name_entry.get().strip()
            new_email = email_entry.get().strip()
            old_password = old_pass.get().strip()
            new_password = new_pass.get().strip()
            if not new_name or not new_email:
                tkmb.showerror("Error", "Name and Email cannot be empty")
                return
            if new_password:
                if not old_password or self.main_app.hash_password(old_password) != self.main_app.passwords[current_username]:
                    tkmb.showerror("Error", "Current password is incorrect")
                    return
                if not self.main_app.is_strong_password(new_password):
                    tkmb.showerror("Error", "New password must be 8+ chars with uppercase, lowercase & number")
                    return
                self.main_app.passwords[current_username] = self.main_app.hash_password(new_password)
            self.main_app.users[current_username]["full_name"] = new_name
            self.main_app.users[current_username]["email"] = new_email
            self.main_app.save_data()
            tkmb.showinfo("Success", "Profile updated successfully!")
            self.show_dashboard()

        ctk.CTkButton(frame, text="Save Changes", command=save_changes).pack(pady=20)

    def show_my_grades(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="My Grades", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        grades = self.main_app.grades.get(self.main_app.current_user, {})
        for sub, mark in grades.items():
            frame = ctk.CTkFrame(self.main_frame)
            frame.pack(pady=8, padx=100, fill="x")
            ctk.CTkLabel(frame, text=sub, width=150).pack(side="left", padx=20)
            ctk.CTkLabel(frame, text=f"{mark}/100", font=ctk.CTkFont(size=18, weight="bold")).pack(side="right", padx=20)

    def show_my_eca(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="My Extracurricular Activities", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        acts = self.main_app.eca.get(self.main_app.current_user, [])
        if not acts:
            ctk.CTkLabel(self.main_frame, text="No ECA recorded yet").pack()
            return
        for act in acts:
            frame = ctk.CTkFrame(self.main_frame)
            frame.pack(pady=8, padx=80, fill="x")
            ctk.CTkLabel(frame, text=f"{act['activity']} - {act['description']}").pack()
            ctk.CTkLabel(frame, text=act['date'], text_color="gray").pack()

    def show_my_attendance(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="My Attendance", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        att = self.main_app.attendance.get(self.main_app.current_user, [])
        if not att:
            ctk.CTkLabel(self.main_frame, text="No attendance records").pack()
            return
        for record in att:
            color = "green" if record["status"] == "Present" else "red"
            ctk.CTkLabel(self.main_frame, text=f"{record['date']}: {record['status']}", text_color=color).pack(pady=5)


if __name__ == "__main__":
    print(" Starting EduManage")
    print("pip install customtkinter matplotlib pandas reportlab")
    app = EduManageApp()
    app.root.mainloop()