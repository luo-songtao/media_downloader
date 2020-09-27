# -*- coding:utf-8 -*-
# @Author: Luo Songtao
# @Email: ryomawithlst@outlook.com
import sys

sys.path.append("/code/main/python")
sys.path.append("/code/test/python")

from media_downloader_test.application.service.test_downloading_service import TestDownloadingService
from media_downloader_test.infrastructure.crawling_lib.test_downloader import TestDownloader

if __name__ == "__main__":
    import unittest
    unittest.main()