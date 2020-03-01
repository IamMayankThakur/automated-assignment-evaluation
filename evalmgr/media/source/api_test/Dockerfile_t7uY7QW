FROM python
EXPOSE 8000
WORKDIR /app
COPY . /app 
COPY main_rides.py /app 
RUN pip install -r requirements.txt
CMD python mr.py

