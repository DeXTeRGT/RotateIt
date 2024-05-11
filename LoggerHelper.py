import logging
import coloredlogs
from configparser import ConfigParser

ReadConfiguration = ConfigParser()
ReadConfiguration.read('Configuration.conf')


coloredlogs.install(level=ReadConfiguration.get('LOGGER','LOG_LEVEL'))

def getLoggerHandle():
    logger = logging.getLogger(__name__)

    # ch = logging.FileHandler(r'log.txt')
    # ch.setLevel(logging.DEBUG)
    # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # # add formatter to ch
    # ch.setFormatter(formatter)
    # # add ch to logger
    # logger.addHandler(ch)
    return logger