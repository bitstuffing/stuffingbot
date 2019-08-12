import logging
import time
logging.basicConfig(format='%(asctime)s - %(message)s', level = logging.DEBUG, filename = time.strftime("log_%Y-%m-%d.log"))

def info(text=''):
    logging.info(text)

def debug(text=''):
    logging.debug(text)

def error(text=''):
    logging.error(text)
