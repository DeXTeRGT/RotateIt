from PyQt5 import QtWidgets, uic, QtCore, QtSerialPort, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QObject
import sys
import Compasswidget
import xmltodict
from UDPHelper import WorkerUDPThread
from RotorHelper import QueryRotorClass
from LoggerHelper import getLoggerHandle
from configparser import ConfigParser
from SettingsHelper import SettingsWindow
from AboutHelper import AboutWindow

ReadConfiguration = ConfigParser()
ReadConfiguration.read('Configuration.conf')

logger  = getLoggerHandle()

class Ui(QtWidgets.QMainWindow):
    SerialOK = False

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('AntRot.ui', self)

        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedSize(260, 520)

        self.dialog = SettingsWindow(self)
        self.AboutDialog = AboutWindow(self)

        self.RotDetails.setText('<font color=blue>'+ ReadConfiguration.get('ROTOR','ROTOR_ID') + " / " + ReadConfiguration.get('ROTOR','STATION_CALL') + "@" + ReadConfiguration.get('ROTOR','STATION_GRID')+ '</font>')
        self.IfLabel.setText("IF: " +  ReadConfiguration.get('UDP_SERVER','UDP_LISTEN_IF'))
        self.PortLabel.setText("PORT: " +  ReadConfiguration.get('UDP_SERVER','UDP_LISTEN_PORT'))

        self.ComPort.setText("PORT: " +  ReadConfiguration.get('SERIAL_COM','SERIAL_PORT'))
        self.ComPortBaud.setText("BAUD: " +  ReadConfiguration.get('SERIAL_COM','SERIAL_BAUD'))

        if (ReadConfiguration.getboolean('UDP_SERVER','UDP_RUN_SERVER')):
            self.UdpServer.setText("UDP STATE <font color=green>RUN</font")
        else:
            self.UdpServer.setText("UDP STATE <font color=red>STOP</font>")

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

        self.Settings.pressed.connect(self.DoSettings)
        self.About.pressed.connect(self.DoAbout)

        self.ccw.pressed.connect(self.CCWClicked)
        self.ccw.released.connect(self.CCWReleased)

        self.cw.pressed.connect(self.CWClicked)
        self.cw.released.connect(self.CWReleased)

        self.stop.pressed.connect(self.StopClicked)
        self.go.pressed.connect (self.GoToHedding)
        self.goToHedding.returnPressed.connect(self.GoToHedding)
    
        self.SerialIO = QtSerialPort.QSerialPort(ReadConfiguration.get('SERIAL_COM','SERIAL_PORT'), baudRate=ReadConfiguration.getint('SERIAL_COM','SERIAL_BAUD'), readyRead=self.SerialIO_Receive)

        logger.info("Trying to open Serial Port")
        if(self.SerialIO.open(QtCore.QIODevice.ReadWrite)):
            self.SerialOK = True
            logger.info("Serial Port Opened OK")
        else:
            self.SerialOK = False
            logger.critical("Error opening Serial Port - please check settings or PORT NUMBER in configuration file")

        self.show()

    @QtCore.pyqtSlot()
    def SerialIO_Receive(self):
        if (self.SerialOK):
            while self.SerialIO.canReadLine():
                logger.debug ("Event triggered for Incoming Serial Data")
                self.SerialReceiveData(self.SerialIO.readLine().data().decode().rstrip())
        else:
            logger.critical ("Serial Port communication error - I might retry next pass... or not")
            if (self.SerialIO.open(QtCore.QIODevice.ReadWrite)):
                self.SerialOK = True
            else:
                logger.critical ("Serial Port communication error - You haven't solve your serial port problems huh?!")
                self.SerialOK = False

    @QtCore.pyqtSlot()
    def SerialIO_Send(self, SerialIO_Data):
        logger.debug ("Event triggered for Outgoing Serial Data")
        if (self.SerialOK):
            self.SerialIO.write(SerialIO_Data.encode())
        else:
            logger.critical ("Serial Port communication error - I might retry next pass... or not")
            if (self.SerialIO.open(QtCore.QIODevice.ReadWrite)):
                self.SerialOK = True
            else:
                logger.critical ("Serial Port communication error - You haven't solve your serial port problems huh?!")
                self.SerialOK = False


    def SerialSendData(self, SerialIO_Data):
        self.SerialIO_Send(SerialIO_Data)

    def SerialReceiveData(self, SerialIO_Data):
        if SerialIO_Data[:2] == "AZ":
            self.Compasswidget.setAngle(int(SerialIO_Data[3:]))
            logger.debug("Received AZ VALUE: " + SerialIO_Data[3:] + " deg from ROTOR")

    def UpdateUDP(self, udp_data):
        data = xmltodict.parse(udp_data)
        try:
            if data.get('PST') is not None:
                logger.debug ("Received an UDP package from DXLog")

                if data['PST'].get('STOP') is not None:
                    logger.debug ("Received STOP command via UDP Client from DXLog")
                    SerialCommand = 'S' + '\r\n' 
                    self.SerialIO_Send(SerialCommand)

                if data['PST'].get('AZIMUTH') is not None:
                    logger.debug ("Received MOVE command via UDP Client from DXLog")
                    SerialCommand = 'M' + data['PST']['AZIMUTH'] + '\r\n'
                    self.SerialIO_Send(SerialCommand)
                    self.Compasswidget.setSecAngle(int(data['PST']['AZIMUTH']))

            if data.get('N1MMRotor') is not None:
                logger.debug ("Received an UDP package from N1MM")

                if data['N1MMRotor'].get('goazi') is not None:
                    logger.debug ("Received MOVE command via UDP Client from N1MM")
                    SerialCommand = 'M' + data['N1MMRotor']['goazi'][:-2] + '\r\n'
                    self.SerialIO_Send(SerialCommand)
                    self.Compasswidget.setSecAngle(int(float(data['N1MMRotor']['goazi'])))

                if data['N1MMRotor'].get('stop') is not None:
                    logger.debug ("Received STOP command via UDP Client from N1MM")
                    SerialCommand = 'S' + '\r\n' 
                    self.SerialIO_Send(SerialCommand)

        except:
            logger.critical("Received an unparsable package via UDP - dumping data: " +  data)
            pass


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

    def DoSettings(self):
        self.dialog.show()

    def DoAbout(self):
        self.AboutDialog.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())

