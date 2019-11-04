import typing
import asyncio

from media_downloader.infrastructure.crawling_lib import Downloader
from media_downloader.infrastructure.dependency_injection import Metaclass
from media_downloader.infrastructure.log import log
from media_downloader import config


class DownloaderManager(metaclass=Metaclass):

    def __init__(self):
        self.downloaders = {}

    async def schedule(self, crawler, downloader):
        requests = crawler.generate_initial_requests()
        async for request in requests:
            await downloader.add_request(request)

    def get_or_create_downloader(self, crawler):
        if crawler.name in self.downloaders:
            downloader = self.downloaders[crawler.name]
        else:
            downloader = Downloader(
                request_queue_max_size=crawler.downloader_params.get("concurrent_number", config.REQUEST_QUEUE_MAX_SIZE),
                concurrent_number=crawler.downloader_params.get("concurrent_number", config.MAX_CONCURRENT_NUMBER),
                delay=crawler.downloader_params.get("delay", config.DEFAULT_DELAY)
            )
            self.downloaders[crawler.name] = downloader
        return downloader

    async def reschedule_downloaders(self):
        coroutine_loops = []
        for crawler_name, downloader in self.downloaders.items():

            if downloader.is_running is False and downloader.request_queue.qsize() > 0:
                for i in range(downloader.concurrent_number):
                    coroutine_loops.append(downloader.run("{} {}".format(crawler_name, i + 1)))
                downloader.is_running = True

        await asyncio.gather(*coroutine_loops)
