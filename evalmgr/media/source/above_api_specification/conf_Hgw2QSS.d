server {
    listen 80;
    server_name ec2-52-201-24-52.compute-1.amazonaws.com;

location / {
        proxy_pass http://127.0.0.1:5000;
   }
}

