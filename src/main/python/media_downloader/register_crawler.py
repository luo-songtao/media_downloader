def register_crawler():
    from media_downloader.application.manager import CrawlerManager

    from media_downloader.application.crawler.crawlers import BilibiliVideoCrawler

    CrawlerManager.register(BilibiliVideoCrawler)