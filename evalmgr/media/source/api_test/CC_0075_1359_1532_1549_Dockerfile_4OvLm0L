FROM python
ADD . /app
WORKDIR /app
ENV TEAM_NAME=CC_0075_1359_1532_1549
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python setup_db.py
CMD ["gunicorn","rides_app:app","-w 3","-b 0.0.0.0:8000"]