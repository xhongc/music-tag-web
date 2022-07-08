FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN sed -i "s@http://deb.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list && rm -Rf /var/lib/apt/lists/* && apt-get update
RUN apt-get install -y gettext python3-dev libpq-dev
RUN mkdir /django-vue-cli
WORKDIR /django-vue-cli
ADD ./requirements.txt /django-vue-cli/

RUN pip install -r /django-vue-cli/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

EXPOSE 80 8000