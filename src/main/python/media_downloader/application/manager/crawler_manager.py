from media_downloader.application.crawler import AbstractCrawler
from media_downloader.infrastructure.dependency_injection import Metaclass


class CrawlerManager(metaclass=Metaclass):

    __registered_crawler = {}

    def __init__(self):
        pass

    def create_crawler(self, crawler_name, crawler_params) -> AbstractCrawler:
        crawler = self.__registered_crawler[crawler_name](crawler_params)
        return crawler

    @classmethod
    def register(cls, crawler_cls):
        cls.__registered_crawler[crawler_cls.name] = crawler_cls

