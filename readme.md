## Motivation

The goal is to interface odoo with any frontend through a JSON restapi without altering auth system.
With odoo routes as they are you have two choices:

- http: you will have to send your request as an application/x-www-form-urlencoded
but you will be able to send json as response thanks to json.dumps()
- json: you will have the ability to receive directly json and respond as json too,
but as the route is not http anymore, in case of error you won't be able to have basic
http error responses.

The simplest option was to add an other dispatcher to odoo, that we called "api"

## Features

- JSON request and JSON/HTTP error as response
- pydantic models possible for request and response bodies
- openapi documentation over the "api" route with pydantic models annotations
  
## Getting Started

## Contributors



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

