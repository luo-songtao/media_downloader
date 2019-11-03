""" CONFIG """
import os

""" log config """
LOG_NAME = "LOG"
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "%(asctime)s [%(levelname)s]: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

""" crawling_lib running config """
MAX_REQUEST_QUEUE_SIZE = int(os.environ.get("MAX_REQUEST_QUEUE_SIZE", 1000))
MAX_CONCURRENT_COUNT = int(os.environ.get("MAX_CONCURRENT_COUNT", 10))
PER_BATCH_REQUEST_DELAY_TIME = int(os.environ.get("PER_BATCH_REQUEST_DELAY_TIME", 0))
