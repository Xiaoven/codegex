from loguru import logger
import os

LOG_PATH = 'log'
os.makedirs(LOG_PATH, exist_ok=True)
TRACE = logger.add(LOG_PATH + '/{time}.log')


def is_comment(content: str):
    strip_content = content.strip()
    if strip_content.startswith('//') or strip_content.startswith('/*') or \
            strip_content.startswith('*'):
        return True
    return False


def create_missing_dirs(path: str):
    os.makedirs(path, exist_ok=True)


def logger_add(path: str, name:str):
    create_missing_dirs(path)
    return logger.add(path+name)
