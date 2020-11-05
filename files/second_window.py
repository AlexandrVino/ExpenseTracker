from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QPixmap

# import classes from my files
from files import analysis_tables
from files import charts
from files import constants

CurrencyTable = analysis_tables.CurrencyTable
MyChart = charts.MyChart

DATABASE = constants.get_date_base()
MONTHS = constants.MONTHS
DATE = constants.DATE


class SecondWindow(QtWidgets.QMainWindow):

    def __init__(self, parent):
        super().__init__()

        # UI
        self.current_month = MONTHS[DATE.now().month]
        self.parent = parent
        self.connectUI()

    # Connecting second window
    def connectUI(self):
        name_ui = 'ui_windows/main_window2.ui'
        uic.loadUi(name_ui, self.parent)

        my_type = [button.text() for button in self.parent.DollarEuro.buttons() if button.isChecked()][0]

        DATABASE['currency'].name = 'exchange_rates_' + my_type
        DATABASE['currency'].draw_exchange_rates()

        self.parent.chart.setPixmap(QPixmap(DATABASE['currency'].directory + DATABASE['currency'].name + '.png'))

        self.connect_buttons()
        self.update_info()

    # Connecting all buttons to their methods
    def connect_buttons(self):
        for button in self.parent.footerbuttons.buttons():
            button.clicked.connect(self.parent.change_window)
        for button in self.parent.DollarEuro.buttons():
            button.clicked.connect(self.change_type_exchange_rates)

    # Connecting info with labels
    def update_info(self):
        pass

    # Connecting selected time span
    def change_type_exchange_rates(self):
        my_type = [button.text() for button in self.parent.DollarEuro.buttons() if button.isChecked()][0]
        DATABASE['currency'].name = 'exchange_rates_' + my_type
        DATABASE['currency'].mytable.check_currency()
        DATABASE['currency'].draw_exchange_rates(my_type)
        self.parent.chart.setPixmap(QPixmap(DATABASE['currency'].directory + DATABASE['currency'].name + '.png'))

    # test function
    def test(self):
        pass
