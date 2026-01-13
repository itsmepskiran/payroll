import sys
import sqlite3
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QComboBox, QMessageBox, QFileDialog, QDateEdit,
    QTextEdit, QProgressBar, QSplitter
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QAction
import pandas as pd
import os

class MainWindow(QMainWindow):
    def __init__(self, user_id, user_role):
        super().__init__()
        self.user_id = user_id
        self.user_role = user_role
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"HRMS - {self.user_role.title()}")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create tab widget
        self.tab_widget = QTabWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.tab_widget)

        # Add tabs based on role
        self.add_dashboard_tab()
        if self.user_role in ['super_admin', 'admin']:
            self.add_companies_tab()
            self.add_departments_tab()
            self.add_positions_tab()
            self.add_users_tab()
        self.add_employees_tab()
        self.add_attendance_tab()
        self.add_payroll_tab()
        self.add_reports_tab()
        self.add_documents_tab()

        # Menu bar
        self.create_menu_bar()

    def create_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')
        logout_action = QAction('Logout', self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def logout(self):
        self.close()
        # Re-run login
        from login import LoginDialog
        login = LoginDialog()
        if login.exec() == LoginDialog.Accepted:
            window = MainWindow(login.user_id, login.user_role)
            window.show()
        else:
            sys.exit()

    def add_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        welcome = QLabel(f"Welcome to HRMS Dashboard - {self.user_role.title()}")
        welcome.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(welcome)

        # Add some stats
        stats_layout = QHBoxLayout()
        self.employee_count = QLabel("Total Employees: 0")
        self.department_count = QLabel("Total Departments: 0")
        stats_layout.addWidget(self.employee_count)
        stats_layout.addWidget(self.department_count)
        layout.addLayout(stats_layout)

        self.tab_widget.addTab(tab, "Dashboard")
        self.update_dashboard_stats()

    def update_dashboard_stats(self):
        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM employees")
        emp_count = cursor.fetchone()[0]
        self.employee_count.setText(f"Total Employees: {emp_count}")

        cursor.execute("SELECT COUNT(*) FROM departments")
        dept_count = cursor.fetchone()[0]
        self.department_count.setText(f"Total Departments: {dept_count}")

        conn.close()

    def add_companies_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Form for adding companies
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Company ID:"))
        self.company_id_input = QLineEdit()
        form_layout.addWidget(self.company_id_input)

        form_layout.addWidget(QLabel("Name:"))
        self.company_name_input = QLineEdit()
        form_layout.addWidget(self.company_name_input)

        form_layout.addWidget(QLabel("Address:"))
        self.company_address_input = QLineEdit()
        form_layout.addWidget(self.company_address_input)

        add_btn = QPushButton("Add Company")
        add_btn.clicked.connect(self.add_company)
        form_layout.addWidget(add_btn)

        layout.addLayout(form_layout)

        # Table for companies
        self.companies_table = QTableWidget()
        self.companies_table.setColumnCount(4)
        self.companies_table.setHorizontalHeaderLabels(["ID", "Company ID", "Name", "Address"])
        layout.addWidget(self.companies_table)

        self.tab_widget.addTab(tab, "Companies")
        self.load_companies()

    def add_company(self):
        company_id = self.company_id_input.text().strip()
        name = self.company_name_input.text().strip()
        address = self.company_address_input.text().strip()

        if not company_id or not name:
            QMessageBox.warning(self, "Error", "Company ID and Name are required.")
            return

        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO companies (company_id, name, address, created_by) VALUES (?, ?, ?, ?)",
                         (company_id, name, address, self.user_id))
            conn.commit()
            QMessageBox.information(self, "Success", "Company added successfully.")
            self.load_companies()
            self.company_id_input.clear()
            self.company_name_input.clear()
            self.company_address_input.clear()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Company ID already exists.")
        conn.close()

    def load_companies(self):
        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, company_id, name, address FROM companies")
        companies = cursor.fetchall()
        conn.close()

        self.companies_table.setRowCount(len(companies))
        for row, company in enumerate(companies):
            for col, value in enumerate(company):
                self.companies_table.setItem(row, col, QTableWidgetItem(str(value)))

    def add_departments_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Form
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Department ID:"))
        self.dept_id_input = QLineEdit()
        form_layout.addWidget(self.dept_id_input)

        form_layout.addWidget(QLabel("Name:"))
        self.dept_name_input = QLineEdit()
        form_layout.addWidget(self.dept_name_input)

        form_layout.addWidget(QLabel("Company:"))
        self.dept_company_combo = QComboBox()
        self.load_companies_combo(self.dept_company_combo)
        form_layout.addWidget(self.dept_company_combo)

        refresh_btn = QPushButton("Refresh Companies")
        refresh_btn.clicked.connect(lambda: self.load_companies_combo(self.dept_company_combo))
        form_layout.addWidget(refresh_btn)

        add_btn = QPushButton("Add Department")
        add_btn.clicked.connect(self.add_department)
        form_layout.addWidget(add_btn)

        layout.addLayout(form_layout)

        # Table
        self.departments_table = QTableWidget()
        self.departments_table.setColumnCount(4)
        self.departments_table.setHorizontalHeaderLabels(["ID", "Dept ID", "Name", "Company"])
        layout.addWidget(self.departments_table)

        self.tab_widget.addTab(tab, "Departments")
        self.load_departments()

    def load_companies_combo(self, combo):
        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM companies")
        companies = cursor.fetchall()
        conn.close()
        combo.clear()
        for company in companies:
            combo.addItem(company[1], company[0])

    def add_department(self):
        dept_id = self.dept_id_input.text().strip()
        name = self.dept_name_input.text().strip()
        company_id = self.dept_company_combo.currentData()

        if not dept_id or not name:
            QMessageBox.warning(self, "Error", "Department ID and Name are required.")
            return

        if not company_id:
            QMessageBox.warning(self, "Error", "Please select a company.")
            return

        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO departments (department_id, name, company_id, created_by) VALUES (?, ?, ?, ?)",
                         (dept_id, name, company_id, self.user_id))
            conn.commit()
            QMessageBox.information(self, "Success", "Department added successfully.")
            self.load_departments()
            self.dept_id_input.clear()
            self.dept_name_input.clear()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Department ID already exists.")
        conn.close()

    def load_departments(self):
        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.id, d.department_id, d.name, c.name
            FROM departments d
            LEFT JOIN companies c ON d.company_id = c.id
        """)
        departments = cursor.fetchall()
        conn.close()

        self.departments_table.setRowCount(len(departments))
        for row, dept in enumerate(departments):
            for col, value in enumerate(dept):
                self.departments_table.setItem(row, col, QTableWidgetItem(str(value)))

    def add_positions_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Form
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Position ID:"))
        self.pos_id_input = QLineEdit()
        form_layout.addWidget(self.pos_id_input)

        form_layout.addWidget(QLabel("Title:"))
        self.pos_title_input = QLineEdit()
        form_layout.addWidget(self.pos_title_input)

        form_layout.addWidget(QLabel("Department:"))
        self.pos_dept_combo = QComboBox()
        self.load_departments_combo(self.pos_dept_combo)
        form_layout.addWidget(self.pos_dept_combo)

        add_btn = QPushButton("Add Position")
        add_btn.clicked.connect(self.add_position)
        form_layout.addWidget(add_btn)

        layout.addLayout(form_layout)

        # Table
        self.positions_table = QTableWidget()
        self.positions_table.setColumnCount(4)
        self.positions_table.setHorizontalHeaderLabels(["ID", "Pos ID", "Title", "Department"])
        layout.addWidget(self.positions_table)

        self.tab_widget.addTab(tab, "Positions")
        self.load_positions()

    def load_departments_combo(self, combo):
        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM departments")
        departments = cursor.fetchall()
        conn.close()
        combo.clear()
        for dept in departments:
            combo.addItem(dept[1], dept[0])

    def add_position(self):
        pos_id = self.pos_id_input.text().strip()
        title = self.pos_title_input.text().strip()
        dept_id = self.pos_dept_combo.currentData()

        if not pos_id or not title or not dept_id:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO positions (position_id, title, department_id, created_by) VALUES (?, ?, ?, ?)",
                         (pos_id, title, dept_id, self.user_id))
            conn.commit()
            QMessageBox.information(self, "Success", "Position added successfully.")
            self.load_positions()
            self.pos_id_input.clear()
            self.pos_title_input.clear()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Position ID already exists.")
        conn.close()

    def load_positions(self):
        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.position_id, p.title, d.name
            FROM positions p
            LEFT JOIN departments d ON p.department_id = d.id
        """)
        positions = cursor.fetchall()
        conn.close()

        self.positions_table.setRowCount(len(positions))
        for row, pos in enumerate(positions):
            for col, value in enumerate(pos):
                self.positions_table.setItem(row, col, QTableWidgetItem(str(value)))

    def add_users_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Form
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Username:"))
        self.user_username_input = QLineEdit()
        form_layout.addWidget(self.user_username_input)

        form_layout.addWidget(QLabel("Password:"))
        self.user_password_input = QLineEdit()
        self.user_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.user_password_input)

        form_layout.addWidget(QLabel("Role:"))
        self.user_role_combo = QComboBox()
        if self.user_role == 'super_admin':
            self.user_role_combo.addItems(['admin', 'user'])
        else:
            self.user_role_combo.addItem('user')
        form_layout.addWidget(self.user_role_combo)

        add_btn = QPushButton("Add User")
        add_btn.clicked.connect(self.add_user)
        form_layout.addWidget(add_btn)

        layout.addLayout(form_layout)

        # Table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(3)
        self.users_table.setHorizontalHeaderLabels(["ID", "Username", "Role"])
        layout.addWidget(self.users_table)

        self.tab_widget.addTab(tab, "Users")
        self.load_users()

    def add_user(self):
        username = self.user_username_input.text().strip()
        password = self.user_password_input.text().strip()
        role = self.user_role_combo.currentText()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password are required.")
            return

        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                         (username, password, role))
            conn.commit()
            QMessageBox.information(self, "Success", "User added successfully.")
            self.load_users()
            self.user_username_input.clear()
            self.user_password_input.clear()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Username already exists.")
        conn.close()

    def load_users(self):
        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users")
        users = cursor.fetchall()
        conn.close()

        self.users_table.setRowCount(len(users))
        for row, user in enumerate(users):
            for col, value in enumerate(user):
                self.users_table.setItem(row, col, QTableWidgetItem(str(value)))

    def add_employees_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Form
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("First Name:"))
        self.emp_fname_input = QLineEdit()
        form_layout.addWidget(self.emp_fname_input)

        form_layout.addWidget(QLabel("Last Name:"))
        self.emp_lname_input = QLineEdit()
        form_layout.addWidget(self.emp_lname_input)

        form_layout.addWidget(QLabel("Email:"))
        self.emp_email_input = QLineEdit()
        form_layout.addWidget(self.emp_email_input)

        form_layout.addWidget(QLabel("Position:"))
        self.emp_pos_combo = QComboBox()
        self.load_positions_combo(self.emp_pos_combo)
        form_layout.addWidget(self.emp_pos_combo)

        add_btn = QPushButton("Add Employee")
        add_btn.clicked.connect(self.add_employee)
        form_layout.addWidget(add_btn)

        layout.addLayout(form_layout)

        # Table
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(6)
        self.employees_table.setHorizontalHeaderLabels(["ID", "Emp ID", "Name", "Email", "Position", "Status"])
        layout.addWidget(self.employees_table)

        self.tab_widget.addTab(tab, "Employees")
        self.load_employees()

    def load_positions_combo(self, combo):
        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM positions")
        positions = cursor.fetchall()
        conn.close()
        combo.clear()
        for pos in positions:
            combo.addItem(pos[1], pos[0])

    def add_employee(self):
        fname = self.emp_fname_input.text().strip()
        lname = self.emp_lname_input.text().strip()
        email = self.emp_email_input.text().strip()
        pos_id = self.emp_pos_combo.currentData()

        if not fname or not lname or not email or not pos_id:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        # Auto-generate employee ID
        emp_id = self.generate_employee_id()

        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO employees (employee_id, first_name, last_name, email, position_id, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (emp_id, fname, lname, email, pos_id, self.user_id))
            conn.commit()
            QMessageBox.information(self, "Success", f"Employee added successfully. Employee ID: {emp_id}")
            self.load_employees()
            self.emp_fname_input.clear()
            self.emp_lname_input.clear()
            self.emp_email_input.clear()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Email already exists.")
        conn.close()

    def generate_employee_id(self):
        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees")
        count = cursor.fetchone()[0]
        conn.close()
        return f"EMP{str(count + 1).zfill(4)}"

    def load_employees(self):
        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id, e.employee_id, e.first_name || ' ' || e.last_name, e.email, p.title, e.status
            FROM employees e
            LEFT JOIN positions p ON e.position_id = p.id
        """)
        employees = cursor.fetchall()
        conn.close()

        self.employees_table.setRowCount(len(employees))
        for row, emp in enumerate(employees):
            for col, value in enumerate(emp):
                self.employees_table.setItem(row, col, QTableWidgetItem(str(value)))

    def add_attendance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Upload button
        upload_btn = QPushButton("Upload Attendance (Excel/CSV)")
        upload_btn.clicked.connect(self.upload_attendance)
        layout.addWidget(upload_btn)

        # Table
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(6)
        self.attendance_table.setHorizontalHeaderLabels(["ID", "Employee", "Date", "Check In", "Check Out", "Hours"])
        layout.addWidget(self.attendance_table)

        self.tab_widget.addTab(tab, "Attendance")
        self.load_attendance()

    def upload_attendance(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Attendance File", "", "Excel Files (*.xlsx);;CSV Files (*.csv)")
        if not file_path:
            return

        try:
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)

            # Assume columns: employee_id, date, check_in, check_out
            conn = sqlite3.connect("database/hrms.db")
            cursor = conn.cursor()

            for _, row in df.iterrows():
                emp_id = row['employee_id']
                date = row['date']
                check_in = row.get('check_in')
                check_out = row.get('check_out')

                # Get employee db id
                cursor.execute("SELECT id FROM employees WHERE employee_id = ?", (emp_id,))
                emp = cursor.fetchone()
                if emp:
                    cursor.execute("""
                        INSERT OR REPLACE INTO attendance (employee_id, date, check_in, check_out, uploaded_by)
                        VALUES (?, ?, ?, ?, ?)
                    """, (emp[0], date, check_in, check_out, self.user_id))

            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Attendance uploaded successfully.")
            self.load_attendance()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to upload attendance: {str(e)}")

    def load_attendance(self):
        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, e.employee_id, a.date, a.check_in, a.check_out, a.hours_worked
            FROM attendance a
            LEFT JOIN employees e ON a.employee_id = e.id
            ORDER BY a.date DESC
            LIMIT 100
        """)
        attendance = cursor.fetchall()
        conn.close()

        self.attendance_table.setRowCount(len(attendance))
        for row, att in enumerate(attendance):
            for col, value in enumerate(att):
                self.attendance_table.setItem(row, col, QTableWidgetItem(str(value)))

    def add_payroll_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Generate payroll button
        generate_btn = QPushButton("Generate Payroll")
        generate_btn.clicked.connect(self.generate_payroll)
        layout.addWidget(generate_btn)

        # Table
        self.payroll_table = QTableWidget()
        self.payroll_table.setColumnCount(8)
        self.payroll_table.setHorizontalHeaderLabels(["ID", "Employee", "Month", "Year", "Payable Days", "Gross", "Deductions", "Net"])
        layout.addWidget(self.payroll_table)

        self.tab_widget.addTab(tab, "Payroll")
        self.load_payroll()

    def generate_payroll(self):
        # Simple payroll generation for current month
        from datetime import datetime
        now = datetime.now()
        month = now.month
        year = now.year

        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()

        # Get all employees
        cursor.execute("SELECT id, employee_id, basic_salary, hra, conveyance, pf, esic FROM employees WHERE status = 'active'")
        employees = cursor.fetchall()

        for emp in employees:
            emp_id, emp_code, basic, hra, conv, pf, esic = emp

            # Calculate payable days (simplified - assume 30 days)
            payable_days = 30  # In real app, calculate from attendance

            gross = basic + (hra or 0) + (conv or 0)
            deductions = (pf or 0) + (esic or 0)
            net = gross - deductions

            cursor.execute("""
                INSERT INTO payroll (employee_id, month, year, payable_days, basic, hra, conveyance, gross, pf, esic, net_salary, generated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (emp_id, month, year, payable_days, basic, hra, conv, gross, pf, esic, net, self.user_id))

        conn.commit()
        conn.close()
        QMessageBox.information(self, "Success", "Payroll generated successfully.")
        self.load_payroll()

    def load_payroll(self):
        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, e.employee_id, p.month, p.year, p.payable_days, p.gross, p.pf + p.esic, p.net_salary
            FROM payroll p
            LEFT JOIN employees e ON p.employee_id = e.id
            ORDER BY p.year DESC, p.month DESC
            LIMIT 100
        """)
        payroll = cursor.fetchall()
        conn.close()

        self.payroll_table.setRowCount(len(payroll))
        for row, pay in enumerate(payroll):
            for col, value in enumerate(pay):
                self.payroll_table.setItem(row, col, QTableWidgetItem(str(value)))

    def add_reports_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Export buttons
        export_attendance_btn = QPushButton("Export Attendance Report")
        export_attendance_btn.clicked.connect(self.export_attendance)
        layout.addWidget(export_attendance_btn)

        export_payroll_btn = QPushButton("Export Payroll Report")
        export_payroll_btn.clicked.connect(self.export_payroll)
        layout.addWidget(export_payroll_btn)

        self.tab_widget.addTab(tab, "Reports")

    def export_attendance(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Attendance Report", "", "Excel Files (*.xlsx);;CSV Files (*.csv)")
        if not file_path:
            return

        conn = sqlite3.connect("database/hrms.db")
        df = pd.read_sql_query("""
            SELECT e.employee_id, e.first_name, e.last_name, a.date, a.check_in, a.check_out, a.hours_worked, a.status
            FROM attendance a
            LEFT JOIN employees e ON a.employee_id = e.id
        """, conn)
        conn.close()

        if file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        else:
            df.to_csv(file_path, index=False)

        QMessageBox.information(self, "Success", "Attendance report exported successfully.")

    def export_payroll(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Payroll Report", "", "Excel Files (*.xlsx);;CSV Files (*.csv)")
        if not file_path:
            return

        conn = sqlite3.connect("database/hrms.db")
        df = pd.read_sql_query("""
            SELECT e.employee_id, e.first_name, e.last_name, p.month, p.year, p.payable_days,
                   p.basic, p.hra, p.conveyance, p.gross, p.pf, p.esic, p.net_salary
            FROM payroll p
            LEFT JOIN employees e ON p.employee_id = e.id
        """, conn)
        conn.close()

        if file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        else:
            df.to_csv(file_path, index=False)

        QMessageBox.information(self, "Success", "Payroll report exported successfully.")

    def add_documents_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Upload document
        upload_doc_btn = QPushButton("Upload Document")
        upload_doc_btn.clicked.connect(self.upload_document)
        layout.addWidget(upload_doc_btn)

        # Table
        self.documents_table = QTableWidget()
        self.documents_table.setColumnCount(4)
        self.documents_table.setHorizontalHeaderLabels(["ID", "Employee", "Type", "File"])
        layout.addWidget(self.documents_table)

        self.tab_widget.addTab(tab, "Documents")
        self.load_documents()

    def upload_document(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Document", "", "All Files (*)")
        if not file_path:
            return

        # Select employee
        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, employee_id, first_name, last_name FROM employees")
        employees = cursor.fetchall()
        conn.close()

        if not employees:
            QMessageBox.warning(self, "Error", "No employees found.")
            return

        # Simple employee selection (in real app, use combo box)
        emp_id = employees[0][0]  # For now, use first employee
        doc_type = "General"  # For now

        # Copy file to documents folder
        docs_dir = Path("documents")
        docs_dir.mkdir(exist_ok=True)
        file_name = Path(file_path).name
        dest_path = docs_dir / file_name
        import shutil
        shutil.copy(file_path, dest_path)

        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO documents (employee_id, document_type, file_path, uploaded_by) VALUES (?, ?, ?, ?)",
                     (emp_id, doc_type, str(dest_path), self.user_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Document uploaded successfully.")
        self.load_documents()

    def load_documents(self):
        conn = sqlite3.connect("database/hrms.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.id, e.employee_id, d.document_type, d.file_path
            FROM documents d
            LEFT JOIN employees e ON d.employee_id = e.id
        """)
        documents = cursor.fetchall()
        conn.close()

        self.documents_table.setRowCount(len(documents))
        for row, doc in enumerate(documents):
            for col, value in enumerate(doc):
                self.documents_table.setItem(row, col, QTableWidgetItem(str(value)))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(1, 'super_admin')
    window.show()
    sys.exit(app.exec())