upstream flask-app {
  server flask-app:5000;
}

server {
  listen 80;

  location / {
    proxy_pass http://flask-app;
  }
}