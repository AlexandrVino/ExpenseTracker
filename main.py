import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow

# import classes from my files
from files import analysis_tables
from files import charts
from files import constants
from files import first_window
from files import second_window
from files import third_window

MyTable, CurrencyTable = analysis_tables.MyTable, analysis_tables.CurrencyTable
MyChart = charts.MyChart

DATABASE = constants.get_date_base()
MONTHS = constants.MONTHS
DATE = constants.DATE


class MyWidget(QMainWindow):

    def __init__(self):
        super().__init__()
        # UI
        self.firstWidget = first_window.FirstWindow(self)
        self.secondWidget = second_window.SecondWindow(self)
        self.thirdWidget = third_window.ThirdWidget(self)
        self.list_of_widgets = [self.firstWidget, self.secondWidget, self.thirdWidget]
        self.list_of_widgets[0].connectUI()
        self.setWindowTitle("ExpenseTracker")
        self.setWindowIcon(QIcon('sources/icons/menu/main.png'))
        self.setFixedSize(1010, 750)
        self.index = 0

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


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())