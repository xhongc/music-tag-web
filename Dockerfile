FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get upgrade
RUN apt-get install -y gettext python3-dev libpq-dev
RUN mkdir /music-tag-web
WORKDIR /music-tag-web
ADD ./requirements.txt /music-tag-web/

RUN pip install -r /music-tag-web/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
CMD gunicorn django_vue_cli.wsgi

EXPOSE 80 8000