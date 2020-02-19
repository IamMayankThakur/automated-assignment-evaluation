FROM python:3.7-alpine3.7
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /opt/services/djangoapp/src
WORKDIR /opt/services/djangoapp/src
ADD . /opt/services/djangoapp/src

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8001
