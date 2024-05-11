from PyQt5 import  QtCore
import time
from queue import Queue
import threading
from LoggerHelper import getLoggerHandle
from configparser import ConfigParser
import serial

logger  = getLoggerHandle()

class SerialServiceThread(QtCore.QObject):
    #UpdateAZ = QtCore.pyqtSignal(int)
    SW_Ser_RX_Q = Queue()
    SW_Ser_TX_Q = Queue()

    def __init__(self):
        super().__init__()
        try:
            self.Serial_Com = serial.Serial('COM5', baudrate=9600)
            self.Serial_Com.setDTR(False)
            self.Serial_Com.setRTS(False)
        except Exception as Exception_Text:
            print(Exception_Text)


    def HandleTX(self):
        while True:
            if self.SW_Ser_TX_Q.empty != True:
                self.Serial_Com.write (self.SW_Ser_TX_Q.get().encode())
                logger.info ("TX Thread - got a message from Q to Serial")
                time.sleep(1)

    def HandleRX(self):
        while True:
            logger.info("RX Thread")
            time.sleep(1)


    #@QtCore.pyqtSlot()
    def run(self):
        HandleRX_Thread = threading.Thread (target=self.HandleRX, daemon=True)
        HandleTX_Thread = threading.Thread (target=self.HandleTX, daemon=True)

        HandleRX_Thread.start()
        HandleTX_Thread.start()

        HandleRX_Thread.join()
        HandleTX_Thread.join()

        # while True:
        #     self.UpdateAZ.emit(int(self.SW_Ser_RX_Q.get()[3:]))
        #     time.sleep(0.05)