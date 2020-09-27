# -*- coding:utf-8 -*-
# @Author: Luo Songtao
# @Email: ryomawithlst@outlook.com
import sys

from media_downloader.application.manager import CrawlerManager
from media_downloader.server import run

from downloaders.bilibili_video_downloader import BilibiliVideoDownloader


CrawlerManager.register(BilibiliVideoDownloader)


if __name__ == '__main__':
    run()
