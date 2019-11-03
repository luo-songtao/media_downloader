import logging

from media_downloader import config


def get_or_create_logger(logger_name="logger"):
    """
    get or create A global logger
    :param logger_name:
    :return:
    """

    logger = logging.getLogger(logger_name)

    if logger.hasHandlers() is False:
        logger.setLevel(config.LOG_LEVEL)
        handler = logging.StreamHandler()
        handler.setLevel(config.LOG_LEVEL)
        formatter = logging.Formatter(fmt=config.LOG_FORMAT, datefmt=config.LOG_DATE_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

log = get_or_create_logger(config.LOG_NAME)
