FROM python:3.9-alpine
MAINTAINER Marcelo Duarte Trevisani

ENV PYTHONUNBUFFERED 1

RUN apk add --update --no-cache  git ca-certificates \
    gcc libc-dev linux-headers musl-dev zlib zlib-dev libffi-dev \
    openssl-dev openssl

RUN mkdir /painterbot
COPY . /painterbot
WORKDIR /painterbot

RUN git config --global user.name "painter-bot"
RUN git config --global user.email "contact@marcelotrevisani.info"
RUN git config --global credential.helper store

RUN python3 -m pip install -r requirements.txt

