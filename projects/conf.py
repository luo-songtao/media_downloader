# -*- coding:utf-8 -*-
# @Author: Luo Songtao
# @Email: ryomawithlst@outlook.com

'''
该模块仅仅用于覆盖或配置项目的默认配置，不应包含任何业务代码
切记不要在该模块中引入media_downloader包及其子模块
'''

bilibili_downloader_params = {
    "type": "by_bv",
    "av": "",
    "bv": "1vt411N7Ti",
    "downloader_params":
        {
            "request_queue_max_size": 1000,
            "delay": 3,
            "concurrent_number": 8
        }
}

DOWNLOADERS = {
    "bilibili-video-downloader": bilibili_downloader_params
}


'''
default config
'''

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

