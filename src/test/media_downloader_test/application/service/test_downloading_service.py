import asyncio
import unittest

from media_downloader.application.crawler import AbstractCrawler
from media_downloader.application.manager import CrawlerManager
from media_downloader.application.service import DownloadingService
from media_downloader.infrastructure.crawling_lib import Request, FileRequest
from media_downloader.infrastructure.async_manager import AsyncManager


real_http_code = None
file_path = "/a.zip"


class FakeCrawler(AbstractCrawler):

    name = "Fake Crawler"

    async def generate_initial_requests(self):
        normal_url = "https://cn.bing.com/"
        file_url = "https://github.com/luo-songtao/media_downloader/releases/download/0.0.1/a.zip"
        yield Request(url=normal_url, callback=self.normal_callback)
        yield FileRequest(url=file_url, callback=self.file_callback, file_path=file_path)

    async def normal_callback(self, response):
        global real_http_code
        real_http_code = response.code

    async def file_callback(self, response):
        pass
CrawlerManager.register(FakeCrawler)


class TestDownloadingService(unittest.TestCase):

    def setUp(self) -> None:
        self.downloading_service = DownloadingService()

    def tearDown(self) -> None:
        pass

    @AsyncManager.async_starter
    async def async_test(self, futures):
        await asyncio.gather(*futures)

    async def _test_downloading(self):
        ''''''
        """ Given """
        crawler_name = FakeCrawler.name
        crawler_params = {"downloader_params":
                              {
                                  "request_queue_max_size": 10,
                                  "delay": 1,
                                  "concurrent_number": 3
                              }
                          }
        await self.downloading_service.append_new_crawling_mission(crawler_name, crawler_params)

        """ When """
        await self.downloading_service.start(forever=False)

        """ Expect """
        self.assertEqual(
            self.downloading_service.downloader_manager.downloaders[crawler_name].pushed_request_count, 2, "Append Request Error"
        )
        self.assertEqual(real_http_code, 200, "Normal Request Failed")
        import os
        self.assertIsNotNone(os.path.exists(file_path), "Download fail: file doesn't exist")
        if os.path.exists(file_path):
            self.assertEqual(os.path.getsize(file_path), 180, "Download fail: file size not correct")
            os.remove(file_path)

    def test_all_method(self):
        t1 = self._test_downloading()
        futures = [t1]
        self.async_test(futures)

