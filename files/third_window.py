import sqlite3
from datetime import timedelta
import sys

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# import classes from my files
from files import constants
from files import errors


DATABASE = ''
error = ''

MONTHS = constants.MONTHS
DATE = constants.DATE
Error = errors.Error


class ThirdWidget(QtWidgets.QMainWindow):

    def __init__(self, parent):
        super().__init__()

        # UI
        self.current_month = MONTHS[DATE.now().month]
        self.parent = parent
        self.path = 'sources/' + self.parent.user_name + '/DataBases'

        global DATABASE
        DATABASE = constants.get_date_base(self.parent.user_name)

        self.connectUI()

    # Connecting third window
    def connectUI(self):
        name_ui = 'ui_windows/main_window3.ui'
        uic.loadUi(name_ui, self.parent)
        self.parent.setFixedSize(1010, 750)

        self.connect_history()
        self.connect_buttons()

        self.update_info()

    # Connecting info with labels
    def update_info(self):
        self.load_profil()

        con = sqlite3.connect(self.path + '/dbFiles/payments.db')
        cur = con.cursor()
        text = [list(elem) for elem in cur.execute("""SELECT type_name FROM types_payments""").fetchall()]
        con.close()
        if any(text):
            font = QFont()
            font.setFamily("Roboto Medium")
            font.setPointSize(10)
            font.setBold(False)
            font.setWeight(50)

            self.parent.selected_type.clear()
            self.parent.selected_type_2.clear()

            for i, elem in enumerate(text):
                self.parent.selected_type.addItem(' ' * (24 - len(elem[0])) + str(elem[0]), i)
                self.parent.selected_type_2.addItem(' ' * (16 - len(elem[0])) + str(elem[0]), i)

        con = sqlite3.connect(self.path + '/dbFiles/cards.db')
        cur = con.cursor()
        text = [list(elem) for elem in cur.execute("""SELECT * FROM card""").fetchall()]
        self.create_cards(text)
        con.close()
        if any(text):
            self.parent.select_card_name_3.clear()
            self.parent.select_card_name.clear()
            self.parent.select_card_name_2.clear()

            for elem in text:
                self.parent.select_card_name_3.addItem(' ' * (20 - len(str(elem[1]) + ' ' + 4 * '*' + ' ' +
                                                                       str(elem[2]))) +
                                                       str(elem[1]) + ' ' + 4 * '*' + ' ' + str(elem[2]))

                self.parent.select_card_name.addItem(' ' * (17 - len(str(elem[1]) + ' ' + 4 * '*' + ' ' +
                                                                     str(elem[2]))) +
                                                     str(elem[1]) + ' ' + 4 * '*' + ' ' + str(elem[2]))

                self.parent.select_card_name_2.addItem(' ' * (22 - len(str(elem[1]) + ' ' + 4 * '*' + ' ' +
                                                                       str(elem[2]))) +
                                                       str(elem[1]) + ' ' + 4 * '*' + ' ' + str(elem[2]))
        self.parent.momey.setAlignment(Qt.AlignCenter)
        self.parent.bank_name.setAlignment(Qt.AlignCenter)
        self.parent.digits.setAlignment(Qt.AlignCenter)
        self.parent.new_type_payment.setAlignment(Qt.AlignCenter)
        self.parent.prise.setAlignment(Qt.AlignCenter)

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

    def connect_buttons(self):
        # connect footer buttons
        self.parent.pay.clicked.connect(self.payment)
        self.parent.add_card.clicked.connect(self.set_cards)
        self.parent.remove_card.clicked.connect(self.set_cards)
        self.parent.add_money.clicked.connect(self.deposit_money)
        self.active_button = 'Yes'
        for button in self.parent.type_payment.buttons():
            button.clicked.connect(self.set_type_payment)
        for button in self.parent.set_payment_type.buttons():
            button.clicked.connect(self.set_payment_types)
        for button in self.parent.footerbuttons.buttons():
            button.clicked.connect(self.parent.change_window)
        for button in self.parent.arrows.buttons():
            button.clicked.connect(self.change_card)

    def deposit_money(self):
        try:
            bank = self.parent.select_card_name_2.currentText().split()
            digit = bank[-1]
            bank = bank[0]
            date = self.parent.date_2.text()
            money = int(self.parent.momey.text())
            assert money > 0
            con = sqlite3.connect(self.path + '/dbFiles/cards.db')
            cur = con.cursor()
            cur.execute(f"""UPDATE card 
                        SET money = money + ?
                        WHERE bank_name = ? AND digits = ?""", (money, bank, digit))
            con.commit()
            con.close()

            DATABASE[MONTHS[int(date.split('.')[1])]].mytable.add_payment('Доход',
                                                                          money,
                                                                          int(date.split('.')[0]))

            self.connectUI()
        except AssertionError:
            error_show('You cannot deposit money that are <= zero')
        except ValueError:
            error_show('The form "Money" was empty')

    # Add new payment
    def payment(self):
        try:
            type_payment = self.parent.selected_type.currentText().strip()

            prise = float(self.parent.prise.text())
            date = self.parent.date.text()
            state = self.active_button
            card_name = self.parent.select_card_name.currentText().split()
            con = sqlite3.connect(self.path + '/dbFiles/cards.db')
            cur = con.cursor()
            money = cur.execute("""SELECT money FROM card
                                   WHERE bank_name = ? AND digits = ?""",
                                (card_name[0], card_name[-1])).fetchone()[0]
            cur.close()

            assert prise > 0
            assert int(money) - prise >= 0

            flag = True if state.lower() == 'yes' else False
            con = sqlite3.connect(self.path + '/dbFiles/payments.db')
            cur = con.cursor()
            text = cur.execute("""SELECT id FROM history""").fetchall()

            try:
                text = max(set([elem[0] for elem in text]))
                last_id = text + 1
            except ValueError:
                last_id = 1
            type_payment = cur.execute("""SELECT id FROM types_payments
                                            WHERE type_name = ?""", (type_payment,)).fetchone()[0]
            cur.execute("""INSERT INTO history(id, type_of_payment, date, prise, type, card) 
                            VALUES(?, ?, ?, ?, ?, ?)""",
                        (last_id, type_payment, date, prise, flag, ' '.join(card_name)))
            con.commit()
            con.close()
            if flag:
                DATABASE[MONTHS[int(date.split('.')[1])]].mytable.add_payment(self.parent.selected_type.currentText(),
                                                                              prise, int(date.split('.')[0]))

                con = sqlite3.connect(self.path + '/dbFiles/cards.db')
                cur = con.cursor()
                cur.execute(f"""UPDATE card 
                                SET money = money - ?
                                WHERE bank_name = ? AND digits = ?""", (prise, card_name[0], int(card_name[-1])))
                con.commit()
                con.close()
            self.connectUI()

        except AssertionError:
            prise = float(self.parent.prise.text())
            text = 'You tried to pay a payment with a price <= zero' if prise <= 0 \
                else 'There are not enough funds on the card'

            error_show(text)
        except ValueError:
            error_show('The form "Prise" was empty')

    # Add or remove payment type
    def set_payment_types(self):
        if self.sender().objectName() == 'add_type':
            text = self.parent.new_type_payment.text()
            if text:
                con = sqlite3.connect(self.path + '/dbFiles/payments.db')
                cur = con.cursor()
                last_id = [list(elem) for elem in cur.execute("""SELECT id FROM types_payments""").fetchall()]
                try:
                    last_id = max(last_id, key=lambda x: x[0])[0] + 1
                except ValueError:
                    last_id = 1
                cur.execute("""INSERT INTO types_payments(id, type_name) VALUES(?, ?)""",
                            (last_id, text,))
                con.commit()
                con.close()
                self.parent.new_type_payment.setText('')
                self.update_info()
        else:
            text = self.parent.selected_type_2.currentText().strip()
            if text:
                con = sqlite3.connect(self.path + '/dbFiles/payments.db')
                cur = con.cursor()
                cur.execute("""DELETE from types_payments
                                WHERE type_name = ?""", (text,))

                con.commit()
                con.close()
                self.update_info()

    # Connecting history of payments
    def connect_history(self):
        con = sqlite3.connect(self.path + '/dbFiles/payments.db')
        cur = con.cursor()
        text = cur.execute("""SELECT * FROM history
                            WHERE type = 1""").fetchall()
        font = QFont()
        font.setFamily("Open Sans")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)

        if any(text):
            text = list(sorted(text, key=lambda x: -x[-2]))
            text = [list(elem) for elem in text]
            type_id = [list(elem) for elem in cur.execute("""SELECT * FROM types_payments""").fetchall()]
            type_id = {elem[0]: elem[1] for elem in type_id}

            for i, item in enumerate(text):
                text[i][1] = type_id[item[1]]

            group_items = list(set([item[2] for item in text]))
            today = [str(elem) for elem in str(DATE.today().date()).split('-')[::-1]]
            yesterday = [str(elem) for elem in str(DATE.today().date() - timedelta(days=1)).split('-')[::-1]]

            for i, item in enumerate(group_items):
                if item == '.'.join(today):
                    group_items[i] = 'Today'
                elif item == '.'.join(yesterday):
                    group_items[i] = 'Yesterday'
                else:
                    key = [int(elem) for elem in item.split('.')]
                    month = MONTHS[key[1]]
                    day = str(key[0])
                    group_items[i] = day + ' ' + month

            months = MONTHS.copy()
            months[13] = 'Yesterday'
            months[14] = 'Today'

            days = [str(i) for i in range(1, 32)] + ['Yesterday', 'Today']
            group_items = sorted(group_items, key=lambda x: (list(months.values()).index(x.split()[-1]),
                                                             days.index(x.split()[0])))

            group_items = {item: [] for item in group_items[::-1]}
            for item in text:
                if item[2] == '.'.join([str(elem) for elem in today]):
                    group_items['Today'] += [[item[1], item[3]]]
                elif item[2] == '.'.join([str(elem) for elem in yesterday]):
                    group_items['Yesterday'] += [[item[1], item[3]]]
                else:
                    key = [int(elem) for elem in item[2].split('.')]
                    month = MONTHS[key[1]]
                    day = str(key[0])
                    group_items[day + ' ' + month] += [[item[1], item[3]]]

            keys = sorted(list(set([key.split()[-1] for key in group_items.keys()])),
                          key=lambda x: (list(months.values()).index(x.split()[-1])))[::-1]
            main_widget = QtWidgets.QWidget()
            y_coord = 0
            for i, month in enumerate(keys):
                title = QtWidgets.QWidget(main_widget)
                title.move(10, y_coord + 10)
                title.resize(290, 35)
                y_coord += 45
                date = QtWidgets.QLabel(title)
                date.resize(290, 25)
                date.move(0, 0)
                date.setStyleSheet('background-color: #21264b;'
                                   'border-radius:12px;'
                                   'color: #fff;'
                                   'border: none;')
                font.setPointSize(11)
                date.setFont(font)
                font.setPointSize(10)
                date.setText("<html><head/><body><p align=\"center\"><span>" +
                             month + "</span></p></body></html>")

                for key_2, value in group_items.items():
                    if key_2.split()[-1] == month:
                        if key_2 not in ['Yesterday', 'Today']:
                            subtitle = QtWidgets.QWidget(main_widget)
                            subtitle.resize(290, 20)
                            subtitle.move(0, y_coord)
                            y_coord += 30
                            date = QtWidgets.QLabel(subtitle)
                            date.resize(25, 20)
                            date.move(25, 0)
                            date.setStyleSheet('color: #fff;'
                                               'border-bottom: 2px solid #fff;'
                                               'border-radius: none;')

                            date.setFont(font)
                            day = key_2.split()[0] if len(key_2.split()[0]) == 2 else '0' + key_2.split()[0]
                            date.setText("<html><head/><body><p align=\"left\"><span>" +
                                         day + ":</span></p></body></html>")
                        for item in value:
                            new_widget = QtWidgets.QWidget(main_widget)
                            new_widget.move(20, y_coord)
                            y_coord += 30
                            new_widget.resize(260, 30)

                            type_pay = QtWidgets.QLabel(new_widget)
                            type_pay.resize(70, 20)
                            type_pay.move(10, 5)
                            type_pay.setStyleSheet(f'color: #3ef3d3;'
                                                   'border: none;')
                            type_pay.setFont(font)
                            type_pay.setText("<html><head/><body><p align=\"left\"><span>" +
                                             item[0] + "</span></p></body></html>")

                            prise = QtWidgets.QLabel(new_widget)
                            prise.resize(60, 20)
                            prise.move(200, 5)
                            prise.setStyleSheet('color: #fff;'
                                                'border: none;')
                            font.setWeight(80)
                            prise.setFont(font)
                            font.setWeight(50)
                            prise.setText("<html><head/><body><p align=\"right\"><span>" +
                                          str(item[1]) + '₽' + "</span></p></body></html>")
                            prise.setStyleSheet('color: #ff5497;'
                                                'border: none')

            main_widget.resize(315, y_coord + 30)

            self.parent.HistoryScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.parent.HistoryScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.parent.HistoryScrollArea.setWidgetResizable(False)
            self.parent.HistoryScrollArea.setWidget(main_widget)
        else:
            widget = QtWidgets.QWidget()
            widget.resize(310, 260)
            widget.setStyleSheet('border-radius: 10px;' 'background-color: 0;')

            type_pay = QtWidgets.QLabel(widget)
            type_pay.resize(280, 40)
            type_pay.move(25, 110)
            type_pay.setStyleSheet('color: #7682bf;'
                                   'border: none;'
                                   'border-radius: none;'
                                   'border-top: 1px solid #3f457c;'
                                   'border-bottom: 1px solid #3f457c;')
            type_pay.setFont(font)
            type_pay.setText("<html><head/><body><p align=\"center\"><span>" +
                             'Your history is clear!!!'.upper() + "</span></p></body></html>")

            self.parent.HistoryScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.parent.HistoryScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.parent.HistoryScrollArea.setWidgetResizable(False)
            self.parent.HistoryScrollArea.setWidget(widget)

    # add cards in widget
    def create_cards(self, cards):
        font = QFont()
        font.setFamily("Open Sans")
        font.setPointSize(13)
        font.setBold(False)
        font.setWeight(50)

        images = ['sources/cards/white_card.png', 'sources/cards/black_card.png',
                  'sources/cards/grey_card.png', 'sources/cards/blue_card.png', 'sources/cards/purple_card.png']
        colors = ['#000', '#fff', '#000', '#fff', '#fff']

        for i, card in enumerate(cards):
            widget = QtWidgets.QWidget()
            widget.resize(290, 180)
            widget.move(0, 40)

            card_name = card[1]
            digits = ('*' * 4 + ' ') * 3 + str(card[2])
            count_money = str(card[-1])

            name = QtWidgets.QLabel(widget)
            number = QtWidgets.QLabel(widget)
            money = QtWidgets.QLabel(widget)

            name.resize(180, 20)
            money.resize(100, 20)

            name.setText("<html><head/><body><p align=\"center\"><span>" +
                         card_name + "</span></p></body></html>")
            money.setText("<html><head/><body><p align=\"center\"><span>" +
                          count_money + '₽' + "</span></p></body></html>")
            number.setText(digits)

            money.setFont(font)
            name.setFont(font)
            number.setFont(font)

            number.move(110, 140)
            name.move(100, 35)
            money.move(0, 70)

            widget.setStyleSheet(f'background-image: url({images[i % len(images)]}) center no-repeat;'
                                 'border-radius: 12px;'
                                 f'color: {colors[i % len(images)]};'
                                 'border: none;')
            name.setStyleSheet(f'color: {colors[i % len(images)]};'
                               'background-color: none;'
                               'background-image: none')
            number.setStyleSheet(f'color: {colors[i % len(images)]};'
                                 'background-color: none;')
            money.setStyleSheet(f'color: {colors[i % len(images)]};'
                                'background-color: none;')
            self.parent.stackedWidget.addWidget(widget)

        for item in self.parent.stackedWidget.children():
            if item.objectName() in ['page_1', 'page_2']:
                item.setParent(None)
        self.index = 0
        self.max_index = len(cards) - 1

    def change_card(self):
        if self.sender().objectName() == 'right_arrow':
            self.index += 1
            if self.index > self.max_index:
                self.index = 0
        else:
            self.index -= 1
            if self.index < 0:
                self.index = self.max_index
        self.parent.stackedWidget.setCurrentIndex(self.index)

    def set_type_payment(self):
        if self.sender().objectName() == 'no':
            self.active_button = 'No'
            self.parent.yes.setStyleSheet('background-color: #7884C1;'
                                          'border-radius: 12px;'
                                          'color: #000000;')
            self.parent.no.setStyleSheet('background-color: #3ef3d3;'
                                         'border-radius: 12px;'
                                         'color: #000000;')
        else:
            self.active_button = 'Yes'
            self.parent.yes.setStyleSheet('background-color: #3ef3d3;'
                                          'border-radius: 12px;'
                                          'color: #000000;')
            self.parent.no.setStyleSheet('background-color: #7884C1;'
                                         'border-radius: 12px;'
                                         'color: #000000;')

    # Add or remove card
    def set_cards(self):
        con = sqlite3.connect(self.path + '/dbFiles/cards.db')
        cur = con.cursor()
        if self.sender().objectName() == 'add_card':
            try:
                bank = self.parent.bank_name.text()
                digits = self.parent.digits.text()

                assert len(bank) > 0
                assert len(digits) > 0

                self.parent.select_card_name_3.clear()
                text = cur.execute("""SELECT card_id FROM card""").fetchall()

                try:
                    text = max(set([elem[0] for elem in text]))
                    last_id = text + 1
                except ValueError:
                    last_id = 1

                cur.execute("""INSERT INTO card(card_id, bank_name, digits, money) VALUES(?, ?, ?, 0)""",
                            (last_id, bank, digits,))
                con.commit()
                con.close()
            except AssertionError:
                error_show('bank or digits are empty'.capitalize())
        else:

            bank = self.parent.select_card_name_3.currentText().split()
            digits = bank[-1]
            bank = bank[0]
            cur.execute("""DELETE from card
                WHERE bank_name = ? AND digits = ?""", (bank, digits,))
            con.commit()
            con.close()
        self.connectUI()


def error_show(text):
    global error
    error = Error(text)
    error.show()
