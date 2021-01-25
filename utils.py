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
BASE_SLEEP_TIME = 4
user_agent = 'Mozilla/5.0 ven(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/69.0.3497.100 Safari/537.36 '


def send(url, token='', max_retry=1, sleep_time=12):
    time.sleep(BASE_SLEEP_TIME)

    headers = {'User-Agent': user_agent}
    if token:
        headers['Authorization'] = 'token' + token

    try:
        res = SESSION.get(url, headers=headers, stream=False, timeout=10)
        return res
    except Exception as e:
        logger.error('[Request Error] url: {}    - msg: {}'.format(url, e))

        # only retry when exception happens
        if max_retry <= 0:
            return None
        time.sleep(sleep_time + BASE_SLEEP_TIME)
        return send(url, token, max_retry - 1)


def tohex(val, nbits):
    # https://stackoverflow.com/questions/7822956/how-to-convert-negative-integer-value-to-hex-in-python
    return hex((val + (1 << nbits)) % (1 << nbits))


def convert_str_to_int(num_str: str):
    num_str = num_str.strip()
    try:
        # Bitwise Complement (with all bits inversed): ~0b 1000 0000 0000 0000, i.e., 0b 0111 1111 1111 1111
        bitwise_complement = False
        if num_str.startswith('~'):
            bitwise_complement = True
            num_str = num_str.lstrip('~')
        # In fact, the type of constant depends on the variable.
        # For example, if the variable is long, then const will be convert to long even if it is int.
        # Since cannot get the variable type, there may be some false positives.
        is_long = False
        if num_str.endswith(('L', 'l')):
            num_str = num_str[:-1]
            is_long = True
        int_val = int(num_str, 0)
        if bitwise_complement:
            int_val = ~int_val

        # Notice 'negative' hex numbers in Java are positive in Python
        # Now, int_val can be a negative number in python, we need to map it back to hex number for Java
        if int_val < 0:
            hex_str = tohex(int_val, 64) if is_long else tohex(int_val, 32)
            int_val = int(hex_str, 0)

        return int_val
    except ValueError:
        return None
