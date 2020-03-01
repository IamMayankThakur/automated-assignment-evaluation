FROM python
WORKDIR usr/src/app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
ENV TEAM_NAME=CC_0129_0837_1525
CMD ["python3", "ride.py"]