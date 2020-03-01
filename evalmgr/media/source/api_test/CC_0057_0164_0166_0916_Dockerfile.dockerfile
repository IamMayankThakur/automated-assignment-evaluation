FROM python:3
WORKDIR /usr/src/app
COPY . ./
ENV TEAM_NAME CC_0057_0164_0166_0916
RUN pip install --no-cache-dir -r requirements.txt
CMD ["flask","run","--host","0.0.0.0","--port","80"]