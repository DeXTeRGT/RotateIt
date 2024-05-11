from PyQt5 import QtWidgets, uic, QtCore, QtSerialPort, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QObject
import sys
import Compasswidget
import xmltodict
from UDPHelper import WorkerUDPThread
from RotorHelper import QueryRotorClass
from LoggerHelper import getLoggerHandle
from configparser import ConfigParser

ReadConfiguration = ConfigParser()
ReadConfiguration.read('Configuration.conf')

logger  = getLoggerHandle()

class Communicate(QObject):
    sig = pyqtSignal(str)

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('AntRot.ui', self)

        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setWindowTitle(ReadConfiguration.get('ROTOR','ROTOR_ID') + " / " + ReadConfiguration.get('ROTOR','STATION_CALL') + "@" + ReadConfiguration.get('ROTOR','STATION_GRID'))
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedSize(625, 250)

        self.worker = QueryRotorClass()
        self.SerialWorkerThread = QtCore.QThread()
        self.SerialWorkerThread.started.connect(self.worker.run)
        self.worker.GetAZ.connect(self.SerialSendData)
        self.worker.moveToThread(self.SerialWorkerThread)  # Move the Worker object to the Thread object
        self.SerialWorkerThread.start()


        self.XXWorker = WorkerUDPThread()
        self.xxThread = QtCore.QThread()
        self.xxThread.started.connect (self.XXWorker.start)
        self.XXWorker.UpdateUDP.connect(self.UpdateUDP)
        self.XXWorker.moveToThread(self.xxThread)
        self.xxThread.start()

        self.ccw.pressed.connect(self.CCWClicked)
        self.ccw.released.connect(self.CCWReleased)

        self.cw.pressed.connect(self.CWClicked)
        self.cw.released.connect(self.CWReleased)

        self.stop.pressed.connect(self.StopClicked)
        self.go.pressed.connect (self.GoToHedding)
        self.goToHedding.returnPressed.connect(self.GoToHedding)
    
        self.SerialIO = QtSerialPort.QSerialPort("COM5", baudRate=QtSerialPort.QSerialPort.Baud9600, readyRead=self.SerialIO_Receive)
        self.SerialIO.open(QtCore.QIODevice.ReadWrite)

        self.show()

    @QtCore.pyqtSlot()
    def SerialIO_Receive(self):
        while self.SerialIO.canReadLine():
            logger.debug ("Event triggered for Incoming Serial Data")
            self.SerialReceiveData(self.SerialIO.readLine().data().decode().rstrip())

    @QtCore.pyqtSlot()
    def SerialIO_Send(self, SerialIO_Data):
        logger.debug ("Event triggered for Outgoing Serial Data")
        self.SerialIO.write(SerialIO_Data.encode())

    def SerialSendData(self, SerialIO_Data):
        self.SerialIO_Send(SerialIO_Data)

    def SerialReceiveData(self, SerialIO_Data):
        if SerialIO_Data[:2] == "AZ":
            self.Compasswidget.setAngle(int(SerialIO_Data[3:]))
            logger.debug("Received AZ VALUE: " + SerialIO_Data[3:] + " deg from ROTOR")

    def UpdateUDP(self, udp_data):
        data = xmltodict.parse(udp_data)
        try:
            if data['PST'].get('STOP') is not None:
                logger.debug ("Received STOP command via UDP Client")
                SerialCommand = 'S' + '\r\n' 

            if data['PST'].get('AZIMUTH') is not None:
                logger.debug ("Received MOVE command via UDP Client")
                SerialCommand = 'M' + data['PST']['AZIMUTH'] + '\r\n'
                self.SerialIO_Send(SerialCommand)
                self.Compasswidget.setSecAngle(int(data['PST']['AZIMUTH']))
        except:
            print(data)

    def StopRotor(self):
        self.SerialIO_Send ("S\r\n")

    def CCWClicked(self):
        self.SerialIO_Send("L\r\n")
        self.ccw.setStyleSheet("border: 3px solid; border-color:red; background: green ;border-radius: 10px; color: white")
        logger.debug ("Free CCW movement issued from GUI")

    def CCWReleased(self):
        self.StopRotor()
        self.ccw.setStyleSheet("background: lime ;border-radius: 10px; color: black")
        logger.debug ("CCW BUTTON releasd issued from GUI - STOP ROTOR")

    def CWClicked(self):
        self.SerialIO_Send("R\r\n")
        self.cw.setStyleSheet("border: 3px solid; border-color:red; background: green ;border-radius: 10px; color: white")
        logger.debug ("Free CW movement issued from GUI")

    def CWReleased(self):
        self.StopRotor()
        self.cw.setStyleSheet("background: lime ;border-radius: 10px; color: black")
        logger.debug ("CW BUTTON releasd issued from GUI - STOP ROTOR")

    def StopClicked(self):
        self.StopRotor()
        logger.debug ("Full STOP issued from GUI")

    def GoToHedding(self):
        SetHeddingTo = 'M' + self.goToHedding.text() + '\r\n'
        self.SerialIO_Send(SetHeddingTo)
        self.Compasswidget.setSecAngle(int(self.goToHedding.text()))



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())

