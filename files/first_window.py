import sqlite3

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont

# import classes from my files
from files import analysis_tables
from files import charts
from files import constants

MyTable = analysis_tables.MyTable
MyChart = charts.MyChart

DATABASE = constants.get_date_base()
MONTHS = constants.MONTHS
DATE = constants.DATE


class FirstWindow(QtWidgets.QMainWindow):
    def __init__(self, parent):
        super().__init__()

        # UI
        self.current_month = MONTHS[DATE.now().month]
        self.parent = parent
        self.connectUI()

    # Connecting first window
    def connectUI(self):
        name_ui = 'ui_windows/main_window.ui'

        uic.loadUi(name_ui, self.parent)
        self.create_months()

        try:
            img = open(DATABASE[str(DATE.now().year)].directory +
                       DATABASE[str(DATE.now().year)].name + '.png')
            img.close()
        except FileNotFoundError:
            # create and load charts
            list_months = ['sources/DataBases/Tables/months/' + value.lower() + '_costs.xlsx'
                           for key, value in MONTHS.items()]
            for file_directory in list_months:
                t = MyTable(file_directory)
                t.save_table()
                del t

            DATABASE[str(DATE.now().year)].mytable.update_year_table(list_months)
            DATABASE[self.current_month].draw_month_chart()
            DATABASE[self.current_month].draw_month_income()
            DATABASE[self.current_month].draw_diagram()
            DATABASE[str(DATE.now().year)].draw_year_chart()
        cols = DATABASE[self.current_month].draw_costs_diagram()
        self.change_labels_style(cols)

        self.parent.label_6.setText(DATABASE[str(DATE.now().year)].rounder)

        self.parent.yearchar.setPixmap(QPixmap(DATABASE[str(DATE.now().year)].directory +
                                               DATABASE[str(DATE.now().year)].name + '.png'))

        self.parent.monthchar.setPixmap(QPixmap(DATABASE[self.current_month].directory +
                                                DATABASE[self.current_month].name + '.png'))

        self.parent.monthchar_2.setPixmap(QPixmap(DATABASE[self.current_month].directory + 'income' +
                                                  DATABASE[self.current_month].name + '.png'))

        self.parent.diagram.setPixmap(QPixmap(DATABASE[self.current_month].directory + 'diagram_' +
                                              DATABASE[self.current_month].name + '.png'))

        self.parent.diagram_costs.setPixmap(QPixmap(DATABASE[self.current_month].directory + 'diagram_costs_' +
                                                    DATABASE[self.current_month].name + '.png'))

        # connect labels with sources
        self.update_info()

        # connect buttons
        self.connect_buttons()

    # Connecting all buttons to their methods
    def connect_buttons(self):
        for button in self.parent.footerbuttons.buttons():
            button.clicked.connect(self.parent.change_window)
        # connect widget menu buttons

        for button in self.parent.menubuttons.buttons():
            button.clicked.connect(self.show_chart_menu)

        # connect buttons for changing the chart type
        for button in self.parent.changeTypeChart.buttons():
            button.clicked.connect(self.change_chart_type)

        self.parent.update_button.clicked.connect(self.update_chart)

    # Enable menu, where menu_button was clicked
    def show_chart_menu(self):
        if self.sender().objectName() == 'chart_menu1':
            self.parent.widget_4.setVisible(not self.parent.widget_4.isVisible())
        elif self.sender().objectName() == 'chart_menu2':
            self.parent.widget_5.setVisible(not self.parent.widget_5.isVisible())
        elif self.sender().objectName() == 'chart_menu3':
            self.parent.widget_6.setVisible(not self.parent.widget_6.isVisible())

    # Updating chart, where button with text "update" was used
    def update_chart(self):
        list_months = ['sources/DataBases/Tables/months/' + value.lower() + '_costs.xlsx'
                       for key, value in MONTHS.items()]

        DATABASE[self.current_month].mytable = MyTable('sources/DataBases/Tables/months/' +
                                                       self.current_month.lower() +
                                                       '_costs.xlsx')
        DATABASE[self.current_month].mytable.sort()
        DATABASE[self.current_month].draw_month_chart()
        DATABASE[self.current_month].draw_month_income()
        DATABASE[self.current_month].draw_diagram()
        DATABASE[str(DATE.now().year)].mytable.update_year_table(list_months)
        DATABASE[str(DATE.now().year)].draw_year_chart()
        cols = DATABASE[self.current_month].draw_costs_diagram()
        self.change_labels_style(cols)
        self.parent.diagram_costs.setPixmap(QPixmap(DATABASE[self.current_month].directory + 'diagram_costs_' +
                                                    DATABASE[self.current_month].name + '.png'))

        self.parent.yearchar.setPixmap(QPixmap(DATABASE[str(DATE.now().year)].directory +
                                               DATABASE[str(DATE.now().year)].name + '.png'))

        self.parent.monthchar.setPixmap(QPixmap(DATABASE[self.current_month].directory +
                                                DATABASE[self.current_month].name + '.png'))

        self.parent.monthchar_2.setPixmap(QPixmap(DATABASE[self.current_month].directory + 'income' +
                                                  DATABASE[self.current_month].name + '.png'))

        self.parent.diagram.setPixmap(QPixmap('sources/images/diagram_' + self.current_month + '.png'))

        self.update_info()

    # Set chart type
    def change_chart_type(self):
        if self.sender().objectName() == 'chart1':
            DATABASE[self.current_month].type = 'chart'
            DATABASE[self.current_month].draw_month_chart()
            DATABASE[self.current_month].draw_month_income()
            self.parent.monthchar.setPixmap(QPixmap(DATABASE[self.current_month].directory +
                                                    DATABASE[self.current_month].name + '.png'))

            self.parent.widget_4.setVisible(False)

        elif self.sender().objectName() == 'chart2':
            DATABASE[str(DATE.now().year)].type = 'chart'
            DATABASE[str(DATE.now().year)].draw_year_chart()
            self.parent.yearchar.setPixmap(QPixmap(DATABASE[str(DATE.now().year)].directory +
                                                   DATABASE[str(DATE.now().year)].name + '.png'))
            self.parent.widget_5.setVisible(False)

        elif self.sender().objectName() == 'chart3':
            DATABASE[self.current_month].type = 'chart'
            DATABASE[self.current_month].draw_month_income()
            self.parent.monthchar_2.setPixmap(QPixmap(DATABASE[self.current_month].directory + 'income' +
                                                      DATABASE[self.current_month].name + '.png'))
            self.parent.widget_6.setVisible(False)

        elif self.sender().objectName() == 'hiss1':
            DATABASE[self.current_month].type = 'hiss'
            DATABASE[self.current_month].draw_month_chart()
            DATABASE[self.current_month].draw_month_income()
            self.parent.monthchar.setPixmap(QPixmap(DATABASE[self.current_month].directory +
                                                    DATABASE[self.current_month].name + '.png'))
            self.parent.monthchar_2.setPixmap(QPixmap(DATABASE[self.current_month].directory + 'income' +
                                                      DATABASE[self.current_month].name + '.png'))
            self.parent.widget_4.setVisible(False)

        elif self.sender().objectName() == 'hiss2':
            DATABASE[str(DATE.now().year)].type = 'hiss'
            DATABASE[str(DATE.now().year)].draw_year_chart()
            self.parent.yearchar.setPixmap(QPixmap(DATABASE[str(DATE.now().year)].directory +
                                                   DATABASE[str(DATE.now().year)].name + '.png'))
            self.parent.widget_5.setVisible(False)

        elif self.sender().objectName() == 'hiss3':
            DATABASE[self.current_month].type = 'hiss'
            DATABASE[self.current_month].draw_month_income()
            self.parent.monthchar_2.setPixmap(QPixmap(DATABASE[self.current_month].directory + 'income' +
                                                      DATABASE[self.current_month].name + '.png'))
            self.parent.widget_6.setVisible(False)

    # Connecting info with labels
    def update_info(self):

        self.connect_bills()
        list_of_items = [self.parent.titlemonth, self.parent.stored, self.parent.cashyear,
                         self.parent.allmoney, self.parent.titleHabites, self.parent.titlemonth_2]

        for item in list_of_items:
            text = item.text()
            if text.find('*') != -1:
                text = text[:text.find('*')]
                if item == self.parent.titlemonth or \
                        item == self.parent.stored or \
                        item == self.parent.titleHabites or \
                        item == self.parent.titlemonth_2:
                    text += self.current_month
                elif item == self.parent.cashyear:
                    text += str(DATE.now().year)
                elif item == self.parent.allmoney:
                    money = list(DATABASE[str(DATE.now().year)].mytable.table['Итого'])[0]
                    text += str(money) + ' ₽ Spent in 2020'
                item.setText(text)

            if self.current_month not in text and (item == self.parent.titlemonth or
                                                   item == self.parent.stored or
                                                   item == self.parent.titleHabites or
                                                   item == self.parent.titlemonth_2):
                text2 = text.split()[:-1]
                text = text[:1] + ' '.join(text2)
                text = text[1:]
                text += ' ' + self.current_month
                item.setText(text)

        con = sqlite3.connect('sources/DataBases/dbFiles/payments.db')
        cur = con.cursor()
        key = cur.execute("""SELECT prise FROM history
                            WHERE type = 0""").fetchall()
        key = [list(elem)[0] for elem in key]
        text = str(sum(key)) + '₽'
        self.parent.allmoney_4.setText("<html><head/><body><p align=\"left\"><span>" +
                                       text + "</span></p></body></html>")

        list_of_items = [self.parent.widget_4, self.parent.widget_5, self.parent.widget_6]

        for item in list_of_items:
            item.setVisible(False)

    # Connecting unpaid widget
    def connect_bills(self):

        con = sqlite3.connect('sources/DataBases/dbFiles/payments.db')
        cur = con.cursor()
        text = cur.execute("""SELECT * FROM history
                                WHERE type = 0""").fetchall()
        font = QFont()
        font.setFamily("Roboto Medium")
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)

        main_widget = QtWidgets.QWidget()

        if any(text):
            text = list(sorted(text, key=lambda x: -x[-1]))
            text = [list(elem) for elem in text]

            type_id = cur.execute("""SELECT * FROM types_payments""").fetchall()
            type_id = [list(elem) for elem in type_id]
            type_id = {elem[0]: elem[1] for elem in type_id}

            for i, item in enumerate(text):
                text[i][1] = type_id[item[1]]
            count = len(text[:6]) * 40
            center = round((240 - count) / 2)

            for i, elem in enumerate(text):
                new_widget = QtWidgets.QWidget(main_widget)
                new_widget.move(10, center + i * 40)
                new_widget.resize(270, 40)
                if i != 0:
                    new_widget.setStyleSheet('border-top: 1px solid #3f457c;'
                                             'border-radius: 0;'
                                             'background-color: 0;')
                else:
                    new_widget.setStyleSheet('border-radius: 0;'
                                             'background-color: 0;')

                date = QtWidgets.QLabel(new_widget)
                date.resize(70, 20)
                date.move(0, 10)
                date.setStyleSheet('background-color: #21264b;'
                                   'border-radius:10px;'
                                   'color: #7682bf;'
                                   'border: none;')
                date.setFont(font)
                date.setText("<html><head/><body><p align=\"center\"><span>" +
                             elem[2] + "</span></p></body></html>")

                type_pay = QtWidgets.QLabel(new_widget)
                type_pay.resize(70, 20)
                type_pay.move(80, 10)
                type_pay.setStyleSheet('color: #7682bf;'
                                       'border: none;')
                type_pay.setFont(font)
                type_pay.setText("<html><head/><body><p align=\"left\"><span>" +
                                 elem[1] + "</span></p></body></html>")

                prise = QtWidgets.QLabel(new_widget)
                prise.resize(60, 20)
                prise.move(140, 10)
                prise.setStyleSheet('color: #fff;'
                                    'border: none;')
                prise.setFont(font)
                prise.setText("<html><head/><body><p align=\"right\"><span>" +
                              str(elem[-2]) + '₽' + "</span></p></body></html>")

                btn = QtWidgets.QPushButton(new_widget)
                btn.resize(50, 20)
                btn.move(210, 10)
                btn.setStyleSheet('color: #fff;'
                                  'border-radius: 10px;'
                                  'background-color: #3b70eb;'
                                  'border: none;')
                btn.setFont(font)
                btn.setText('Pay now')
                btn.clicked.connect(self.remove_bill)

            main_widget.resize(310, 40 * len(text) + center)
        else:
            font = QFont()
            font.setFamily("Roboto Medium")
            font.setPointSize(8)
            font.setBold(False)
            font.setWeight(50)
            main_widget.move(10, 75)
            main_widget.resize(270, 240)
            main_widget.setStyleSheet('border-radius: 0;'
                                      'background-color: 0;')
            type_pay = QtWidgets.QLabel(main_widget)
            type_pay.resize(270, 40)
            type_pay.move(10, 100)
            type_pay.setStyleSheet('border-top: 1px solid #3f457c;'
                                   'border-bottom: 1px solid #3f457c;'
                                   'color: #7682bf;')
            type_pay.setFont(font)
            type_pay.setText("<html><head/><body><p align=\"center\"><span>" +
                             'No unpaid bills!!!'.upper() + "</span></p></body></html>")
        self.parent.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.parent.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.parent.scrollArea.setWidgetResizable(False)
        self.parent.scrollArea.setWidget(main_widget)

    # Removing unpaid widget
    def remove_bill(self):
        widgets = [widget for widget in self.sender().parentWidget().children()]
        keys = []
        for item in widgets:
            try:
                keys.append(item.text())
            except AttributeError:
                pass

        keys = [elem.split('<span>')[1] for elem in keys[:-1]] + keys[-1:]
        keys = [elem.split('</span>')[0] for elem in keys[:-1]] + keys[-1:]

        DATABASE[MONTHS[int(keys[0].split('.')[1])]].mytable.add_payment(keys[1],
                                                                         float(keys[2][:-1]),
                                                                         int(keys[0].split('.')[0]))
        con = sqlite3.connect('sources/DataBases/dbFiles/payments.db')
        cur = con.cursor()

        my_type = keys[1]
        my_type = cur.execute("""SELECT id FROM types_payments
                                    WHERE type_name = ?""", (my_type,)).fetchone()[0]

        first_id = cur.execute("""SELECT id FROM HISTORY
                                    WHERE type_of_payment = ? AND date = ? AND prise = ? AND type = 0""",
                               (my_type, keys[0], keys[2][:-1])).fetchone()[0]
        cur.execute("""UPDATE HISTORY SET type = 1 
                    WHERE id = ? AND type = 0""",
                    (first_id,))
        con.commit()
        con.close()
        self.update_info()
        self.update_chart()

    # View statistics for the current month
    def change_month(self):
        for button in self.parent.widget.children():
            if button.text() == self.current_month[:3]:
                button.setStyleSheet('border-bottom: 2px solid #fff;'
                                     'border-radius: 0;'
                                     'background-color: 0;'
                                     'color: #fff;')

        self.sender().setStyleSheet('border-bottom: 2px solid #3ef3d3;'
                                    'border-radius: 0;'
                                    'background-color: 0;'
                                    'color: #3ef3d3;')

        self.current_month = [item for item in MONTHS.values() if item[:3].lower() == self.sender().text().lower()][0]
        month_file_name = 'sources/DataBases/Tables/months/' + \
                          self.current_month + '_costs.xlsx'
        db = MyChart(MyTable(month_file_name), self.current_month,
                     'sources/images/', DATABASE[self.current_month].type)
        DATABASE[self.current_month] = db

        try:  # checking that the images have been taken
            img = open('sources/images/' + self.current_month + '.png', 'r')
            img.close()
            img = open('sources/images/' + 'diagram_' + self.current_month + '.png', 'r')
            img.close()
        except FileNotFoundError:
            db.draw_month_chart()
            db.draw_month_income()
            db.draw_diagram()
        cols = db.draw_costs_diagram()
        self.change_labels_style(cols)

        self.parent.monthchar.setPixmap(QPixmap('sources/images/' + self.current_month + '.png'))
        self.parent.monthchar_2.setPixmap(QPixmap('sources/images/' + 'income' + self.current_month + '.png'))
        self.parent.diagram.setPixmap(QPixmap('sources/images/' + 'diagram_' + self.current_month + '.png'))
        self.parent.diagram_costs.setPixmap(QPixmap(DATABASE[self.current_month].directory + 'diagram_costs_' +
                                                    DATABASE[self.current_month].name + '.png'))
        self.parent.diagram_costs.setPixmap(QPixmap(DATABASE[self.current_month].directory + 'diagram_costs_' +
                                                    DATABASE[self.current_month].name + '.png'))

        self.update_info()

    # create months widget
    def create_months(self):
        months = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                  7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        font = QFont()
        font.setFamily("Open Sans")
        font.setPointSize(7)
        for i in range(1, 13):
            button = QtWidgets.QPushButton(self.parent.widget)
            button.setObjectName(str(i))
            button.resize(20, 17)
            button.move(5 + (i - 1) * 25, 10)
            if months[i].lower() != str(self.current_month)[:3].lower():
                button.setStyleSheet('border-bottom: 2px solid #fff;'
                                     'border-radius: 0;'
                                     'background-color: 0;'
                                     'color: #fff;')
            else:
                button.setStyleSheet('border-bottom: 2px solid #3ef3d3;'
                                     'border-radius: 0;'
                                     'background-color: 0;'
                                     'color: #3ef3d3;')
            button.setText(months[i])
            button.setFont(font)
            button.clicked.connect(self.change_month)

    # Set colors in types of payments in habits
    def change_labels_style(self, items):
        font = QFont()
        font.setFamily("Roboto Medium")
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        types, colors, values = items
        color_index = 0
        text_index = 0
        list_labels = sorted(self.parent.labels.children(), key=lambda item: item.objectName())

        for i, label in enumerate(list_labels):
            label.setFont(font)
            if 'color' in label.objectName():
                label.setStyleSheet(f'background-color: {colors[color_index]};'
                                    'border-radius:10px;'
                                    'border: none;')
                color_index += 1
            else:
                label.setStyleSheet('background-color: none;'
                                    'border-radius:none;'
                                    'border: none;'
                                    'color: #fff;')
                label.setText(str(types[text_index]))
                text_index += 1
        self.parent.label_11.setText("<html><head/><body><p align=\"center\"><span>" +
                                     str(sum(values)) + '₽' + "</span></p></body></html>")
        font.setPointSize(11)
        self.parent.label_11.setFont(font)
