import asyncio
import unittest

from media_downloader.infrastructure.crawling_lib import Downloader
from media_downloader.infrastructure.crawling_lib import Request, FileRequest
from media_downloader.infrastructure.async_manager import AsyncManager

class TestDownloader(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @AsyncManager.async_starter
    async def async_test(self, futures):
        await asyncio.gather(*futures)

    async def _test_normal_request(self):
        ''''''
        """ Given """
        downloader = Downloader()
        url = "https://cn.bing.com/"
        real_http_code = None
        async def callback(response):
            nonlocal real_http_code
            real_http_code = response.code

        request = Request(url=url, callback=callback)

        """ When """
        await downloader.add_request(request)
        downloader.is_running = True
        await downloader.run()

        """ Expect """
        self.assertEqual(real_http_code, 200, "Failed Request")

    async def _test_file_request(self):
        ''''''
        """ Given """
        downloader = Downloader()
        url = "https://github.com/luo-songtao/media_downloader/releases/download/0.0.1/a.zip"
        file_path = "/a.zip"

        async def callback(response):
            pass

        request = FileRequest(url=url, callback=callback, file_path=file_path)

        """ When """
        await downloader.add_request(request)
        downloader.is_running = True
        await downloader.run()

        """ Expect """
        import os
        self.assertIsNotNone(os.path.exists(file_path), "Download fail: file doesn't exist")
        if os.path.exists(file_path):
            self.assertEqual(os.path.getsize(file_path), 180, "Download fail: file size not correct")
            os.remove(file_path)

    def test_all_method(self):
        t1 = self._test_normal_request()
        t2 = self._test_file_request()
        futures = [t1, t2]
        self.async_test(futures)

