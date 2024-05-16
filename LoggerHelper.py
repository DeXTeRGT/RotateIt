import logging
import coloredlogs
from configparser import ConfigParser

ReadConfiguration = ConfigParser()
ReadConfiguration.read('config/Configuration.conf')

coloredlogs.install(level=ReadConfiguration.get('LOGGER','LOG_LEVEL'))

LogToFile = ReadConfiguration.getboolean('LOGGER','LOG_TO_FILE')

def getLoggerHandle():
    logger = logging.getLogger(__name__)
    if (LogToFile):
        FileLogger = logging.FileHandler(r'RotateIt.log')
        FileLogger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        FileLogger.setFormatter(formatter)
        logger.addHandler(FileLogger)
    return logger