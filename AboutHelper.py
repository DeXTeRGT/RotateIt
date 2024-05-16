from PyQt5 import QtWidgets, uic

class AboutWindow (QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        super(AboutWindow, self).__init__(parent)
        uic.loadUi('resources/About.ui', self)