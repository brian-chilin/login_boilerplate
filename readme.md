# login_boilerplate project
- simple hash verification systems that all share one database
- only reading is supported.
- index is special because it's static
- TODO fix all the xss attacks on the username input field (ex php)
- TODO automate some deployment or build stuff like a single script to build/push all docker containers
- TODO add to html template 'source code available here' mustache

# Pre-requisites
## Database
I used a simple Docker container
```
docker run -d \
  --name postgres_login_boilerplate \
  -e POSTGRES_USER={{CUSTOM_USERNAME}} \
  -e POSTGRES_PASSWORD={{CUSTOM_PASSWORD}} \
  -e POSTGRES_DB=database \
  -p {{EXPOSED_PORT}}:5432 \
  -v postgres_login_boilerplate:/var/lib/postgresql/data \
  --restart unless-stopped \
  postgres:16
```
To populate this database with some data to play with get `psql` program (probably available in the postgres:16 container, or online for your machine) and `sql` file from this project directory in the same spot.  
`psql -h {{IP}} -p {{EXPOSED_PORT}} -U {{CUSTOM_USERNAME}} -d database -f sql`

## Kubernetes
When doing kubernetes stuff run  
`kubectl create namespace login-boilerplate`

## Secrets, Config
Each of the source codes expects 
- `/etc/config/db/` to contain files (no extensions) with plaintext:
  - `host` {{IP}}
  - `port` {{EXPOSED_PORT}}
  - `name` database
  - `user` {{CUSTOM_USERNAME}}
  - `password` {{CUSTOM_PASSWORD}}
- `/etc/config/html/` to contain `html_template` (no extension) with the contents of https://github.com/brian-chilin/live-k8s/blob/main/pe410a/html_template  
### For devcontainers:
I spin up the devcontainer and with a shell inside manually make those files / variables.  
### For k8s I run  
- `kubectl create configmap html-conf -n login-boilerplate --from-file=html_template`
  - where `html_template` is https://github.com/brian-chilin/live-k8s/blob/main/pe410a/html_template
- `kubectl create secret generic database-conf -n login-boilerplate --from-env-file=secrets.env`
  - where `secrets.env` is a plaintext file with the 5 k:v pairs mentioned above, each `key=value` on 1 line  

Some containers also expect environment variables to be set.  
- See [django](##django)

# Overview of Source Code and Other Devcontainer Instructions

## index
- static html served in nginx for simplicity

## actix-web
**To Dev** `cargo run`

## aspnet
- `dotnet run`
- admittedly not dotnet-like
- fixed to port 8080; no https

## django
<!-- - requires environment variable `DJANGO_SECRET_KEY` to be set
  - In devcontainers `export DJANGO_SECRET_KEY="value"` works
  - TODO k8s? -->
- psycopg2

## express
- `npm start`

## fastapi
**To Dev** `uvicorn main:app --host 0.0.0.0 --port 80 --workers 2`
- psycopg2

## flask
**To Dev** `gunicorn -b 0.0.0.0:80 main:app`
- psycopg2

## php
**To Dev** `php -S 0.0.0.0:8080`

## rails

## springboot
