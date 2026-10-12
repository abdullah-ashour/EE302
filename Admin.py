import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QRadioButton, QTabWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

DB_PATH = r"C:\Users\abdul\Desktop\university\university.db"


# ===== Helper: Find Admin =====
def find_admin(admin_id=None, email=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if admin_id:
        cur.execute("SELECT id, name, password, email FROM Admins WHERE id=?", (admin_id,))
    else:
        cur.execute("SELECT id, name, password, email FROM Admins WHERE email=?", (email,))
    row = cur.fetchone()
    conn.close()
    return row


# ===== Admin Page =====
class AdminPage(QWidget):
    def __init__(self, admin_name, admin_id, session_id, login_window):
        super().__init__()
        self.admin_name = admin_name
        self.admin_id = admin_id
        self.session_id = session_id
        self.login_window = login_window
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Admin Page")
        self.resize(900, 600)
        self.setFont(QFont("Times New Roman", 13))

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # Header
        header = QLabel(f"Welcome Admin: {self.admin_name}")
        header.setFont(QFont("Times New Roman", 20, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(QWidget(), "Course Manager")
        self.tabs.addTab(QWidget(), "Student Manager")
        self.tabs.addTab(QWidget(), "Doctor Manager")
        self.tabs.addTab(QWidget(), "Program Manager")
        self.tabs.addTab(QWidget(), "Registration")
        self.tabs.addTab(QWidget(), "Reports")
        self.tabs.setFont(QFont("Times New Roman", 12))

        # Logout Button
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
        self.setWindowTitle("Admin Login")
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
        admin_id = self.id_input.text().strip()
        email = self.email_input.text().strip()
        password = self.pass_input.text().strip()

        if use_id and not admin_id:
            return QMessageBox.warning(self, "Error", "Enter your ID.")
        if not use_id and not email:
            return QMessageBox.warning(self, "Error", "Enter your Email.")
        if not password:
            return QMessageBox.warning(self, "Error", "Enter your Password.")

        uid = int(admin_id) if use_id and admin_id.isdigit() else None
        admin = find_admin(uid, email)
        if not admin:
            return QMessageBox.warning(self, "Error", "Admin not found.")

        db_id, name, db_pass, db_email = admin
        if password != str(db_pass):
            return QMessageBox.warning(self, "Error", "Incorrect password.")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO Sessions (user_id, role, login_time) VALUES (?, ?, ?)",
                    (db_id, "Admin", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        session_id = cur.lastrowid
        conn.commit()
        conn.close()

        self.hide()
        self.page = AdminPage(name, db_id, session_id, self)
        self.page.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())
