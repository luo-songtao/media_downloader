FROM continuumio/miniconda3:4.7.12

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    apt-get update && apt-get clean

RUN apt-get install -y ffmpeg && apt-get clean
RUN conda install -y pycurl

COPY ./pip.conf /root/.pip/pip.conf
COPY ./requirements.txt /root/requirements.txt
RUN pip install -r /root/requirements.txt

COPY  ./src /root/sources
RUN cd /root/sources/main/python && python setup.py install

WORKDIR /code