import time
from loguru import logger
import requests


requests.adapters.DEFAULT_RETRIES = 5
SESSION = requests.Session()
SESSION.keep_alive = False
BASE_SLEEP_TIME = 4
user_agent = 'Mozilla/5.0 ven(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/69.0.3497.100 Safari/537.36 '


def send(url, token='', max_retry=1, sleep_time=2):
    time.sleep(BASE_SLEEP_TIME)

    headers = {'User-Agent': user_agent}
    if token:
        headers['Authorization'] = f'token %{token}'

    try:
        res = SESSION.get(url, headers=headers, stream=False, timeout=10)
        return res
    except Exception as e:
        logger.error('[Request Error] url: {}    - msg: {}'.format(url, e))

        # only retry when exception happens
        if max_retry <= 0:
            return None
        cur_sleep_time = sleep_time + BASE_SLEEP_TIME
        time.sleep(cur_sleep_time)
        return send(url, token, max_retry - 1, sleep_time=cur_sleep_time)