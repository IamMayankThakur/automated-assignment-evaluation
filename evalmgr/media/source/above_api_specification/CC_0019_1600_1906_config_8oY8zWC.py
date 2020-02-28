#upstream backend  {
 # server 127.0.0.1:5000;
#  server 127.0.0.1:8001;
#}

server {
    listen 80;
    server_name ec2-34-236-193-159.compute-1.amazonaws.com;
    location / {
        include proxy_params;
#	proxy_pass http://backend;
        proxy_pass http://unix:/home/ubuntu/myproject/myproject.sock;
#	proxy_pass ec2-34-236-193-159.compute-1.amazonaws.com:8000;
#	proxy_set_header Host $http_host;
    }
}
