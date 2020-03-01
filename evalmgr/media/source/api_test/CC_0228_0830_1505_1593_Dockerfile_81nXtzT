FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN mkdir /ride_service

WORKDIR /ride_service

ADD . /ride_service/

RUN pip install -r requirements.txt
