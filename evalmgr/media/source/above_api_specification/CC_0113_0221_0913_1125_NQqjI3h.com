server {
        listen 80;
        server_name ec2-34-227-18-156.compute-1.amazonaws.com;

        location / {
                proxy_pass http://127.0.0.1:8000/;
        }
}