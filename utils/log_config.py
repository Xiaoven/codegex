from loguru import logger
from pathlib import Path

_LOG_FILE_DIR = Path.cwd().parent / 'log'
_LOG_FILE_DIR.mkdir(exist_ok=True)

logger.add(str(_LOG_FILE_DIR) + '/error.log',
           level='ERROR', compression="zip", rotation="500MB", enqueue=True, retention='1 month')
logger.add(str(_LOG_FILE_DIR) + '/debug.log',
           filter=lambda record: record["level"].name == "DEBUG",
           compression="zip", rotation="500MB", enqueue=True, retention='1 month')
