from PyQt5 import QtWidgets, uic
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from configparser import ConfigParser

ReadConfiguration = ConfigParser()
ReadConfiguration.read('Configuration.conf')

class SettingsWindow (QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        super(SettingsWindow, self).__init__(parent)
        uic.loadUi('Settings.ui', self)
        self.LoadSettings()
        self.setFixedSize(226, 330)

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



    def SaveSettings (self):
        print(self.ComPortList.currentText())
        print(self.BaudRateList.currentText())
        print(self.UDPServerEnabled.isChecked())