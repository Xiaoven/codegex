from loguru import logger
import os

LOG_PATH = 'log'
os.makedirs(LOG_PATH, exist_ok=True)
logger.add(LOG_PATH + '/{time}.log')


def is_comment(content: str):
    strip_content = content.strip()
    if strip_content.startswith('//') or strip_content.startswith('/*') or \
            strip_content.startswith('*'):
        return True
    return False
