FROM python:3.7-alpine
COPY . /web
WORKDIR /web/api
EXPOSE 8000
ENV TEAM_NAME=CC_0160_1540_1868
RUN pip install -r ./requirements.txt
#RUN adduser -D myuser
#USER myuser
ENTRYPOINT ["python"]
CMD ["rides.py"]
