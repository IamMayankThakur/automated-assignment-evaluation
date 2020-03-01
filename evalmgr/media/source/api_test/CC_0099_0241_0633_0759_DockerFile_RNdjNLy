FROM python:3
MAINTAINER Rishabh <rishabhkj98@gmail.com>

RUN apt-get update
RUN apt-get upgrade -y

RUN mkdir /app
WORKDIR /app

COPY . /app

ENV TEAM_NAME CC_0099_0241_0633_0759

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python3","./rides.py"]