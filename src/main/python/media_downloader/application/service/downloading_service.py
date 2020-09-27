import time
import asyncio

from  asyncio.queues import Queue, QueueEmpty

from media_downloader.application.manager import DownloaderManager, CrawlerManager
from media_downloader.infrastructure.dependency_injection import Metaclass
from media_downloader.infrastructure.log import log


class DownloadingService(metaclass=Metaclass):

    def __init__(self, crawler_manager: CrawlerManager, downloader_manager: DownloaderManager):
        self.crawler_manager = crawler_manager
        self.downloader_manager = downloader_manager

        self.running_crawler = {}

        self.start_time = int(time.time())

        self.schedule_queue = Queue()

        self.QUIT = False

    def get_running_messages(self):
        msgs = []
        for crawler_name, downloader in self.downloader_manager.downloaders.items():
            status = "Running" if downloader.is_running else "Not Running"
            msg = "Status: {}" \
                  " | Crawler Name: {}, " \
                  " | Concurrent Number: {}," \
                  " | Request Number: {}," \
                  " | Finished Number: {}," \
                  " | Failed Number: {}".\
                format(status, crawler_name, downloader.concurrent_number, downloader.pushed_request_count,
                       downloader.finished_request_count, downloader.failed_request_count)
            msgs.append(msg)

        msgs.append("运行时长：{}s".format(time.time() - self.start_time))
        return "\n".join(msgs)

    async def status_print_loop(self):
        while True:
            running_time = int(time.time()) - self.start_time
            if running_time > 0 and running_time%60 == 0:
                log.info(self.get_running_messages())
            await asyncio.sleep(1)
            if self.QUIT is True:
                log.info(self.get_running_messages())
                break
        log.debug("Quit status print loop")

    async def append_new_crawling_mission(self, crawler_name, crawler_params):
        await self.schedule_queue.put((crawler_name, crawler_params))

    async def task_scheduling_loop(self):
        while True:
            try:
                crawler_name, crawler_params = self.schedule_queue.get_nowait()
            except QueueEmpty:
                await asyncio.sleep(1)
            else:
                crawler = self.crawler_manager.create_crawler(crawler_name, crawler_params)
                downloader = self.downloader_manager.get_or_create_downloader(crawler)
                await self.downloader_manager.schedule(crawler, downloader)
            finally:
                if self.QUIT and self.schedule_queue.qsize() == 0:
                    break
        log.debug("Quit task scheduling loop")

    async def start(self, forever=True):

        self.start_time = int(time.time())

        f1 = asyncio.ensure_future(self.task_scheduling_loop())
        f2 = asyncio.ensure_future(self.downloader_manager.reschedule_downloaders())
        f3 = asyncio.ensure_future(self.status_print_loop())

        if forever == False:
            def callback(_):
                log.debug("Downloading Mission Done!")
                self.QUIT = True
            f2.add_done_callback(callback)

        await asyncio.gather(f1, f2, f3)
