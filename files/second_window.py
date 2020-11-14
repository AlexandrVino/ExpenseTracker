from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QPixmap, QFont
from pymorphy2 import MorphAnalyzer
import sqlite3
from PyQt5.QtCore import Qt
from datetime import datetime
import requests  # Модуль для обработки URL
from bs4 import BeautifulSoup  # Модуль для работы с HTML
from pandas import read_excel, DataFrame

# import classes from my files
from files import analysis_tables
from files import charts
from files import constants
from files import errors

CurrencyTable = analysis_tables.CurrencyTable
MyChart = charts.MyChart
Error = errors.Error

DATABASE = ''
error = ''
MONTHS = constants.MONTHS
DATE = constants.DATE


class SecondWindow(QtWidgets.QMainWindow):

    def __init__(self, parent):
        super().__init__()

        # UI
        self.dollar = 1
        self.current_month = MONTHS[DATE.now().month]
        self.parent = parent
        self.path = 'sources/' + self.parent.user_name + '/DataBases'

        global DATABASE
        DATABASE = constants.get_date_base(self.parent.user_name)

        self.currency_dict = {'USD': 'Долларов',
                              'RUB': 'Российский Рубль'}
        self.connectUI()

    # Connecting second window
    def connectUI(self):
        name_ui = 'ui_windows/main_window2.ui'
        uic.loadUi(name_ui, self.parent)
        self.setFixedSize(1010, 750)

        self.connect_buttons()
        self.update_info()
        self.create_labels(['', '', '', ''])
        self.set_group_companies()

        DATABASE['currency'].name = 'exchange_rates_month'
        money = DATABASE['currency'].draw_exchange_rates(self.parent.value.currentText(), my_type='Month')
        self.parent.chart.setPixmap(QPixmap(DATABASE['currency'].directory + DATABASE['currency'].name + '.png'))

        morph_country = MorphAnalyzer().parse('Российский')[0]
        morph_currency = MorphAnalyzer().parse('Рубль')[0]

        text = [str(money), morph_country.make_agree_with_number(money).word.capitalize() + ' ' +
                morph_currency.make_agree_with_number(money).word.capitalize()]
        self.parent.currensy.setText("<html><head/><body><p align=\"center\"><span>" +
                                     text[0] + "</span></p></body></html>")
        self.parent.currensy_2.setText("<html><head/><body><p align=\"center\"><span>" +
                                       text[1] + "</span></p></body></html>")
        self.parent.value.currentTextChanged.connect(self.change_type_exchange_rates)
        self.parent.current_company_2.currentTextChanged.connect(self.set_group_companies)
        self.parent.current_company.currentTextChanged.connect(self.set_company)
        try:
            company = self.parent.current_company.currentText().strip().lower()
            if not company:
                return
            img = open(DATABASE[company].directory + DATABASE[company].name + '.png')
            img.close()
            self.parent.chart_3.setPixmap(QPixmap(DATABASE[company].directory + DATABASE[company].name + '.png'))

        except FileNotFoundError:
            self.set_company()

    # Connecting all buttons to their methods
    def connect_buttons(self):
        for button in self.parent.footerbuttons.buttons():
            button.clicked.connect(self.parent.change_window)
        for button in self.parent.time.buttons():
            button.clicked.connect(self.change_type_exchange_rates)
        for button in self.parent.time_2.buttons():
            button.clicked.connect(self.set_company)
        self.parent.find_company_btn.clicked.connect(self.find_company)
        self.parent.add_company_type_btn.clicked.connect(self.add_company_type)
        self.parent.remove_company_type_btn.clicked.connect(self.add_company_type)

    # Connecting info with labels
    def update_info(self):

        self.parent.value.clear()
        self.parent.current_company.clear()
        self.parent.current_company_2.clear()
        self.parent.type_company.clear()
        self.load_profil()

        for currency in DATABASE['currency'].mytable.cols[1:]:
            self.parent.value.addItem(' ' * (27 - len(currency)) + currency)

        con = sqlite3.connect(self.path + '/dbFiles/database.db')
        cur = con.cursor()
        companies = [list(elem)[0] for elem in cur.execute("""SELECT company_name FROM companies""").fetchall()]
        com_types = [list(elem)[0] for elem in cur.execute("""SELECT type_company FROM companies_types""").fetchall()]

        for company in companies:
            self.parent.current_company.addItem(' ' * (27 - len(company)) + company.capitalize())
        companies_2 = []
        index = 0
        for i in range(len(companies.copy())):
            if companies[i + index:i+4+index]:
                companies_2.append(companies[i + index:i+4+index])
            else:
                break
            index += 3
        for company in companies_2:
            self.parent.current_company_2.addItem(' ' * (43 - len(', '.join(company))) +
                                                  ', '.join([item.capitalize() for item in company]))

        for company_type in com_types:
            self.parent.type_company.addItem(' ' * (17 - len(company_type)) + company_type.capitalize())

        my_type = [button.text() for button in self.parent.time_2.buttons() if button.isChecked()][0]
        company = self.parent.current_company.currentText().strip().lower()
        if not company:
            return
        money = DATABASE[company].draw_company(my_type)

        text = cur.execute("""SELECT currency from companies
                                                        WHERE company_name = ?""", (company.lower(),)).fetchone()

        text = self.currency_dict[list(text)[0]]
        if len(text.split()) == 1:
            morph_country = MorphAnalyzer().parse('Долларов')[0].make_agree_with_number(money).word.capitalize()
            text = morph_country + ' США'
        else:
            morph_country = MorphAnalyzer().parse(text.split()[0])[0].make_agree_with_number(money).word.capitalize()
            morph_country_1 = MorphAnalyzer().parse(text.split()[1])[0].make_agree_with_number(money).word.capitalize()
            text = morph_country + ' ' + morph_country_1

        text = [str(money), text]
        self.parent.money_2.setText("<html><head/><body><p align=\"center\"><span>" +
                                    text[0] + "</span></p></body></html>")
        self.parent.valut.setText("<html><head/><body><p align=\"center\"><span>" +
                                  text[1] + "</span></p></body></html>")
        self.parent.name_company.setAlignment(Qt.AlignCenter)
        self.parent.type_company_2.setAlignment(Qt.AlignCenter)

    # Connecting selected time span
    def change_type_exchange_rates(self):
        try:
            my_type = [button.text() for button in self.parent.time.buttons() if button.isChecked()][0]
            DATABASE['currency'].name = 'exchange_rates_' + my_type
            exception = DATABASE['currency'].mytable.check_currency()
            if exception:
                error_show("Check your network connection \n If you do not do this, you may lose data.")
            money = DATABASE['currency'].draw_exchange_rates(self.parent.value.currentText(), my_type=my_type)

            self.parent.chart.setPixmap(QPixmap(DATABASE['currency'].directory + DATABASE['currency'].name + '.png'))

            morph_country = MorphAnalyzer().parse('Российский')[0]
            morph_currency = MorphAnalyzer().parse('Рубль')[0]

            text = [str(money), morph_country.make_agree_with_number(money).word.capitalize() + ' ' +
                    morph_currency.make_agree_with_number(money).word.capitalize()]
            self.parent.currensy.setText("<html><head/><body><p align=\"center\"><span>" +
                                         text[0] + "</span></p></body></html>")
            self.parent.currensy_2.setText("<html><head/><body><p align=\"center\"><span>" +
                                           text[1] + "</span></p></body></html>")
        except TypeError:
            return

    # Checking info from site
    def set_company(self):
        con = sqlite3.connect(self.path + '/dbFiles/database.db')
        cur = con.cursor()
        companies = [list(elem)[0] for elem in cur.execute("""SELECT company_name FROM companies""").fetchall()]
        self.dollar = float(DATABASE['currency'].draw_exchange_rates('Доллар США'))
        for company in companies:
            exception = DATABASE[company].mytable.check_company(self.dollar)
            if exception:
                error_show("Check your network connection \n If you do not do this, you may lose data.")

        my_type = [button.text() for button in self.parent.time_2.buttons() if button.isChecked()][0]
        company = self.parent.current_company.currentText().strip().lower()

        try:
            money = DATABASE[company].draw_company(my_type)
        except KeyError:
            money = 0

        if not company:
            return
        self.parent.chart_3.setPixmap(QPixmap(DATABASE[company.strip()].directory + DATABASE[company.strip()].name +
                                              '.png'))
        self.parent.money.setText(DATABASE[company.strip()].rounder)

        date = open(self.path + '/txtFiles/last_day_company.txt', 'w')
        date.write(str(datetime.now()).split()[0])
        date.close()
        text = cur.execute("""SELECT currency from companies
                                                WHERE company_name = ?""", (company.lower(),)).fetchone()

        text = self.currency_dict[list(text)[0]]
        money = money if money else 0
        if len(text.split()) == 1:
            morph_country = MorphAnalyzer().parse('Долларов')[0].make_agree_with_number(money).word.capitalize()
            text = morph_country + ' США'
        else:
            morph_country = MorphAnalyzer().parse(text.split()[0])[0].make_agree_with_number(money).word.capitalize()
            morph_country_1 = MorphAnalyzer().parse(text.split()[1])[0].make_agree_with_number(money).word.capitalize()
            text = morph_country + ' ' + morph_country_1

        text = [str(money), text]
        self.parent.money_2.setText("<html><head/><body><p align=\"center\"><span>" +
                                    text[0] + "</span></p></body></html>")
        self.parent.valut.setText("<html><head/><body><p align=\"center\"><span>" +
                                  text[1] + "</span></p></body></html>")

    # Load header
    def load_profil(self):
        con = sqlite3.connect('sources/profiles.db')
        cur = con.cursor()
        user = cur.execute("""SELECT img_directory FROM profiles
                                    WHERE username = ?""", (self.parent.user_name,)).fetchone()[0]
        try:
            self.parent.avatar.setStyleSheet('border-radius: 45px;'
                                             f"background-image: url({user}) center no-repeat;")
        except TypeError:
            pass
        self.parent.name.setText(self.parent.user_name)
        self.parent.name.setStyleSheet('color: #fff')

    # Find company bay name
    def find_company(self):
        try:
            global DATABASE
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                     'like Gecko) Chrome/88.0.4315.4 Safari/537.36',
                       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/'
                                 'webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

            s = requests.Session()
            company = self.parent.name_company.text().strip().lower()
            if not company:
                error_show('The form "Name" was empty')
                return
            type_company = self.parent.type_company.currentText().strip().lower().capitalize()
            url = f'https://www.google.com/search?q=исторические+цены+на+акции+компании+{"+".join(company.split())}' \
                  f'&oq=курс+{"+".join(company.split())}&aqs=chrome.0.69i59j0i10l7.2527j1j7&sourceid=chrome&ie=UTF-8'
            answer = s.get(url, headers=headers)
            all_href = BeautifulSoup(answer.content, 'html.parser').findAll('div', class_='yuRUbf')

            href = all_href[0].find('a')['href']
            answer = s.get(href, headers=headers)
            curr = BeautifulSoup(answer.content, 'html.parser').find('div', class_='bottom lighterGrayFont arial_11')
            curr = curr.findAll('span', class_='bold')[-1].text

            table = BeautifulSoup(answer.content, 'html.parser').findAll('table',
                                                                         class_='genTbl closedTbl historicalTbl')
            table = [elem.strip() for elem in table[0].text.split('\n') if elem.strip()]
            table = [table[i * 6:(i + 1) * 6][:2] for i in range(len(table[::6]))]

            key_0 = table[0][0]
            key_1 = table[0][1]
            if curr != 'USD':
                curr = 'USD'
                self.dollar = float(DATABASE['currency'].draw_exchange_rates('Доллар США'))
                # For PEP8
                d = self.dollar
                tb = DataFrame({key_0: [company[0] for company in table[1:][::-1]],
                                key_1: [round(float('.'.join(''.join(company[1].split('.')).split(','))) / d, 3)
                                        for company in table[1:][::-1]]})
            else:
                tb = DataFrame({key_0: [company[0] for company in table[1:][::-1]],
                                key_1: [float('.'.join(''.join(company[1].split('.')).split(',')))
                                        for company in table[1:][::-1]]})
            tb.to_excel(self.path + f'/companies/{company}.xlsx')

            con = sqlite3.connect(self.path + '/dbFiles/database.db')
            cur = con.cursor()
            text = cur.execute("""SELECT id from companies""")
            try:
                text = max(set([elem[0] for elem in text]))
                last_id = text + 1
            except ValueError:
                last_id = 1
            directory = self.path + '/companies/' + company.lower() + '.xlsx'
            cur.execute("""INSERT INTO companies(id, company_name, directory, directory_img, 
                                                 type_chart, type_company, currency) 
                            VALUES(?, ?, ?, ?, "chart", ?, ?)""",
                        (last_id, company.lower(), directory, '/'.join(self.path.split('/')[:-1])+ '/images/',
                         type_company, curr))
            con.commit()
            con.close()

            DATABASE = constants.get_date_base(self.parent.user_name)
            self.update_info()
        except TypeError:
            error_show("I can't find a company with that name")
        except requests.exceptions.ConnectionError:
            error_show("Check your network connection \n If you do not do this, you may lose data.")

    # Function added type into database
    def add_company_type(self):
        con = sqlite3.connect(self.path + '/dbFiles/database.db')
        cur = con.cursor()
        if self.sender().objectName() == 'add_company_type_btn':
            text = self.parent.type_company_2.text().lower().capitalize()
            try:
                last_id = max([list(elem)[0]
                               for elem in cur.execute("""SELECT id FROM companies_types""").fetchall()]) + 1
            except ValueError:
                last_id = 1
            cur.execute("""INSERT INTO companies_types(id, type_company) 
                                VALUES(?, ?)""",
                        (last_id, text))
        else:
            text = self.parent.type_company_2.text().lower().capitalize()
            try:
                item = list(cur.execute("""SELECT * FROM companies_types
                                            WHERE type_company = ?""", (text,)).fetchone())
            except ValueError:
                return

            cur.execute("""DELETE from companies_types
                            WHERE id = ? AND type_company = ?""", (item[0], item[1]))

        con.commit()
        con.close()
        self.update_info()

    # Function for reset group of companies
    def set_group_companies(self):
        my_type = [button.text() for button in self.parent.time_2.buttons() if button.isChecked()][0]

        try:
            companies = self.parent.current_company_2.currentText().strip().lower().split(', ')
            companies = [DATABASE[item.strip()] for i, item in enumerate(companies)]
            companies = sorted(companies, key=lambda chart: -sum(list(chart.mytable.table['Цена'])))
        except KeyError:
            return
        companies[0].draw_company(my_type, companies=companies)

        self.parent.chart_2.setPixmap(QPixmap(companies[0].directory + 'all.png'))
        self.parent.money_3.setText("<html><head/><body><p align=\"center\"><span>" +
                                    str(companies[0].rounder) + "</span></p></body></html>")

        colors = ['#ff5497', '#ffa05d', '#465bca', '#3ef3d3']
        keys = [item.name for item in companies]
        keys += [''] * (4 - len(keys))

        labels_names = [elem for elem in self.parent.companies.children() if '_' in elem.objectName()]
        labels_colors = [elem for elem in self.parent.companies.children() if '_' not in elem.objectName()]

        for i, label in enumerate(labels_names):
            if keys[i]:
                label.setStyleSheet(f'background-color: none;'
                                    f'border-radius: none;'
                                    f'color: #fff')
                label.setText(keys[i].capitalize())
                labels_colors[i].setStyleSheet(f'background-color: {colors[i]};'
                                               f'border-radius: 7px;')
            else:
                labels_colors[i].setStyleSheet(f'background-color: none;'
                                               f'border-radius: none;')
                label.setText('')

    # Function for reset group of companies
    def create_labels(self, keys):
        font = QFont()
        font.setFamily("Open Sans")
        font.setPointSize(9)
        padding_top = 30
        for i, key in enumerate(keys):
            color = QtWidgets.QLabel(self.parent.companies)
            color.resize(15, 15)
            color.move(0, padding_top + i * 25)
            color.setObjectName(str(i))
            name_company = QtWidgets.QLabel(self.parent.companies)
            name_company.resize(75, 15)
            name_company.move(25, padding_top + i * 25)
            name_company.setText(key.capitalize())
            name_company.setObjectName('1_' + str(i))
            name_company.setFont(font)


# This function show an exception, if it occurs
def error_show(text):
    global error
    error = Error(text)
    error.show()
