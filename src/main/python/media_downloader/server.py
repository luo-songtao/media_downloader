# -*- coding:utf-8 -*-
# @Author: Luo Songtao
# @Email: ryomawithlst@outlook.com
from media_downloader.application.service import DownloadingService
from media_downloader.infrastructure.async_manager import AsyncManager
from media_downloader.config import DOWNLOADERS


async def setup(downloading_service):
    for downloader_name, downloader_params in DOWNLOADERS.items():
        await downloading_service.append_new_crawling_mission(downloader_name, downloader_params)

async def start(downloading_service):
    await downloading_service.start(forever=False)

@AsyncManager.async_starter
async def run():
    server = DownloadingService()
    await setup(server)
    await start(server)

if __name__ == '__main__':
    run()
