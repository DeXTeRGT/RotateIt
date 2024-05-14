from PyQt5 import  QtCore
import time
import socket
from LoggerHelper import getLoggerHandle
from configparser import ConfigParser

ReadConfiguration = ConfigParser()
ReadConfiguration.read('Configuration.conf')

logger  = getLoggerHandle()


class WorkerUDPThread(QtCore.QObject):
    UpdateUDP = QtCore.pyqtSignal(str)
 
    def __init__(self):
        super().__init__()
        logger.info("UDP Helper Object initialized")
        self.server_start = False

    @QtCore.pyqtSlot()
    def start(self):
        self.server_start = True

        ip = ReadConfiguration.get('UDP_SERVER','UDP_LISTEN_IF')
        port = ReadConfiguration.getint('UDP_SERVER','UDP_LISTEN_PORT')
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if (ReadConfiguration.getboolean('UDP_SERVER','UDP_RUN_SERVER')):
            try:
                self.sock.bind((ip,port))
                logger.info("Opened UDP server on interface " + ip + " and port " + str(port))
            except Exception as e:
                logger.critical(e)
            self.run()
        else:
            logger.info ("UDP Server Configured but NOT running - if is needed, please enable it from configuration file and restart")

    def run(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            logger.debug("Received DATA: " + data.decode() + " from HOST: " + str(addr[0]))
            self.UpdateUDP.emit(data.decode())
            time.sleep(0.05)
