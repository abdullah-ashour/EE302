import sys
import sqlite3
import smtplib
import random
from datetime import datetime
from email.mime.text import MIMEText
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

DB_PATH = r"C:\Users\apody\Desktop\university\university.db"

# ========== البحث عن المستخدم ==========
def find_user(user_id=None, email=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for role, table in [("Student", "Students"), ("Doctor", "Doctors"), ("Admin", "Admins")]:
        if user_id:
            cur.execute(f"SELECT id, name, password FROM {table} WHERE id = ?", (user_id,))
        else:
            cur.execute(f"SELECT id, name, password FROM {table} WHERE email = ?", (email,))
        row = cur.fetchone()
        if row:
            conn.close()
            return role, table, row
    conn.close()
    return None, None, None


# ========== إرسال البريد ==========
def send_email(recipient_email, code):
    sender = 'your_email@gmail.com'
    sender_password = "your_app_password"
    subject = "Password Reset Code"
    message = f"Your verification code is: {code}"

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, sender_password)
            server.sendmail(sender, recipient_email, msg.as_string())
        return True
    except Exception as e:
        print("❌ Email error:", e)
        return False


# ========== نافذة تسجيل الدخول ==========
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(600, 300, 350, 250)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Course Registration System")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID (or leave blank to use Email)")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email (or leave blank to use ID)")

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)

        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.clicked.connect(self.forgot_password)

        layout.addWidget(self.id_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.pass_input)
        layout.addWidget(login_btn)
        layout.addWidget(forgot_btn)

        self.setLayout(layout)

    def login(self):
        id_text = self.id_input.text().strip()
        email = self.email_input.text().strip()
        password = self.pass_input.text().strip()

        if not id_text and not email:
            QMessageBox.warning(self, "Error", "Please enter ID or Email")
            return
        if not password:
            QMessageBox.warning(self, "Error", "Please enter your password")
            return

        user_id = None
        if id_text:
            try:
                user_id = int(id_text)
            except ValueError:
                QMessageBox.warning(self, "Error", "ID must be a number")
                return

        role, table, user = find_user(user_id, email)
        if not user:
            QMessageBox.warning(self, "Error", "User not found")
            return

        user_id, name, stored_pw = user
        if password == str(stored_pw):
            # ✅ تسجيل الدخول في Sessions مع role
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                "INSERT INTO Sessions (user_id, role, login_time) VALUES (?, ?, ?)",
                (user_id, role, login_time),
            )
            session_id = cur.lastrowid
            conn.commit()
            conn.close()

            # فتح صفحة Dashboard
            self.hide()
            self.dashboard = DashboardWindow(user_id, name, role, session_id, self)
            self.dashboard.show()
        else:
            QMessageBox.warning(self, "Error", "Incorrect password")

    def forgot_password(self):
        id_text = self.id_input.text().strip()
        email = self.email_input.text().strip()

        if not id_text and not email:
            QMessageBox.warning(self, "Error", "Please enter your ID or Email")
            return

        user_id = int(id_text) if id_text else None
        role, table, user = find_user(user_id, email)
        if not user:
            QMessageBox.warning(self, "Error", "User not found")
            return

        new_code = str(random.randint(100000, 999999))

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(f"UPDATE {table} SET password = ? WHERE id = ?", (new_code, user[0]))
        conn.commit()
        conn.close()

        sent = send_email(email, new_code)
        if sent:
            QMessageBox.information(self, "Success", f"A reset code has been sent to {email}")
        else:
            QMessageBox.warning(self, "Error", "Failed to send email.")


# ========== نافذة Dashboard ==========
class DashboardWindow(QWidget):
    def __init__(self, user_id, name, role, session_id, login_window):
        super().__init__()
        self.user_id = user_id
        self.session_id = session_id
        self.login_window = login_window

        self.setWindowTitle("Dashboard")
        self.setGeometry(600, 300, 300, 200)

        layout = QVBoxLayout()

        welcome = QLabel(f"Welcome {name}\nRole: {role}")
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setFont(QFont("Arial", 12, QFont.Bold))

        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)

        layout.addWidget(welcome)
        layout.addWidget(logout_btn)
        self.setLayout(layout)

    def logout(self):
        logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE Sessions SET logout_time = ? WHERE id = ?", (logout_time, self.session_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Logout", "You have been logged out successfully.")
        self.close()
        self.login_window.show()


# ========== تشغيل التطبيق ==========
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())
