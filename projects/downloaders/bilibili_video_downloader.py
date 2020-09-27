# -*- coding:utf-8 -*-
# @Author: Luo Songtao
# @Email: ryomawithlst@outlook.com
import re
import os
import json
import typing
from copy import deepcopy

from media_downloader.application.crawler import AbstractCrawler
from media_downloader.infrastructure.crawling_lib import Request, FileRequest
from media_downloader.infrastructure.log import log
from media_downloader import config


class BilibiliVideoDownloader(AbstractCrawler):

    name = "bilibili-video-downloader"

    list_headers = {
        "Referer": "https://www.bilibili.com/v/life/funny/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    }

    detail_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "www.bilibili.com",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    }

    media_headers = {
        "Access-Control-Request-Headers": "range",
        "Access-Control-Request-Method": "GET",
        "Origin": "https://www.bilibili.com",
        "Cookie": "CURRENT_FNVAL=16; _uuid=50490F0C-5C5B-4DFE-24C0-9F93FED12FF311298infoc; buvid3=58C341D7-8813-4C3A-8A05-7685255574FE190967infoc; stardustvideo=1; LIVE_BUVID=AUTO2115652848839489; fts=1565284901; rpdid=|(u)~lJYul|k0J'ulYlk)Rmku; im_notify_type_2337708=0; DedeUserID=2337708; DedeUserID__ckMd5=43a52e17dead6445; SESSDATA=dca4c74a%2C1574791722%2Cb104e9a1; bili_jct=005383ebddb2ec3eee6e4404e2a6e9a1; UM_distinctid=16e0e68a9d4507-0a541b0a7a8e31-38677b00-1fa400-16e0e68a9d511bd; CURRENT_QUALITY=80; sid=8so0imdo",
        "Referer": None,            # 比如："https://www.bilibili.com/video/av45560472/"
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    }

    video_type = None

    base_url = "https://s.search.bilibili.com/cate/search?main_ver=v3&search_type=video&view_type=hot_rank&order={order}&copy_right=-1&cate_id={cate_id}&page={page}&pagesize={page_size}&jsonp=jsonp&time_from={time_from}&time_to={time_to}&_={ts}"

    video_codecs = "avc1"

    av_base_url = "https://www.bilibili.com/video/av{}/"
    
    bv_base_url = "https://www.bilibili.com/video/BV{}/"

    def parse_crawler_params(self, crawler_params):
        # 缓存文件夹，用于临时存储媒体文件
        self.tmp_dir = "/tmp/bilibili"
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

        # 缓存OBJ，用于临时记录媒体文件下载记录
        self.new_version_records = {}
        self.old_version_records = {}

        self.base_storage_dir = os.path.join(config.ROOT_STORAGE_DIR, self.name)
        if not os.path.exists(self.base_storage_dir):
            os.mkdir(self.base_storage_dir)

        self.crawling_type = crawler_params.get("type")    # by_av|by_up_master
        self.av_number = crawler_params.get("av")
        self.bv_number = crawler_params.get("bv")
        self.up_master_id = crawler_params.get("up_master_id")

    async def generate_initial_requests(self) -> typing.AsyncGenerator:
        if self.crawling_type == "by_av":
            yield Request(
                url=self.av_base_url.format(self.av_number),
                headers=self.detail_headers,
                callback=self.detail_callback,
                metadata={"base_storage_dir": self.base_storage_dir, "av_number": self.av_number}
                # proxy_host=PROXY_HOST,
                # proxy_port=PROXY_PORT,
                # proxy_username=PROXY_USERNAME,
                # proxy_password=PROXY_PASSWORD,
            )
            
        if self.crawling_type == "by_bv":
            yield Request(
                url=self.bv_base_url.format(self.bv_number),
                headers=self.detail_headers,
                callback=self.detail_callback,
                metadata={"base_storage_dir": self.base_storage_dir, "av_number": self.av_number}
                # proxy_host=PROXY_HOST,
                # proxy_port=PROXY_PORT,
                # proxy_username=PROXY_USERNAME,
                # proxy_password=PROXY_PASSWORD,
            )            
            
    async def detail_callback(self, response):
        media_headers = deepcopy(self.media_headers)
        media_headers["Referer"] = response.request.url  # 设置media下载请求头的Referer地址

        metadata = response.request.metadata

        if "DIRECTLY_PARSING" in metadata:
            content = json.loads(response.body)
            log.info("详情页解析成功：[{}]".format(response.request.url))
            log.debug(metadata)
            async for request in self.content_parser(content, metadata, media_headers):
                yield request
        else:
            # _content = re.search(r"<script>window.__playinfo__=(.*?)</script>", response.body.decode())

            # if _content is None:
            _videoData = re.search(r"\"videoData\":(.*?),\"upData\"", response.body.decode())
            if _videoData is None:
                # 如果没有匹配到任何数据，记录日志，并直接退出
                log.warning("详情页解析失败: <{}>[{}]".format(response.code, response.request.url))
            else:
                videoData = json.loads(_videoData.group(1))
                videoData["title"] = re.sub("\W", "-", videoData["title"])
                storage_dir = os.path.join(metadata["base_storage_dir"], "{}-{}".format(videoData["title"], metadata["av_number"]))
                if not os.path.exists(storage_dir):
                    os.mkdir(storage_dir)
                metadata["storage_dir"] = storage_dir
                content_base_url = "https://api.bilibili.com/x/player/playurl?avid={aid}&cid={cid}&qn=0&type=&otype=json&fnver=0&fnval=16"
                pages = videoData["pages"]
                if len(pages) == 1:
                    url = content_base_url.format(aid=videoData["aid"], cid=videoData["cid"])
                    metadata["DIRECTLY_PARSING"] = "标示该请求是通过提取 videoData 中的 aid 和 cid 来发起单独的请求解析到 JSON Content 的"
                    metadata["video_name"] = videoData["title"]
                    metadata["id"] = "{}-{}".format(videoData["aid"], videoData["cid"])
                    yield Request(
                        url,
                        headers=media_headers,
                        callback=self.detail_callback,
                        metadata=metadata,
                        # proxy_host=PROXY_HOST,
                        # proxy_port=PROXY_PORT,
                        # proxy_username=PROXY_USERNAME,
                        # proxy_password=PROXY_PASSWORD,
                    )
                else:
                    downloaded_pages = [int(name.split("-")[0]) for name in os.listdir(storage_dir) if not name.startswith(".")]
                    for page in pages:
                        # if int(page["page"]) not in [57]:
                        #     continue
                        if int(page["page"]) in downloaded_pages:
                            continue
                        url = content_base_url.format(aid=videoData["aid"], cid=page["cid"])
                        metadata[
                            "DIRECTLY_PARSING"] = "标示该请求是通过提取 videoData 中的 aid 和 cid 来发起单独的请求解析到 JSON Content 的"
                        metadata["video_name"] = "{}-{}".format(page["page"], re.sub("\W", "-", page["part"]))
                        metadata["id"] = "{}-{}".format(videoData["aid"], page["cid"])
                        yield Request(
                            url,
                            headers=media_headers,
                            callback=self.detail_callback,
                            metadata=deepcopy(metadata),
                            # proxy_host=PROXY_HOST,
                            # proxy_port=PROXY_PORT,
                            # proxy_username=PROXY_USERNAME,
                            # proxy_password=PROXY_PASSWORD,
                        )
            # content = json.loads(_content.group(1))


    async def content_parser(self, content, metadata, media_headers):

        if "dash" not in content["data"]:
            '''------分割线------: 老版本'''
            requests = self.old_version_parser(metadata, content, media_headers)

        else:
            '''------分割线------: 新版本'''
            requests = self.new_version_parser(metadata, content, media_headers)
        for request in requests:
            yield request


    def old_version_parser(self, metadata, content, media_headers):
        metadata["video_info"] = content["data"]["durl"]
        self.old_version_records[metadata["id"]] = {"fragments": [], "image_path": None}
        for fragment in metadata["video_info"]:
            yield FileRequest(
                fragment["url"],
                callback=self.old_version_download_callback,
                file_path=os.path.join(self.tmp_dir, "{}-{}-video.flv".format(fragment["order"], metadata["id"])),
                headers=media_headers,
                metadata=metadata,
                # proxy_host=PROXY_HOST,
                # proxy_port=PROXY_PORT,
                # proxy_username=PROXY_USERNAME,
                # proxy_password=PROXY_PASSWORD,
            )

    def new_version_parser(self, metadata, content, media_headers):

        metadata["video_info"] = content["data"]["dash"]    # 提取视频的详细信息
        # metadata["video_quality"] = 64 if 64 in content["data"]["accept_quality"] else content["data"]["accept_quality"][-1]    # 视频质量默认最高选取代号64(720P)
        # metadata["video_quality"] = content["data"]["accept_quality"][0]    # 视频质量默认最高

        # 设置空记录
        self.new_version_records[metadata["id"]] = {"audio_path": None, "video_path": None, "image_path": None}

        '''下载视频'''
        for temp in metadata["video_info"]["video"]:
            if temp["codecs"].startswith(self.video_codecs):
                yield FileRequest(
                    temp["base_url"],
                    callback=self.new_version_download_callback,
                    file_path=os.path.join(self.tmp_dir, "{}-video.m4s".format(metadata["id"])),
                    headers=media_headers,
                    metadata=metadata,
                    # proxy_host=PROXY_HOST,
                    # proxy_port=PROXY_PORT,
                    # proxy_username=PROXY_USERNAME,
                    # proxy_password=PROXY_PASSWORD,
                )
                break
        else:
            log.warning("没有解析出符合条件的视频链接地址：av<{}>".format(metadata["id"]))

        '''下载音频'''
        temp2 = metadata["video_info"]["audio"][0]  # 音频的质量默认选择提供的最高清版本
        yield FileRequest(
            temp2["base_url"],
            callback=self.new_version_download_callback,
            file_path=os.path.join(self.tmp_dir, "{}-audio.m4s".format(metadata["id"])),
            headers=media_headers,
            metadata=metadata,
            # proxy_host=PROXY_HOST,
            # proxy_port=PROXY_PORT,
            # proxy_username=PROXY_USERNAME,
            # proxy_password=PROXY_PASSWORD,
        )

    async def old_version_download_callback(self, response):
        log.debug("Old version download callback")
        file_path = response.request.file_path
        metadata = response.request.metadata
        if file_path.endswith("video.flv"):
            order = file_path.split("/")[-1].split("-")[0]
            log.info("视频片段[{}]下载完毕: AV<{}>".format(order, metadata["id"]))
            self.old_version_records[metadata["id"]]["fragments"].append(file_path)

        if len(self.old_version_records[metadata["id"]]["fragments"]) == len(metadata["video_info"]):
            fragments_path = self.old_version_records[metadata["id"]]["fragments"]
            fragments_path = sorted(fragments_path, key=lambda x: int(x.split("/")[-1].split("-")[0]))

            ts_path_list = []
            for fragment_path in fragments_path:
                ts_path = fragment_path[:-3] + "ts"
                os.system("ffmpeg -i {flv_path} -y -loglevel warning -c copy -bsf:v h264_mp4toannexb -f mpegts {ts_path}".format(
                        flv_path=fragment_path,
                        ts_path=ts_path
                    )
                )
                ts_path_list.append(ts_path)
            output_path = os.path.join(metadata["storage_dir"], "{}.mp4".format(metadata["video_name"]))
            os.system('ffmpeg -i "concat:{concat_param}" -y -loglevel warning -c copy -bsf:a aac_adtstoasc -movflags +faststart {output_path}'.format(
                    concat_param="|".join(ts_path_list),
                    output_path=output_path
                )
            )
            for temp in ts_path_list+fragments_path:
                os.remove(temp)
            log.info("视频分片合并完毕: AV<{}>".format(metadata["id"]))

    async def new_version_download_callback(self, response):
        file_path = response.request.file_path
        metadata = response.request.metadata
        if file_path.endswith("video.m4s"):
            log.info("视频下载完毕: AV<{}>".format(metadata["id"]))
            self.new_version_records[metadata["id"]]["video_path"] = file_path
        elif file_path.endswith("audio.m4s"):
            log.info("音频下载完毕: AV<{}>".format(metadata["id"]))
            self.new_version_records[metadata["id"]]["audio_path"] = file_path

        if self.new_version_records[metadata["id"]]["video_path"] is not None \
        and self.new_version_records[metadata["id"]]["audio_path"] is not None:
            audio_path = self.new_version_records[metadata["id"]]["audio_path"]
            video_path = self.new_version_records[metadata["id"]]["video_path"]
            output_path = os.path.join(metadata["storage_dir"], "{}.mp4".format(metadata["video_name"]))
            os.system(
                "ffmpeg -i {audio_path} -i {video_path} -loglevel warning -y -acodec copy -vcodec copy {dst_path}".format(
                    audio_path=audio_path,
                    video_path=video_path,
                    dst_path=output_path,
                )
            )
            os.remove(audio_path)
            os.remove(video_path)
            log.info("音视频合并完毕: AV<{}>".format(metadata["id"]))
