FROM python:3.8-alpine
MAINTAINER Marcelo Duarte Trevisani

RUN adduser -D painter

ENV PYTHONUNBUFFERED 1

RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers musl-dev zlib zlib-dev libffi-dev openssl-dev

RUN mkdir /painterbot
RUN chown -R painter:painter /painterbot
WORKDIR /painterbot
COPY . /painterbot

RUN python -m pip install -r requirements.txt
RUN python -m pip install -e .

RUN apk del .tmp-build-deps

USER painter
