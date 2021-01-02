from loguru import logger
import os
import requests
import time

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


def logger_add(path: str, name: str):
    create_missing_dirs(path)
    return logger.add(os.path.join(path, name))


def log_message(message: str, level='info'):
    if level == 'info':
        logger.info(message)
    elif level == 'warning':
        logger.warning(message)
    elif level == 'error':
        logger.error(message)
    elif level == 'debug':
        logger.debug(message)



requests.adapters.DEFAULT_RETRIES = 5
SESSION = requests.Session()
SESSION.keep_alive = False
SLEEP_TIME = 4
user_agent = 'Mozilla/5.0 ven(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/69.0.3497.100 Safari/537.36 '


def send(url, token='', max_retry=1):
    time.sleep(SLEEP_TIME)

    headers = {'User-Agent': user_agent}
    if token:
        headers['Authorization'] = 'token ' + token

    try:
        res = SESSION.get(url, headers=headers, stream=False, timeout=10)
        return res
    except Exception as e:
        logger.error('[Request Error] url: {}    - msg: {}'.format(url, e))

        # only retry when exception happens
        if max_retry <= 0:
            return None
        time.sleep(SLEEP_TIME * 3)
        return send(url, token, max_retry - 1)