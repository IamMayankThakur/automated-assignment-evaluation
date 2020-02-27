FROM python:3.7
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code/automated-assignment-evaluation

COPY ./requirements.txt /code/automated-assignment-evaluation/requirements.txt
RUN pip install --upgrade pip
RUN cd /code/automated-assignment-evaluation && pip install -r requirements.txt

COPY . /code/automated-assignment-evaluation

WORKDIR /code/automated-assignment-evaluation