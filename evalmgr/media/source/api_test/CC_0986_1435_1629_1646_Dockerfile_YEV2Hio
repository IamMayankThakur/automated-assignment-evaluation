FROM mongo:4.2.3-bionic

WORKDIR /app

ADD . /app

RUN apt-get update

RUN apt-get install python3 python3-pip -y

RUN pip3 install -r requirements.txt

EXPOSE 80

CMD [ "python3", "flaskapp.py" ]
