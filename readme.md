# Getting Started with odoo-api

The Goal is to serve the website with a mordern Js framework as root url, and keep odoo
backoffice available.

This config give access to backoffice at odoo.localhost (you have to add it in your host file).
The api calls will be done with a prefix /odoo which will be rewritten by nginx

TODO: Find a cleaner way to use odoo not as root url 

## Nginx settings

```
    server {
        listen       80;
        server_name  odoo.localhost;

        proxy_read_timeout 720s;
        proxy_connect_timeout 720s;
        proxy_send_timeout 720s;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;

        #charset koi8-r;

        location / {
            proxy_redirect off;
            proxy_pass http://odoo;
        }
    }

    server {
        listen       80;
        server_name  localhost;

        proxy_read_timeout 720s;
        proxy_connect_timeout 720s;
        proxy_send_timeout 720s;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;

        #charset koi8-r;

        #access_log  logs/host.access.log  main;

        location /odoo {
            rewrite /odoo/(.*) /$1  break;
            proxy_redirect off;
            proxy_pass http://odoo;
        }
        location / {
            proxy_redirect off;
            proxy_pass http://react;
    }
```

