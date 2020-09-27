# -*- coding:utf-8 -*-
# @Author: Luo Songtao
# @Email: ryomawithlst@outlook.com
from setuptools import setup, find_packages

setup(
    name="mdeia_downloader",
    version="0.0.1",
    decription = "async media downloader framework for http/https",
    author="luo-songtao",
    author_email="ryomawithlst@outlook.com",
    packages=find_packages(),
    install_requires=[
        "tornado==6.0.2",
        "ffmpeg-python==0.1.17"
    ]
)
