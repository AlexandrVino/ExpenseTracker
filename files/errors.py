from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


# Error window
class Error(QMainWindow):
    def __init__(self, text_error):
        super().__init__()
        text_error = text_error.split()
        index = 0
        string = ''
        for item in text_error:
            string += item + ' '
            if len(string) >= 21:
                index += 1
                break
            index += 1
        index = 1 if not index else index
        text_error = '\n'.join([' '.join(text_error[i:i+index]) for i in range(0, len(text_error), index)])

        self.text_error = text_error
        self.connectUI()

    def connectUI(self):
        name_ui = 'ui_windows/error.ui'
        uic.loadUi(name_ui, self)
        self.setWindowTitle('Error')
        self.setFixedSize(300, 300)
        self.setWindowIcon(QIcon('sources/error_img.png'))
        self.error_message.setText(self.text_error)
        self.error_message.setAlignment(Qt.AlignCenter)

