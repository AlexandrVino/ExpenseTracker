import sqlite3
from datetime import timedelta

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# import classes from my files
from files import constants

DATABASE = constants.get_date_base()
MONTHS = constants.MONTHS
DATE = constants.DATE


class ThirdWidget(QtWidgets.QMainWindow):

    def __init__(self, parent):
        super().__init__()

        # UI
        self.current_month = MONTHS[DATE.now().month]
        self.parent = parent
        self.connectUI()

    # Connecting third window
    def connectUI(self):
        name_ui = 'ui_windows/main_window3.ui'
        uic.loadUi(name_ui, self.parent)

        self.connect_history()
        self.connect_buttons()

        self.update_info()

    # Connecting info with labels
    def update_info(self):
        con = sqlite3.connect('sources/DataBases/dbFiles/payments.db')
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
                self.parent.selected_type.addItem(str(elem[0]), i)
                self.parent.selected_type_2.addItem(str(elem[0]), i)

        con = sqlite3.connect('sources/DataBases/dbFiles/cards.db')
        cur = con.cursor()
        text = [list(elem) for elem in cur.execute("""SELECT * FROM card""").fetchall()]
        con.close()
        if any(text):
            self.parent.select_bank.clear()
            self.parent.select_card_name.clear()
            self.parent.select_card_name_2.clear()
            self.parent.select_digits.clear()

            for elem in text:
                self.parent.select_bank.addItem(str(elem[1]))
                self.parent.select_card_name.addItem(str(elem[1]) + ' ' + 4 * '*' + ' ' + str(elem[2]))
                self.parent.select_card_name_2.addItem(str(elem[1]) + ' ' + 4 * '*' + ' ' + str(elem[2]))
                self.parent.select_digits.addItem(4 * '*' + ' ' + str(elem[2]))

    def connect_buttons(self):
        # connect footer buttons
        self.parent.pay.clicked.connect(self.payment)
        self.parent.add_card.clicked.connect(self.set_cards)
        self.parent.remove_card.clicked.connect(self.set_cards)
        self.active_button = 'Yes'
        for button in self.parent.type_payment.buttons():
            button.clicked.connect(self.set_type_payment)

        for button in self.parent.set_payment_type.buttons():
            button.clicked.connect(self.set_payment_types)
        for button in self.parent.footerbuttons.buttons():
            button.clicked.connect(self.parent.change_window)

    # Add new payment
    def payment(self):
        try:
            type_payment = self.parent.selected_type.currentText()

            prise = float(self.parent.prise.text())
            date = self.parent.date.text()
            state = self.active_button
            # card_name = self.parent.card.text()

            assert prise > 0
            # assert card_name in CARDS

            flag = True if state.lower() == 'yes' else False
            con = sqlite3.connect('sources/DataBases/dbFiles/payments.db')
            cur = con.cursor()
            text = cur.execute("""SELECT id FROM history""").fetchall()

            try:
                text = max(set([elem[0] for elem in text]))
                last_id = text + 1
            except ValueError:
                last_id = 1

            type_payment = cur.execute("""SELECT id FROM types_payments
                                            WHERE type_name = ?""", (type_payment,)).fetchone()[0]
            cur.execute("""INSERT INTO history(id, type_of_payment, date, prise, type) VALUES(?, ?, ?, ?, ?)""",
                        (last_id, type_payment, date, prise, flag))
            if flag:
                DATABASE[MONTHS[int(date.split('.')[1])]].mytable.add_payment(self.parent.selected_type.currentText(),
                                                                              prise, int(date.split('.')[0]))
            con.commit()
            con.close()
            self.connect_history()

        except AssertionError:
            pass
        except ValueError:
            pass

    def set_payment_types(self):
        if self.sender().objectName() == 'add_type':
            text = self.parent.new_type_payment.text()
            if text:
                con = sqlite3.connect('sources/DataBases/dbFiles/payments.db')
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
            text = self.parent.selected_type_2.currentText()
            if text:
                con = sqlite3.connect('sources/DataBases/dbFiles/payments.db')
                cur = con.cursor()
                cur.execute("""DELETE from types_payments
                                WHERE type_name = ?""", (text,))

                con.commit()
                con.close()
                self.update_info()

    # Connecting history of payments
    def connect_history(self):
        con = sqlite3.connect('sources/DataBases/dbFiles/payments.db')
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
            months[12] = 'Yesterday'
            months[13] = 'Today'

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
            widget.resize(310, 493)
            widget.setStyleSheet('border-radius: 10px;' 'background-color: 0;')

            type_pay = QtWidgets.QLabel(widget)
            type_pay.resize(280, 40)
            type_pay.move(25, 215)
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
        con = sqlite3.connect('sources/DataBases/dbFiles/cards.db')
        cur = con.cursor()
        if self.sender().objectName() == 'add_card':
            bank = self.parent.bank_name.text()
            digits = self.parent.digits.text()
            for i in range(10):
                self.parent.select_bank.removeItem(i)
                self.parent.select_digits.removeItem(i)
            text = cur.execute("""SELECT card_id FROM card""").fetchall()

            try:
                text = max(set([elem[0] for elem in text]))
                last_id = text + 1
            except ValueError:
                last_id = 1

            cur.execute("""INSERT INTO card(card_id, bank_name, digits) VALUES(?, ?, ?)""",
                        (last_id, bank, digits,))
            con.commit()
            con.close()
        else:

            bank = self.parent.select_bank.currentText()
            digits = self.parent.select_digits.currentText().split()[1]
            cur.execute("""DELETE from card
                WHERE bank_name = ? AND digits = ?""", (bank, digits,))
            con.commit()
            con.close()
        self.connectUI()
