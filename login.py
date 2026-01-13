import sys
import sqlite3
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.user_id = None
        self.user_role = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("HRMS Login")
        self.setFixedSize(400, 250)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        # Title
        title = QLabel("HRMS - Human Resource Management System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        # Username
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # Password
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.authenticate)
        layout.addWidget(self.login_btn)

        # Default credentials info
        info = QLabel("Default Super Admin: superadmin / admin123")
        info.setStyleSheet("font-size: 10px; color: gray;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        self.setLayout(layout)

    def authenticate(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return

        # Connect to database
        db_path = Path("database/hrms.db")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.user_id = user[0]
            self.user_role = user[1]
            self.accept()  # Close dialog with success
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec() == QDialog.DialogCode.Accepted:
        print(f"Logged in as {login.user_role}")
    sys.exit(app.exec())