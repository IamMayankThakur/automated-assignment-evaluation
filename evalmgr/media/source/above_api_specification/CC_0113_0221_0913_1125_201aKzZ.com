server {
        listen 80;
        server_name ec2-3-95-169-94.compute-1.amazonaws.com;

        location / {
                proxy_pass http://127.0.0.1:8000/;
        }
}