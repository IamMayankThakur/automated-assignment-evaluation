FROM tiangolo/uwsgi-nginx-flask:python3.7

COPY ./requirements.txt /tmp/

RUN pip install -U pip

RUN pip install -r /tmp/requirements.txt

COPY ./app /app

ENV TEAM_NAME "CC_1628_1731_1746"
