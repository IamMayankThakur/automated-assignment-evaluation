FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN mkdir /user_service

WORKDIR /user_service

ADD . /user_service/

RUN pip install -r requirements.txt
