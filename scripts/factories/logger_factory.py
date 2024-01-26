import logging
import sys
from os import path
from pathlib import Path


class LoggerFactory:
    @staticmethod
    def build_logger(log_location, name='run', log_level='INFO'):
        logger_name = name + '_logger'
        logger = logging.getLogger(logger_name)

        if (logger.hasHandlers()):
            logger.handlers.clear()
        
        logger.propagate = False
        
        if name == 'run':
            logger.addHandler(logging.StreamHandler(sys.stdout))
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s:%(lineno)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        else:
            logger_name = logger_name + '.csv'
            formatter = logging.Formatter('%(message)s,%(asctime)s', datefmt='%Y-%m-%d %H:%M:%S')

        log_dir = path.dirname(log_location)
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        hdlr = logging.FileHandler(log_location, 'a', 'utf-8')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)

        match log_level.upper():
            case 'DEBUG':
                logger.setLevel(logging.DEBUG)
            case 'INFO':
                logger.setLevel(logging.INFO)
            case 'WARNING':
                logger.setLevel(logging.WARNING)
            case 'ERROR':
                logger.setLevel(logging.ERROR)
            case 'CRITICAL':
                logger.setLevel(logging.CRITICAL)
            case _:
                print('Unknown log_level ' + log_level)
                exit()

        return logger
    
    @staticmethod    
    def shutdown_logger(logger):
        for handler in logger.handlers:
            logger.removeHandler(handler)
        for handler in logger.handlers:
            logger.removeHandler(handler)
        logging.shutdown()

