# 🎓 EduManage - Student Profile Management System

A modern **Student Profile Management System** built using Python with a GUI powered by `customtkinter`.  
EduManage demonstrates practical **Object-Oriented Programming (OOP)**, data persistence, analytics, and visualization in a single integrated desktop application.

---

## 🚀 Features

### 🔐 Authentication System
- Secure login system with role-based access:
  - Admin
  - Teacher
  - Student
- Password hashing using `hashlib`
- Password strength validation

---

### 👨‍🏫 Admin Panel
- Manage users (Add/Delete students, teachers, admins)
- View all student grades
- Manage extracurricular activities (ECA)
- System-wide analytics dashboard
- Export full reports to PDF

---

### 👩‍🏫 Teacher Panel
- Assign and update student grades
- Mark and manage attendance (calendar-based UI)
- Add ECA activities with points
- View subject-wise performance statistics
- Attendance analytics using Pandas
- Export class reports as PDF
- Student overview dashboard

---

### 👨‍🎓 Student Panel
- View personal dashboard with performance graph
- Update profile information (secure password change)
- View grades per subject
- View attendance history
- View extracurricular activities

---

### 📊 Data Visualization
- Matplotlib-based bar charts:
  - Subject performance averages
  - Student grade distribution
  - ECA point comparison
- Embedded charts inside GUI

---

### 📅 Attendance System
- Interactive calendar-based attendance marking
- Daily present/absent tracking
- Monthly attendance analytics

---

### 📁 Data Storage
- JSON-based local file storage:
  - Users
  - Passwords (hashed)
  - Grades
  - Attendance
  - ECA records

---

### 📄 PDF Export
- Generates professional PDF reports using `reportlab`
- Includes:
  - Student list
  - Grades summary
  - Attendance summary
  - ECA details

---

## 🛠️ Tech Stack

- **Python 3.14.4**
- `customtkinter` – Modern GUI
- `matplotlib` – Data visualization
- `pandas` – Data analysis
- `reportlab` – PDF generation
- `json` – Data storage
- `hashlib` – Password security

---

## 📦 Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/edumanage.git
cd edumanage
python3 -m venv venv # For Mac/Linux/Unix
source venv/bin/activate # For Mac/Linux/Unix
python -m venv venv  # For Windows
venv\scripts\activate.ps1 # For Windows
pip install -r requirements.txt
python3 main.py # For Mac/Linux/Unix
python main.py # For windows
```
---
## 🔑 Default Demo Accounts

| Role    | Username | Password   |
| ------- | -------- | ---------- |
| Admin   | admin    | admin123   |
| Teacher | teacher1 | teacher123 |
| Student | student1 | student123 |

---
## 📁 Project Structure
```bash
student_management_system/
│
├── .gitignore            # ignores venv from being upload to github  
├── data/                 # .txt storage files 
├── main.py               # Main application
├── README.md             # Project documentation
```
---
## ⚠️ Note
This project is designed for educational purposes and demonstrates basic Python desktop application development.
---

# 🧠 Authors
Surya Pratap Gautam, Prashanna Rijal, Pranshu Bhatta

Built with effort and caffeine ☕. <br>
For academic learning and portfolio showcase.
