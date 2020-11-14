import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5 import uic
import sqlite3
from PyQt5.QtCore import Qt
from PIL import Image
import os


# import classes from my files
from files import analysis_tables
from files import charts
from files import constants
from files import first_window
from files import second_window
from files import third_window
from files import errors


MyTable, CurrencyTable = analysis_tables.MyTable, analysis_tables.CurrencyTable
MyChart = charts.MyChart
Error = errors.Error

DATABASE = ''
MONTHS = constants.MONTHS
DATE = constants.DATE

# These variables were initialized to avoid deleting widgets after executing a function
main_widget = ''
error = ''
registration_widget = ''
settings = ''
edit_profil = ''
USER = []


# Main window
class MyWidget(QMainWindow):

    def __init__(self, user_name):
        super().__init__()
        # UI
        global DATABASE
        DATABASE = constants.get_date_base(user_name)
        self.user_name = user_name
        self.secondWidget = second_window.SecondWindow(self)
        self.thirdWidget = third_window.ThirdWidget(self)
        self.firstWidget = first_window.FirstWindow(self)

        self.list_of_widgets = [self.firstWidget, self.secondWidget, self.thirdWidget]

        self.setWindowTitle("ExpenseTracker")
        self.setWindowIcon(QIcon('sources/icons/menu/main.png'))
        self.setFixedSize(1010, 750)
        self.index = 0
        self.firstWidget.connectUI()
        self.settings.clicked.connect(self.start_settings)

    # Set window
    def change_window(self):
        if self.sender().objectName() == 'f_btn_1':
            self.index = 0
        elif self.sender().objectName() == 'f_btn_2':
            self.index = 1
        elif self.sender().objectName() == 'f_btn_3':
            self.index = 2
        self.list_of_widgets[self.index].connectUI()
        self.setWindowTitle("ExpenseTracker")
        self.setWindowIcon(QIcon('sources/icons/menu/main.png'))
        self.setFixedSize(1010, 750)
        self.settings.clicked.connect(self.start_settings)

    def start_settings(self):
        global settings
        settings = Settings()
        settings.show()


class EditProfil(QMainWindow):
    def __init__(self):
        super().__init__()
        # UI
        self.filename = ''
        self.ConnectUI()

        # Set window

    def ConnectUI(self):
        name_ui = 'ui_windows/create_account.ui'
        uic.loadUi(name_ui, self)
        self.setWindowTitle("ExpenseTracker")
        self.setWindowIcon(QIcon('sources/icons/menu/main.png'))
        self.setFixedSize(360, 360)
        global USER

        self.Username.setAlignment(Qt.AlignCenter)
        self.Password.setAlignment(Qt.AlignCenter)
        self.repeat_Password.setAlignment(Qt.AlignCenter)

        self.Username.setText(USER[0])
        self.Username.setEnabled(False)
        self.Password.setText(USER[1])
        self.repeat_Password.setText(USER[1])

        self.connect_buttons()

    def connect_buttons(self):
        self.create_account.clicked.connect(self.edit_profil)
        self.choose_img.clicked.connect(self.set_image)

    def edit_profil(self):
        username = self.Username.text()
        password = self.Password.text()
        repeat_password = self.repeat_Password.text()
        date = self.date_birth.text()
        img_file = self.filename
        try:
            con = sqlite3.connect('sources/profiles.db')
            cur = con.cursor()
            users_name = [elem for elem in cur.execute("""SELECT username from profiles""").fetchall()]
            assert len(username) > 0
            assert len(password) > 0
            assert password == repeat_password
            assert username not in users_name

            if img_file:
                im = Image.open(img_file)
                im2 = im.resize((90, 90))
                img_file = img_file.split('/')[-1]
                img_file = 'sources/' + username + '/DataBases/Profil/' + img_file
                im2.save(img_file)
            cur.execute("""UPDATE profiles 
                            SET password = ?
                            WHERE username = ? AND password = ?""",
                        (password, USER[0], USER[1]))
            cur.execute("""UPDATE profiles 
                            SET date = ?
                            WHERE username = ? AND password = ?""",
                        (date, USER[0], USER[1]))
            cur.execute("""UPDATE profiles 
                            SET img_directory = ?
                            WHERE username = ? AND password = ?""",
                        (img_file, USER[0], USER[1]))
            con.commit()
            con.close()
            self.close()

        except AssertionError:
            if not username or not password:
                error_show('Login or password fields were empty !')
            elif password != repeat_password:
                error_show('Passwords do not match !')
            else:
                error_show('This name is already interesting')

    def set_image(self):
        self.filename = QFileDialog.getOpenFileName(self, 'Выберите картинку', '', 'Картинки (*.jpg)')[0]


# Registration window
class RegistrationWidget(QMainWindow):

    def __init__(self):
        super().__init__()
        # UI
        self.filename = ''
        self.ConnectUI()

    # Set window
    def ConnectUI(self):
        name_ui = 'ui_windows/create_account.ui'
        uic.loadUi(name_ui, self)
        self.setWindowTitle("ExpenseTracker")
        self.setWindowIcon(QIcon('sources/icons/menu/main.png'))
        self.setFixedSize(360, 360)
        self.Username.setAlignment(Qt.AlignCenter)
        self.Password.setAlignment(Qt.AlignCenter)
        self.repeat_Password.setAlignment(Qt.AlignCenter)
        self.connect_buttons()

    def connect_buttons(self):
        self.create_account.clicked.connect(self.add_profil)
        self.choose_img.clicked.connect(self.set_image)

    # add new profil in database
    def add_profil(self):
        username = self.Username.text()
        password = self.Password.text()
        repeat_password = self.repeat_Password.text()
        date = self.date_birth.text()
        img_file = self.filename
        try:
            con = sqlite3.connect('sources/profiles.db')
            cur = con.cursor()
            users_name = [elem for elem in cur.execute("""SELECT username from profiles""").fetchall()]
            assert len(username) > 0
            assert len(password) > 0
            assert password == repeat_password
            assert username not in users_name

            self.create_directory(username)

            if img_file:
                im = Image.open(img_file)
                im2 = im.resize((90, 90))
                img_file = img_file.split('/')[-1]
                img_file = 'sources/' + username + '/DataBases/Profil/' + img_file
                im2.save(img_file)

            cur.execute("""INSERT INTO profiles(username, password, date, img_directory) 
                                        VALUES(?, ?, ?, ?)""",
                        (username, password, date, img_file))

            con.commit()
            con.close()
            self.close()

        except AssertionError:
            if not username or not password:
                error_show('Login or password fields were empty !')
            elif password != repeat_password:
                error_show('Passwords do not match !')
            else:
                error_show('This name is already interesting')

    # creating all files for user
    def create_directory(self, username):
        path = "sources/" + username
        os.mkdir(path)
        os.mkdir(path + '/images')
        path += '/DataBases'
        os.mkdir(path)
        os.mkdir(path + '/companies')
        os.mkdir(path + '/dbFiles')

        conn = sqlite3.connect(path + '/dbFiles/' + "cards.db")
        cursor = conn.cursor()

        cursor.execute("""CREATE TABLE card (
                            card_id   INT,
                            bank_name TEXT,
                            digits    INT,
                            money     INT);""")
        conn.commit()
        conn.close()

        directory = 'sources/' + username + '/DataBases/Tables/'
        directory_img = 'sources/' + username + '/images/'
        names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                 'November', 'December', 'currency', '2020']
        tables = ['months/january_costs.xlsx', 'months/february_costs.xlsx', 'months/march_costs.xlsx',
                  'months/april_costs.xlsx', 'months/may_costs.xlsx', 'months/june_costs.xlsx',
                  'months/july_costs.xlsx', 'months/august_costs.xlsx', 'months/september_costs.xlsx',
                  'months/october_costs.xlsx', 'months/november_costs.xlsx', 'months/december_costs.xlsx',
                  'sources/currency.xlsx', 'years/2020.xlsx']
        time = names.copy()
        time[-2] = 'exchange_rates_month'

        charts_types = ['hiss' for _ in range(12)] + ['chart', 'chart']

        conn = sqlite3.connect(path + '/dbFiles/' + "database.db")
        cursor = conn.cursor()

        cursor.execute("""CREATE TABLE companies (
                            id            INTEGER,
                            company_name  TEXT,
                            directory     TEXT,
                            directory_img TEXT,
                            type_chart    TEXT,
                            type_company  TEXT,
                            currency      TEXT);""")

        cursor.execute("""CREATE TABLE companies_types (
                            id           INTEGER,
                            type_company TEXT);""")

        cursor.execute("""CREATE TABLE database_table (
                            name          TEXT,
                            directory     TEXT,
                            time          TEXT,
                            directory_img TEXT,
                            type          TEXT);""")

        for i in range(14):
            cursor.execute("""INSERT INTO database_table(name, directory, time, directory_img, type) 
                                VALUES(?, ?, ?, ?, ?)""",
                           (names[i], directory + tables[i], time[i], directory_img, charts_types[i]))

        conn.commit()
        conn.close()

        conn = sqlite3.connect(path + '/dbFiles/' + "payments.db")
        cursor = conn.cursor()

        cursor.execute("""CREATE TABLE history (
                            id              INT,
                            type_of_payment INT,
                            date            DATE,
                            prise           REAL,
                            type            BOOLEAN,
                            card            TEXT);""")
        cursor.execute("""CREATE TABLE types_payments (
                            id        INT,
                            type_name TEXT);""")

        conn.commit()
        conn.close()

        os.mkdir(path + '/Profil')
        os.mkdir(path + '/Tables')
        os.mkdir(path + '/Tables/months')
        os.mkdir(path + '/Tables/years')
        os.mkdir(path + '/txtFiles')
        date = open(path + '/txtFiles/last_day_company.txt', 'w')
        date.close()

    def set_image(self):
        self.filename = QFileDialog.getOpenFileName(self, 'Выберите картинку', '', 'Картинки (*.jpg)')[0]


# Sign in window
class Start(QMainWindow):

    def __init__(self):
        super().__init__()
        # UI
        self.ConnectUI()

    # Set window
    def ConnectUI(self):
        name_ui = 'ui_windows/sign_in.ui'
        uic.loadUi(name_ui, self)
        self.setWindowTitle("ExpenseTracker")
        self.setWindowIcon(QIcon('sources/icons/menu/main.png'))
        self.setFixedSize(360, 240)
        self.Username.setAlignment(Qt.AlignCenter)
        self.Password.setAlignment(Qt.AlignCenter)
        self.connect_buttons()

    def connect_buttons(self):
        self.sign_in.clicked.connect(self.sign_in_account)
        self.create_account.clicked.connect(self.create_new_account)

    def create_new_account(self):
        global registration_widget
        registration_widget = RegistrationWidget()
        registration_widget.show()

    def sign_in_account(self):
        try:
            username = self.Username.text()
            password = self.Password.text()

            assert len(username) > 0
            assert len(password) > 0

            con = sqlite3.connect('sources/profiles.db')
            cur = con.cursor()
            user = cur.execute("""SELECT * FROM profiles
                                    WHERE username = ? AND password = ?""",
                               (username, password)).fetchone()
            if user:
                self.connect_widget(username)
                global USER
                USER = []
                USER += list(user)
                print(USER)
            else:
                error_show('Login or password is entered incorrectly !')
        except AssertionError:
            error_show('Login or password fields were empty !')

    def connect_widget(self, username):
        global main_widget
        main_widget = MyWidget(username)
        main_widget.show()
        self.close()


class Settings(QMainWindow):
    def __init__(self):
        super().__init__()
        # UI
        self.ConnectUI()

    # Set window
    def ConnectUI(self):
        name_ui = 'ui_windows/settings.ui'
        uic.loadUi(name_ui, self)
        self.setWindowTitle("ExpenseTracker")
        self.setWindowIcon(QIcon('sources/icons/menu/main.png'))
        self.setFixedSize(360, 240)
        self.connect_buttons()

    def connect_buttons(self):
        self.edit_profil_btn.clicked.connect(self.edit_profil)
        self.current_theme.clicked.connect(self.change_theme)
        self.current_language.clicked.connect(self.change_language)
        self.exit_btn.clicked.connect(self.exit)
        self.reset_account.clicked.connect(self.change_profil)

    def exit(self):
        sys.exit(True)

    def edit_profil(self):
        global edit_profil
        edit_profil = EditProfil()
        edit_profil.show()
        edit_profil.create_account.setText('Set')
        edit_profil.Title.setText('Edit Profil')
        edit_profil.Title.setAlignment(Qt.AlignCenter)

    def change_theme(self):
        text = 'Dark' if self.sender().text() == 'Light' else 'Light'
        self.current_theme.setText(text)

    def change_language(self):
        text = 'Ru' if self.sender().text() == 'Eng' else 'Eng'
        self.current_language.setText(text)

    def change_profil(self):
        self.close()
        global main_widget
        main_widget.close()
        global start
        start = Start()
        start.show()


# This function show an exception, if it occurs
def error_show(text):
    global error
    error = Error(text)
    error.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    start = Start()
    start.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
