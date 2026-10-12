import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QRadioButton, QTabWidget,
    QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

DB_PATH = r"C:\Users\abdul\Desktop\university\university.db"


# ===== Helper: Find Student =====
def find_student(student_id=None, email=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if student_id:
        cur.execute("SELECT id, name, password, email FROM Students WHERE id=?", (student_id,))
    else:
        cur.execute("SELECT id, name, password, email FROM Students WHERE email=?", (email,))
    row = cur.fetchone()
    conn.close()
    return row


# ===== Student Page =====
class StudentPage(QWidget):
    def __init__(self, student_name, student_id, session_id, login_window):
        super().__init__()
        self.student_name = student_name
        self.student_id = student_id
        self.session_id = session_id
        self.login_window = login_window
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Student Page")
        self.resize(900, 600)
        self.setFont(QFont("Times New Roman", 13))

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # Header # NEW
        header = QLabel(f"Welcome Eng: {self.student_name}")
        header.setFont(QFont("Times New Roman", 20, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)

        # Tabs # NEW
        self.tabs = QTabWidget()
        self.tabs.addTab(QWidget(), "Profile")
        self.tabs.addTab(QWidget(), "Academic History")  # NEW
        self.tabs.addTab(QWidget(), "Course Registration")
        self.tabs.addTab(QWidget(), "Academic Schedule")
        self.tabs.addTab(QWidget(), "Waitlist System")
        self.tabs.addTab(QWidget(), "Program Plan")
        self.tabs.setFont(QFont("Times New Roman", 12))

        # Setup Academic History Tab # NEW
        self.setup_academic_history_tab()

        # Logout Button # NEW
        logout_btn = QPushButton("Logout")
        logout_btn.setFont(QFont("Times New Roman", 12))
        logout_btn.setFixedWidth(120)
        logout_btn.setStyleSheet("background-color: black; color: white; border-radius: 8px; padding: 5px;")
        logout_btn.clicked.connect(self.logout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(logout_btn)
        btn_layout.addStretch()

        layout.addWidget(header)
        layout.addWidget(self.tabs)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    # ===== Academic History Tab =====
    def setup_academic_history_tab(self):
        tab = self.tabs.widget(1)  # Academic History tab index 1 # NEW
        layout = QVBoxLayout()

        self.acad_table = QTableWidget()  # NEW
        self.acad_table.setColumnCount(7)  # NEW
        self.acad_table.setHorizontalHeaderLabels([  # NEW
            "Course Name", "Course Code", "Credit Hours", "Grade", "Level", "Year", "Semester",
        ])
        self.acad_table.horizontalHeader().setStretchLastSection(True)  # NEW
        self.acad_table.setEditTriggers(QTableWidget.NoEditTriggers)  # NEW
        self.acad_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)  # Center text horizontally # NEW
        self.acad_table.horizontalHeader().setSectionResizeMode(  # Auto-resize columns # NEW
            0, self.acad_table.horizontalHeader().ResizeToContents
        )
        self.acad_table.horizontalHeader().setSectionResizeMode(
            1, self.acad_table.horizontalHeader().ResizeToContents
        )
        self.acad_table.horizontalHeader().setSectionResizeMode(
            2, self.acad_table.horizontalHeader().ResizeToContents
        )
        self.acad_table.horizontalHeader().setSectionResizeMode(
            3, self.acad_table.horizontalHeader().ResizeToContents
        )
        self.acad_table.horizontalHeader().setSectionResizeMode(
            4, self.acad_table.horizontalHeader().ResizeToContents
        )
        self.acad_table.horizontalHeader().setSectionResizeMode(
            5, self.acad_table.horizontalHeader().ResizeToContents
        )
        self.acad_table.horizontalHeader().setSectionResizeMode(
            6, self.acad_table.horizontalHeader().ResizeToContents
        )

        layout.addWidget(self.acad_table)
        tab.setLayout(layout)

        self.load_academic_history()  # NEW

    def load_academic_history(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            # Get finished_courses from Students table # NEW
            cur.execute("SELECT finished_courses FROM Students WHERE id=?", (self.student_id,))
            row = cur.fetchone()
            if not row or not row[0]:
                self.acad_table.setRowCount(0)
                conn.close()
                return

            finished_courses = row[0].split(',')  # Courses separated by commas # NEW
            finished_courses = [c.strip() for c in finished_courses if c.strip()]

            self.acad_table.setRowCount(len(finished_courses))

            for idx, code in enumerate(finished_courses):
                # Fetch course data from Courses, Grades, ProgramPlans tables # NEW
                cur.execute("""
                    SELECT 
                        C.name,       -- course_name
                        C.code,       -- course_code
                        C.credits,    -- credit_hours
                        G.letter_grade, -- grade
                        P.level,      -- level
                        G.year_taken, -- year
                        G.semester_taken -- semester
                    FROM Courses C
                    JOIN Grades G ON C.code = G.course_code
                    LEFT JOIN ProgramPlans P ON C.code = P.course_code
                    WHERE G.student_id = ? AND G.course_code = ?
                """, (self.student_id, code))
            
                course_data = cur.fetchone()
                if course_data:
                    for col, value in enumerate(course_data):
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignCenter)  # Center text in cells # NEW
                        self.acad_table.setItem(idx, col, item)
                else:
                    # If no data found, fill first column with course code only # NEW
                    item = QTableWidgetItem(code)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.acad_table.setItem(idx, 0, item)
                    for col in range(1, 7):
                        empty_item = QTableWidgetItem("")
                        empty_item.setTextAlignment(Qt.AlignCenter)
                        self.acad_table.setItem(idx, col, empty_item)

            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Error loading academic history: {e}")

    # ===== Logout =====
    def logout(self):
        reply = QMessageBox.question(
            self, "Logout", "Are you sure you want to log out?", QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.record_logout_time()
            QMessageBox.information(self, "Logout", "You have been logged out successfully.")
            self.close()
            self.login_window.show()

    def record_logout_time(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("UPDATE Sessions SET logout_time = ? WHERE id = ?", (logout_time, self.session_id))
            conn.commit()
            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Error updating logout time: {e}")


# ===== Login Window =====
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Login")
        self.setGeometry(600, 300, 400, 350)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Course Registration System")
        title.setFont(QFont("Times New Roman", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Radio buttons
        radio_layout = QHBoxLayout()
        self.use_id = QRadioButton("Use ID")
        self.use_email = QRadioButton("Use Email")
        self.use_id.setChecked(True)
        self.use_id.toggled.connect(self.toggle_input)
        radio_layout.addWidget(self.use_id)
        radio_layout.addWidget(self.use_email)
        layout.addLayout(radio_layout)

        # Inputs
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter your ID")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your Email")
        self.email_input.setDisabled(True)
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)

        # Login button
        login_btn = QPushButton("Login")
        login_btn.setFont(QFont("Times New Roman", 12))
        login_btn.setStyleSheet("padding: 5px; border-radius:5px;")
        login_btn.clicked.connect(self.login)

        layout.addWidget(self.id_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.pass_input)
        layout.addWidget(login_btn)
        self.setLayout(layout)

    def toggle_input(self):
        if self.use_id.isChecked():
            self.id_input.setEnabled(True)
            self.email_input.setDisabled(True)
            self.email_input.clear()
        else:
            self.email_input.setEnabled(True)
            self.id_input.setDisabled(True)
            self.id_input.clear()

    def login(self):
        use_id = self.use_id.isChecked()
        student_id = self.id_input.text().strip()
        email = self.email_input.text().strip()
        password = self.pass_input.text().strip()

        if use_id and not student_id:
            return QMessageBox.warning(self, "Error", "Enter your ID.")
        if not use_id and not email:
            return QMessageBox.warning(self, "Error", "Enter your Email.")
        if not password:
            return QMessageBox.warning(self, "Error", "Enter your Password.")

        uid = int(student_id) if use_id and student_id.isdigit() else None
        student = find_student(uid, email)
        if not student:
            return QMessageBox.warning(self, "Error", "Student not found.")

        db_id, name, db_pass, db_email = student
        if password != str(db_pass):
            return QMessageBox.warning(self, "Error", "Incorrect password.")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO Sessions (user_id, role, login_time) VALUES (?, ?, ?)",
                    (db_id, "Student", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        session_id = cur.lastrowid
        conn.commit()
        conn.close()

        self.hide()
        self.page = StudentPage(name, db_id, session_id, self)
        self.page.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())
