from loguru import logger
import os

LOG_PATH = 'log'
os.makedirs(LOG_PATH, exist_ok=True)
logger.add(LOG_PATH + '/{time}.log')
