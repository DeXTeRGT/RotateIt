from PyQt5 import QtWidgets, uic, QtCore, QtSerialPort, QtGui
from PyQt5.QtCore import Qt, QTimer
import sys
import Compasswidget
import xmltodict
import datetime
from UDPHelper import WorkerUDPThread
from RotorHelper import QueryRotorClass
from LoggerHelper import getLoggerHandle
from configparser import ConfigParser
from SettingsHelper import SettingsWindow
from AboutHelper import AboutWindow


ReadConfiguration = ConfigParser()
ReadConfiguration.read('config/Configuration.conf')

logger  = getLoggerHandle()

class Ui(QtWidgets.QMainWindow):
    SerialOK = False

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('./resources/AntRot.ui', self)

        self.setWindowIcon(QtGui.QIcon('resources/icon.png'))

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedSize(260, 520)

        self.dialog = SettingsWindow(self)
        self.AboutDialog = AboutWindow(self)

        self.fs_watcher = QtCore.QFileSystemWatcher(['config/Configuration.conf'])
        self.fs_watcher.fileChanged.connect(self.file_changed)
        
        self.FirstTimer = QTimer()
        self.FirstTimer.setTimerType(QtCore.Qt.VeryCoarseTimer)
        self.FirstTimer.timeout.connect(self.StartScheduledRotor)

        self.SecondTimer = QTimer()
        self.SecondTimer.setTimerType(QtCore.Qt.VeryCoarseTimer)
        self.SecondTimer.timeout.connect(self.StartScheduledRotor)

        self.RotDetails.setText('<font color=blue>'+ ReadConfiguration.get('ROTOR','ROTOR_ID') + " / " + ReadConfiguration.get('ROTOR','STATION_CALL') + "@" + ReadConfiguration.get('ROTOR','STATION_GRID')+ '</font>')
        self.IfLabel.setText("IF: " +  ReadConfiguration.get('UDP_SERVER','UDP_LISTEN_IF'))
        self.PortLabel.setText("PORT: " +  ReadConfiguration.get('UDP_SERVER','UDP_LISTEN_PORT'))

        self.ComPort.setText("PORT: " +  ReadConfiguration.get('SERIAL_COM','SERIAL_PORT'))
        self.ComPortBaud.setText("BAUD: " +  ReadConfiguration.get('SERIAL_COM','SERIAL_BAUD'))

        if (ReadConfiguration.getboolean('UDP_SERVER','UDP_RUN_SERVER')):
            self.UdpServer.setText("UDP STATE <font color=green>RUN</font")
        else:
            self.UdpServer.setText("UDP STATE <font color=red>STOP</font>")


        if (ReadConfiguration.getboolean('SCHED','SCHED_ENABLE')):
            
            

            self.CurrentTime = datetime.datetime.strptime(datetime.datetime.strftime(datetime.datetime.now(),'%H:%M:%S'), '%H:%M:%S')
            self.ScheduledTime = datetime.datetime.strptime(ReadConfiguration.get('SCHED','SCHED_TIME'), '%H:%M:%S')  

            logger.info("Current time is: " + str(self.CurrentTime))
            logger.info("Scheduled time is: " + str(self.ScheduledTime))

            self.diff = (self.ScheduledTime - self.CurrentTime) 
            logger.info("Timer will trigger after: " + str(int(self.diff.seconds/60)) + " minutes")        
            
            self.FirstTimer.start(self.diff.seconds * 1000)
        else:
            logger.info ("Scheduler is configured but the Scheduler was not enabled")

        selfSerialWorker = QueryRotorClass()
        self.SerialWorkerThread = QtCore.QThread()
        self.SerialWorkerThread.started.connect(selfSerialWorker.run)
        selfSerialWorker.GetAZ.connect(self.SerialSendData)
        selfSerialWorker.moveToThread(self.SerialWorkerThread)  # Move the Worker object to the Thread object
        self.SerialWorkerThread.start()


        self.UDPWorker = WorkerUDPThread()
        self.UDPWorkerThread = QtCore.QThread()
        self.UDPWorkerThread.started.connect (self.UDPWorker.start)
        self.UDPWorker.UpdateUDP.connect(self.UpdateUDP)
        self.UDPWorker.moveToThread(self.UDPWorkerThread)
        self.UDPWorkerThread.start()

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

    def StartScheduledRotor(self):
        ReadConfiguration.read('config/Configuration.conf')
        if (abs(ReadConfiguration.getint('SCHED','SCHED_HEDDING') - int(self.Compasswidget.getAngle()))  > ReadConfiguration.getint('SCHED','SCHED_HEDDING_TOLERANCE')):
            SetHeddingTo = 'M' + ReadConfiguration.get('SCHED','SCHED_HEDDING') + '\r\n'
            self.SerialIO_Send(SetHeddingTo)
            self.Compasswidget.setSecAngle(int(ReadConfiguration.get('SCHED','SCHED_HEDDING')))
            logger.critical("Schedule triggered - moving antenna to hedding: " + ReadConfiguration.get('SCHED','SCHED_HEDDING') + " deg")
            self.FirstTimer.stop()
            self.SecondTimer.stop()
        else:
            print(ReadConfiguration.getint('SCHED','SCHED_HEDDING'))
            print(self.Compasswidget.getAngle())
            print(abs(ReadConfiguration.getint('SCHED','SCHED_HEDDING') - int(self.Compasswidget.getAngle())))
            logger.warning ("Scheduled hedding is within set tolerance - scheduler triggered but antenna will not be moved")
            self.FirstTimer.stop()
            self.SecondTimer.stop()

    @QtCore.pyqtSlot(str)
    def file_changed(self,path):
        self.FirstTimer.stop()
        ReadConfiguration.read('config/Configuration.conf')
        if (ReadConfiguration.getboolean('SCHED','SCHED_ENABLE')):
            self.CurrentTime = datetime.datetime.strptime(datetime.datetime.strftime(datetime.datetime.now(),'%H:%M:%S'), '%H:%M:%S')
            self.ScheduledTime = datetime.datetime.strptime(ReadConfiguration.get('SCHED','SCHED_TIME'), '%H:%M:%S')  

            logger.info("Current time is *: " + str(self.CurrentTime))
            logger.info("Scheduled time is *: " + str(self.ScheduledTime))

            self.diff = (self.ScheduledTime - self.CurrentTime) 
            logger.info("Timer will trigger after *: " + str(int(self.diff.seconds/60)) + " minutes")        
            
            self.SecondTimer.start(self.diff.seconds * 1000)
        else:
            logger.info ("Scheduler is configured but the Scheduler was not enabled")

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
        print(data)
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

