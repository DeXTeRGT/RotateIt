from PyQt5 import  QtCore
import time
from LoggerHelper import getLoggerHandle
from configparser import ConfigParser

ReadConfiguration = ConfigParser()
ReadConfiguration.read('config/Configuration.conf')

logger  = getLoggerHandle()

class QueryRotorClass(QtCore.QObject):
    GetAZ = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        logger.info("Query Rotor Object initialized")
    
    @QtCore.pyqtSlot()
    def run(self):
        while True:
            logger.debug ("Sending Query to Rotor")
            self.GetAZ.emit("C\r\n")
            logger.debug ("My outstanding work is done - sleeping for " + str(ReadConfiguration.getfloat('ROTOR','ROTOR_QUERY_INTERVAL')))
            time.sleep(ReadConfiguration.getfloat('ROTOR','ROTOR_QUERY_INTERVAL'))