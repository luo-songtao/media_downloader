from media_downloader.application.service import DownloadingService
from media_downloader.infrastructure.async_manager import AsyncManager

crawler_name = "bilibili-video-crawler"
crawler_params = {
    "type": "by_av",
    "av": "24325548",
    "downloader_params":
        {
            "request_queue_max_size": 1000,
            "delay": 2,
            "concurrent_number": 5
        }
}

@AsyncManager.async_starter
async def main():
    downloading_service = DownloadingService()
    await downloading_service.append_new_crawling_mission(crawler_name, crawler_params)
    await downloading_service.start(False)

if __name__ == '__main__':
    main()
