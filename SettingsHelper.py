from PyQt5 import QtWidgets, uic, QtCore, QtSerialPort, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QObject

class SettingsWindow (QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        super(SettingsWindow, self).__init__(parent)
        uic.loadUi('Settings.ui', self)