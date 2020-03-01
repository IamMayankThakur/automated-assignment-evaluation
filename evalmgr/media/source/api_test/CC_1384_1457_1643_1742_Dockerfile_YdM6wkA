FROM python:3.7.2-stretch
EXPOSE 8080
COPY . /flaskapp/flask2
WORKDIR /flaskapp/flask2


RUN pip3 --no-cache-dir install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["ride.py"]
ENV TEAM_NAME = CC_1384_1457_1643_1742
