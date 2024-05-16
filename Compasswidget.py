from PyQt5 import QtWidgets, QtCore, QtGui
# from mainwindow import Ui_MainWindow
from PyQt5.QtGui import QPainter, QPolygon, QFont, QFontMetricsF, QPen, QPalette, QColor, QBrush, QPainterPath
from PyQt5.QtCore import QPointF, QPoint, Qt, QLineF
from configparser import ConfigParser

ReadConfiguration = ConfigParser()
ReadConfiguration.read('config/Configuration.conf')


class Compasswidget(QtWidgets.QLabel):

    BeamAngle = ReadConfiguration.getint('ANTENNA','ANTENNA_BEAM_WIDTH_DEG')
    ShowAntennaBW = ReadConfiguration.getboolean('ANTENNA','SHOW_ANTENNA_BEAM_WIDTH')
    def __init__(self, parent):
        super(Compasswidget, self).__init__(parent)

        self.setStyleSheet('QFrame {background-color:(239,100,100);}')
        self.resize(341, 341)
        self._angle = 0
        self._secangle = 0
        self._margins = 10
        self._pointText = {0: "0", 30: "30", 60: "60", 90: "90", 120: "120",150: "150", 180: "180", 210: "210",240: "240", 270:"270", 300:"300", 330:"330"}

    def paintEvent(self, event):

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor(168, 34, 3))
        self.drawMarkings(painter)
        self.drawNeedle(painter)
        self.drawSecNeedle(painter)
        painter.end()

    def drawMarkings(self, painter):

        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        scale = min((self.width() - self._margins) / 120,
                    (self.height() - self._margins) / 120)
        painter.scale(scale, scale)

        font = QFont(self.font())
        font.setPixelSize(5)
        metrics = QFontMetricsF(font)

        painter.setFont(font)
        painter.setPen(self.palette().color(QPalette.Shadow))



        i = 0
        while i < 360:
            if i % 30 == 0:
                painter.setPen(Qt.red)
                painter.drawLine(0, -40, 0, -50)
                painter.drawText(QPointF(-metrics.width(self._pointText[i]) / 2, -52),
                                  self._pointText[i])
            else:
                painter.drawLine(0, -45, 0, -50)

            painter.rotate(30)
            i += 30

        i = 0
        while i < 360:
            if i % 30 !=0:
                if i % 5 == 0:
                    painter.setPen(Qt.black)
                    painter.drawLine(0, -45, 0, -50)
            painter.rotate(5)
            i += 5

        


        painter.restore()

    def drawNeedle(self, painter):

        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self._angle)
        scale = min((self.width() - self._margins) / 120,
                        (self.height() - self._margins) / 120)
        painter.scale(scale, scale)

        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(self.palette().brush(QPalette.Shadow))

        painter.setPen(QtCore.Qt.red)
        painter.drawLine(0, 0, 0, -45)
        
        painter.setPen(Qt.red)
        painter.setBrush(QBrush(QColor(255,0,0), Qt.SolidPattern))
        painter.drawPolygon(
            QPolygon([QPoint(-5, -25), QPoint(0, -45), QPoint(5, -25),
            QPoint(0, -30), QPoint(-5, -25)])
            )

        if (self.ShowAntennaBW):
            painter.setPen(QPen(QColor(255,51,255,100), 2, Qt.DotLine))
            BeamWidthOne = QLineF()
            BeamWidthTwo = QLineF()

            BeamWidthOne.setP1(QPointF(0.1,0.1))
            BeamWidthOne.setAngle(90 + (self.BeamAngle/2))
            BeamWidthOne.setLength(50)

            BeamWidthTwo.setP1(QPointF(0.1,0.1))
            BeamWidthTwo.setAngle(90- (self.BeamAngle/2))
            BeamWidthTwo.setLength(50)

            painter.drawLine (BeamWidthOne)
            painter.drawLine (BeamWidthTwo)

        
        painter.restore()

    def drawSecNeedle(self, painter):

        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self._secangle)
        scale = min((self.width() - self._margins) / 120,
                        (self.height() - self._margins) / 120)
        painter.scale(scale, scale)

        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(self.palette().brush(QPalette.Shadow))

        painter.setPen(QtCore.Qt.blue)
        painter.drawLine(0, 0, 0, -45)

        painter.setPen(QtCore.Qt.green)

        painter.setPen(Qt.black)
        painter.drawPolygon(
            QPolygon([QPoint(-5, -25), QPoint(0, -45), QPoint(5, -25),
            QPoint(0, -30), QPoint(-5, -25)])
            )

        painter.restore()

    def setAngle(self, angle):

        if angle != self._angle:
            self._angle = angle
            self.update()

    def setSecAngle(self, angle):

        if angle != self._secangle:
            self._secangle = angle
            self.update()
    
    def getAngle(self):
        return self._angle