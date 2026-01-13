import sys
from PyQt6.QtWidgets import QApplication
from login import LoginDialog
from main_window import MainWindow
from database_setup import create_database

def main():
    # Create database if not exists
    create_database()

    app = QApplication(sys.argv)

    # Show login dialog
    login = LoginDialog()
    if login.exec() == LoginDialog.DialogCode.Accepted:
        # Show main window
        window = MainWindow(login.user_id, login.user_role)
        window.show()
        return app.exec()
    else:
        return 0

if __name__ == '__main__':
    sys.exit(main())