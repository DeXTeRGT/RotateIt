from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QMessageBox
from configparser import ConfigParser
from LoggerHelper import getLoggerHandle

ReadConfiguration = ConfigParser()
ReadConfiguration.read('config/Configuration.conf')
logger  = getLoggerHandle()

class SettingsWindow (QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        super(SettingsWindow, self).__init__(parent)
        uic.loadUi('resources/Settings.ui', self)
        self.LoadSettings()
        self.setFixedSize(250, 370)
        self.setWindowIcon(QtGui.QIcon('resources/wrench.png'))
        self.SaveComSettings.clicked.connect(self.SaveSettings)


    def LoadSettings(self):
        self.ComPortList.addItems([ port.portName() for port in QSerialPortInfo().availablePorts() ])

        self.ComPortList.setCurrentText(ReadConfiguration.get('SERIAL_COM','SERIAL_PORT'))
        self.BaudRateList.setCurrentText(ReadConfiguration.get('SERIAL_COM','SERIAL_BAUD'))

        self.UDPServerEnabled.setChecked(ReadConfiguration.getboolean('UDP_SERVER','UDP_RUN_SERVER'))
        self.IPAddress.setText(ReadConfiguration.get('UDP_SERVER','UDP_LISTEN_IF'))
        self.IPPort.setText(ReadConfiguration.get('UDP_SERVER','UDP_LISTEN_PORT'))

        self.RotorID.setText(ReadConfiguration.get('ROTOR','ROTOR_ID'))
        self.StationCall.setText(ReadConfiguration.get('ROTOR','STATION_CALL'))
        self.StationGrid.setText(ReadConfiguration.get('ROTOR','STATION_GRID'))
        self.RotorQueryInterval.setText(str(ReadConfiguration.getfloat('ROTOR','ROTOR_QUERY_INTERVAL')))

        self.ShowAntennaBeam.setChecked(ReadConfiguration.getboolean('ANTENNA','SHOW_ANTENNA_BEAM_WIDTH'))
        self.BeamWidth.setText(ReadConfiguration.get('ANTENNA','ANTENNA_BEAM_WIDTH_DEG'))

        self.DebugLevel.setCurrentText(ReadConfiguration.get('LOGGER','LOG_LEVEL'))
        self.LogToFile.setChecked(ReadConfiguration.getboolean('LOGGER','LOG_TO_FILE'))
        self.LogName.setText(ReadConfiguration.get('LOGGER','LOG_FILE_NAME'))

        self.SchedEnable.setChecked(ReadConfiguration.getboolean('SCHED','SCHED_ENABLE'))
        self.SchedTime.setText(ReadConfiguration.get('SCHED','SCHED_TIME'))
        self.SchedHedding.setValue(ReadConfiguration.getint('SCHED','SCHED_HEDDING'))
        self.HeddingTolerance.setText(ReadConfiguration.get('SCHED','SCHED_HEDDING_TOLERANCE'))

    def CreateInfoDlg(self,DlgText):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText(DlgText)
        msg.setWindowTitle("RotateIT")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        self.hide()

    def CreateCriticalDlg(self,DlgText):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.critical)
        msg.setText(DlgText)
        msg.setWindowTitle("RotateIT")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        self.hide()


    def SaveSettings (self):

        ReadConfiguration.set('SERIAL_COM','SERIAL_PORT',self.ComPortList.currentText())
        ReadConfiguration.set('SERIAL_COM','SERIAL_BAUD',self.BaudRateList.currentText())

        ReadConfiguration.set('UDP_SERVER','UDP_RUN_SERVER',str(self.UDPServerEnabled.isChecked()))
        ReadConfiguration.set('UDP_SERVER','UDP_LISTEN_IF',self.IPAddress.text())
        ReadConfiguration.set('UDP_SERVER','UDP_LISTEN_PORT',self.IPPort.text())

        ReadConfiguration.set('ROTOR','ROTOR_ID',self.RotorID.text())
        ReadConfiguration.set('ROTOR','STATION_CALL',self.StationCall.text())
        ReadConfiguration.set('ROTOR','STATION_GRID',self.StationGrid.text())
        ReadConfiguration.set('ROTOR','ROTOR_QUERY_INTERVAL',self.RotorQueryInterval.text())

        ReadConfiguration.set('ANTENNA','SHOW_ANTENNA_BEAM_WIDTH',str(self.ShowAntennaBeam.isChecked()))
        ReadConfiguration.set('ANTENNA','ANTENNA_BEAM_WIDTH_DEG',self.BeamWidth.text())

        ReadConfiguration.set('LOGGER','LOG_LEVEL',self.DebugLevel.currentText())
        ReadConfiguration.set('LOGGER','LOG_TO_FILE',str(self.LogToFile.isChecked()))
        ReadConfiguration.set('LOGGER','LOG_FILE_NAME',self.LogName.text())

        ReadConfiguration.set('SCHED','SCHED_ENABLE',str(self.SchedEnable.isChecked()))
        ReadConfiguration.set('SCHED','SCHED_TIME',self.SchedTime.text())
        ReadConfiguration.set('SCHED','SCHED_HEDDING',str(self.SchedHedding.value()))
        ReadConfiguration.set('SCHED','SCHED_HEDDING_TOLERANCE',str(self.HeddingTolerance.text()))
        
        with open('config/Configuration.conf', 'w') as configfile:
            ReadConfiguration.write(configfile)
            
        logger.debug ("Settings were saved successfully! Well done!")
        self.CreateInfoDlg("Settings were saved successfully! \n Please restart to load new settings!")