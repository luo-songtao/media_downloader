# media_downloader

基于async+tornado(pycurl)实现的简易异步下载框架，结合ffmpeg等工具可批量下载视频

- 异步下载器框架代码，详见：src目录
    - 代码结构模仿DDD(领域驱动设计)模式，偶性强，可重构性高
    - 另外实现了简单的依赖注入功能，详见：src/main/python/media_downloader/infrastrcture/dependency_injection

# dependence

- python3.7+

- tools: ffmpeg
```
apt-get install -y ffmpeg
```

- python library:
```
tornado==6.0.2
ffmpeg-python==0.1.17
pycurl>=7.43.0.5
```

# Usage

- 哔哩哔哩视频下载，具体业务逻辑见：projects/downloader/bilibili_videl_downloader
    - 目前仅仅支持根据视频AV号、BV号下载，如果对应视频AV号、BV号下存在多个视频，将一齐下载
    - 基本目前对于B站新老接口都适用

- 配置
    - 在`conf.py`中，配置下载设置，如果有多个

- Docker 启动

    - 默认使用镜像：continuumio/miniconda3:4.7.12
    - `docker-compose build` 构建项目镜像
    - `docker-comppose up` 启动下载，将会下载到当前download文件夹下

# 更新记录

- v0.0.1: 基础功能已完善
