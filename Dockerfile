FROM python:3.8-alpine
MAINTAINER Marcelo Duarte Trevisani

RUN adduser -D painter

ENV PYTHONUNBUFFERED 1

RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers musl-dev zlib zlib-dev libffi-dev openssl-dev

RUN mkdir /painter
RUN chown -R painter:painter /painter
WORKDIR /painter
COPY . /painter

RUN python -m pip install -e .

RUN apk del .tmp-build-deps

USER painter
