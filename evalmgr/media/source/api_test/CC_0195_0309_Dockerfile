FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y python3 && \
    apt-get install -y python3-pip && \
    pip3 install Flask-PyMongo==2.3.0 requests pandas

ENV TEAM_NAME=CC_0195_0309

WORKDIR /app

COPY . /app

EXPOSE 5050

CMD ["python3","a2rides.py"]
