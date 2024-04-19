import logging
import sys
from os import path
from pathlib import Path
import time;

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

      # match statement only works in >= Python 3.10
      # match log_level.upper():
      #     case 'DEBUG':
      #         logger.setLevel(logging.DEBUG)
      #     case 'INFO':
      #         logger.setLevel(logging.INFO)
      #     case 'WARNING':
      #         logger.setLevel(logging.WARNING)
      #     case 'ERROR':
      #         logger.setLevel(logging.ERROR)
      #     case 'CRITICAL':
      #         logger.setLevel(logging.CRITICAL)
      #     case _:
      #         logger.setLevel(logging.INFO)
      if log_level.upper() == 'DEBUG':
         logger.setLevel(logging.DEBUG)
      elif log_level.upper() == 'INFO':
         logger.setLevel(logging.INFO)
      elif log_level.upper() == 'WARNING':
         logger.setLevel(logging.WARNING)
      elif log_level.upper() == 'ERROR':
         logger.setLevel(logging.ERROR)
      elif log_level.upper() == 'CRITICAL':
         logger.setLevel(logging.CRITICAL)
      else:
         logger.setLevel(logging.INFO)

      return logger
    
   @staticmethod    
   def shutdown_logger(logger):
      for handler in logger.handlers:
         logger.removeHandler(handler)
      for handler in logger.handlers:
         logger.removeHandler(handler)
      logging.shutdown()
      
   def debug(self,msg,*args,**kwargs):
      # Add minor delay to force logging to order better under debug
      time.sleep(0.01);
      return super(LoggerFactory,self).debug(msg,*args,**kwargs);

