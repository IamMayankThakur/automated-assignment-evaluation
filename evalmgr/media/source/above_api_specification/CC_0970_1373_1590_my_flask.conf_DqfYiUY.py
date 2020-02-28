Listen 80
<VirtualHost *:80>

        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html

        LogLevel debug

        WSGIScriptAlias / /home/ubuntu/flaskapp/my_flask.wsgi
        WSGIDaemonProcess flask-api processes=5 threads=1 user=ubuntu group=ubuntu display-name=%{GROUP}
        WSGIProcessGroup flask-api
        WSGIApplicationGroup %{GLOBAL}
        WSGIPassAuthorization On
        WSGIChunkedRequest On
        ErrorLog ${APACHE_LOG_DIR}/error-5000.log
        CustomLog ${APACHE_LOG_DIR}/access-5000.log combined

        <Directory /home/ubuntu/flaskapp>
            <IfVersion >= 2.4>
                Require all granted
            </IfVersion>
            <IfVersion < 2.4>
                Order allow,deny
                Allow from all
            </IfVersion>
        </Directory>

</VirtualHost>
