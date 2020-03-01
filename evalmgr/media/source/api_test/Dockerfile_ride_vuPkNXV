FROM rides:latest

EXPOSE 8000:8000

ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD Iusepostgres@321
ENV POSTGRES_DB cloud_computing_assignment_ride

ENV TEAM_NAME CC_0227_1123_1139_1526

RUN git clone http://github.com/madhavmk/Cloud-Computing-Course

CMD python3 Cloud-Computing-Course/Assignment\ 2/Ride/waitress_server.py