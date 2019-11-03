import typing
import asyncio

from tornado.queues import Queue, QueueEmpty
from tornado.httpclient import AsyncHTTPClient, HTTPClientError

from media_downloader.infrastructure.crawling_lib.httplib import Request, Response, FileRequest, FileResponse
from media_downloader.infrastructure.dependency_injection import Metaclass
from media_downloader.infrastructure.log import log
from media_downloader import config

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


class Downloader(metaclass=Metaclass):
    '''下载器逻辑'''

    __polling_interval = 0.0001    # 轮询暂停间隔，防止CPU进行空循环

    def __init__(self):
        self.http_client = AsyncHTTPClient()

        self.request_queue = Queue(config.MAX_REQUEST_QUEUE_SIZE)  # 请求队列
        self.max_concurrent_count = config.MAX_CONCURRENT_COUNT  # 请求最大并发数
        self.delay = config.PER_BATCH_REQUEST_DELAY_TIME  # 每批请求之间的延时
        self.is_running = False  # 记录采集器的运行状态
        self.pushed_request_count = 0  # 记录采集器队列中已经添加的请求数量
        self.failed_request_count = 0  # 记录失败的请求数量
        self.finished_request_count = 0  # 记录总共完成的请求数量

    async def add_request(self, request: Request):
        '''
        添加请求
        :param request: 请求对象
        :return:
        '''
        await self.request_queue.put(request)
        self.pushed_request_count += 1

    async def fetch(self, request: Request):
        '''根据指定的请求对象发起HTTP请求'''
        log.debug("Send request {}".format(request))
        try:
            response = await self.http_client.fetch(request)
        except HTTPClientError as e:
            return Response(e.response, request)
        else:
            return Response(response, request)

    async def download(self, request: FileRequest):
        log.debug("Downloading '{}'".format(request.file_path))
        actual_length = 0
        file = open(request.file_path, "wb")
        def write_data(data):
            nonlocal actual_length
            actual_length += len(data)
            file.write(data)
        tornado_request = Request(
            url=request.url,
            callback=None,
            headers=request.headers,
            streaming_callback=write_data,
            request_timeout=60*10,
            connect_timeout=60*10
        )
        tornado_response = await self.http_client.fetch(tornado_request)
        file.close()

        if actual_length == int(tornado_response.headers["Content-Length"]):
            log.debug("Success download '{}'".format(request.file_path))
        else:
            raise Exception("Error download '{}': content-length error".format(request.file_path))
        return FileResponse(tornado_response, request, file_size=actual_length, file_path=request.file_path)

    async def handle_request(self, request):
        log.debug("Handle request {}".format(request))
        try:
            if isinstance(request, FileRequest):
                response = await self.download(request)
            else:
                response = await self.fetch(request)
            # 注意：callback方法必须是一个awaitable对象
            response_processed_result = request.callback(response)

            if isinstance(response_processed_result, typing.AsyncGenerator):
                async for result in response_processed_result:
                    if isinstance(result, Request):
                        await self.add_request(result)
            else:
                result = await response_processed_result
                if isinstance(result, Request):
                    await self.add_request(result)
        except Exception as e:
            log.exception(e)
            log.error("Catch exception: {} {}".format(e, request))
            self.failed_request_count += 1
        else:
            log.debug("Fetched response from {}".format(request))
            self.finished_request_count += 1

    async def run(self, downloader_name=None):
        downloader_name = downloader_name if downloader_name else ""
        log.debug("Run downloader {}".format(downloader_name))
        while self.is_running:
            try:
                request = self.request_queue.get_nowait()
            except QueueEmpty:
                await asyncio.sleep(self.__polling_interval)
            else:
                await self.handle_request(request)
                if self.pushed_request_count == self.finished_request_count + self.failed_request_count:
                    self.is_running = False
            await asyncio.sleep(self.delay)
        log.debug("Quit downloader {}".format(downloader_name))
