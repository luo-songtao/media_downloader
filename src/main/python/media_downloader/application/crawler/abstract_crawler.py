import abc
import typing


class AbstractCrawler(metaclass=abc.ABCMeta):

    name = None

    crawler_params: typing.Dict = None
    downloader_params: typing.Dict = None

    def __init__(self, crawler_params):
        self.crawler_params = crawler_params
        if self.downloader_params is None:
            self.downloader_params = crawler_params.get("downloader_params")
        self.parse_crawler_params(crawler_params)

    def parse_crawler_params(self, crawler_params: typing.Dict):
        pass

    @abc.abstractmethod
    async def generate_initial_requests(self) -> typing.AsyncGenerator:
        raise NotImplementedError
