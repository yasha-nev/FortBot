FROM python:latest

LABEL authors="yasha-nev"

RUN pip install psycopg2 \
    pip install aiogram \
    pip install requests \
    pip install apscheduler

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY configs        /workdir/configs
COPY images         /workdir/images

ADD main.py         /workdir/
ADD config.py       /workdir/
ADD db.py           /workdir/
ADD vkparser.py     /workdir/

WORKDIR /workdir