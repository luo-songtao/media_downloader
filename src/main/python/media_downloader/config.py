""" CONFIG """
import os

""" log config """
LOG_NAME = "LOG"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(levelname)s]: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

""" crawling_lib running config """
REQUEST_QUEUE_MAX_SIZE = int(os.environ.get("REQUEST_QUEUE_MAX_SIZE", 1000))
MAX_CONCURRENT_NUMBER = int(os.environ.get("MAX_CONCURRENT_NUMBER", 10))
DEFAULT_DELAY = int(os.environ.get("DEFAULT_DELAY", 0))

ROOT_STORAGE_DIR = "/download"
if not os.path.exists(ROOT_STORAGE_DIR):
    os.mkdir(ROOT_STORAGE_DIR)

DOWNLOADERS = dict()

try:
    from conf import *
except ModuleNotFoundError:
    pass
