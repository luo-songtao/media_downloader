from urllib.parse import *

from tornado.httpclient import HTTPRequest, HTTPResponse

from media_downloader.infrastructure.log import log

class Response(HTTPResponse):

    def __init__(self, *args, **kwargs):
        pass

    def __new__(cls, response, request):
        response.request = request
        response.__class__ = cls
        return response


class FileResponse(HTTPResponse):

    def __init__(self, *args, **kwargs):
        pass

    def __new__(cls, response, request, file_size, file_path):
        response.request = request
        response.file_size = file_size
        response.file_path = file_path
        response.__class__ = cls
        return response


class Request(HTTPRequest):

    def __init__(self, url, callback, *args, handler=None, metadata=None, **kwargs):
        super(Request, self).__init__(url, *args, **kwargs)
        self.callback = callback
        self.handler=handler
        self.metadata = metadata
        self.parse_url()

    def parse_url(self):
        temp = urlparse(self.url)
        self.hostname = temp.hostname
        self.query = dict(parse_qsl(temp.query))
        self.path = temp.path
        self.scheme = temp.scheme

    def __repr__(self):
        return self.url

class FileRequest(Request):

    def __init__(self, url, callback, file_path, *args, **kwargs):
        super(FileRequest, self).__init__(url, callback, *args, **kwargs)
        self.file_path = file_path

    def set_client(self, client):
        self.client = client
