from .infrastructure.dependency_injection import Mapper
from .infrastructure.log import log


class InversionOfController(object):

    @staticmethod
    def _register_all_manager():
        from media_downloader.application.manager import CrawlerManager
        from media_downloader.application.manager import DownloaderManager

        Mapper.register(CrawlerManager)
        log.debug("Inversion Of Controller Registered CrawlerManager")

        Mapper.register(DownloaderManager)
        log.debug("Inversion Of Controller Registered DownloaderManager")

    @staticmethod
    def _register_all_service():
        from media_downloader.application.manager import CrawlerManager
        from media_downloader.application.manager import DownloaderManager
        from media_downloader.application.service import DownloadingService

        Mapper.register(DownloadingService, CrawlerManager(), DownloaderManager())
        log.debug("Inversion Of Controller Registered DownloadingService")

    @classmethod
    def register_all(cls):
        cls._register_all_manager()
        cls._register_all_service()