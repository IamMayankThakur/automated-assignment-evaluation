server {
    listen 80;
    listen [::]:80;
    server_name 52.45.244.156;

    
    location / {
        proxy_pass http://127.0.0.1:5000/;   
        proxy_redirect   off;
        proxy_set_header Host $http_host;   
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

