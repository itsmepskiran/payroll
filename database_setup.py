import os
import sqlite3
from pathlib import Path

def create_database():
    # Ensure database directory exists
    db_dir = Path("database")
    db_dir.mkdir(exist_ok=True)

    # Database file path
    db_path = db_dir / "hrms.db"

    # Connect to SQLite database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create users table (for login)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('super_admin', 'admin', 'user')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create companies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            address TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')

    # Create departments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            company_id INTEGER,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')

    # Create positions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            position_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            department_id INTEGER,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')

    # Create employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            address TEXT,
            date_of_birth DATE,
            date_of_joining DATE,
            position_id INTEGER,
            basic_salary REAL,
            hra REAL,
            conveyance REAL,
            pf REAL,
            esic REAL,
            status TEXT DEFAULT 'active',
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (position_id) REFERENCES positions(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')

    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            date DATE NOT NULL,
            check_in TIME,
            check_out TIME,
            hours_worked REAL,
            status TEXT DEFAULT 'present',
            uploaded_by INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (uploaded_by) REFERENCES users(id)
        )
    ''')

    # Create payroll table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            month INTEGER,
            year INTEGER,
            payable_days REAL,
            basic REAL,
            hra REAL,
            conveyance REAL,
            gross REAL,
            pf REAL,
            esic REAL,
            net_salary REAL,
            generated_by INTEGER,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (generated_by) REFERENCES users(id)
        )
    ''')

    # Create documents table for employee documents
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            document_type TEXT,
            file_path TEXT,
            uploaded_by INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (uploaded_by) REFERENCES users(id)
        )
    ''')

    # Insert default super admin user
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)
    ''', ('superadmin', 'admin123', 'super_admin'))

    # Commit changes
    conn.commit()
    conn.close()

    print("Database initialized successfully!")

if __name__ == '__main__':
    create_database()