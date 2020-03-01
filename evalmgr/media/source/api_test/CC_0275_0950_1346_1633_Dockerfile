
# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
#FROM python:3.6

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
#ENV PYTHONUNBUFFERED 1

# create root directory for our project in the container
#RUN mkdir /ridess

# Set the working directory to /music_service
#WORKDIR /ridess

# Copy the current directory contents into the container at /music_service
#ADD . /ridess/

# Install any needed packages specified in requirements.txt
#RUN pip install -r requirements.txt


#EXPOSE 8000

FROM python
ADD . /rideshare
WORKDIR /rideshare
ENV TEAM_NAME = CC_0275_0950_1346_1633
RUN pip install -r requirements.txt
EXPOSE 8000


