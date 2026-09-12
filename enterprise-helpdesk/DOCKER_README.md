# Docker Setup

## Start
docker compose up --build

Swagger:
http://localhost:8000/docs

## Stop
docker compose down

## Reset database completely
docker compose down -v

## Background mode
docker compose up --build -d

## API logs
docker compose logs -f api

## Important
When FastAPI runs inside Docker, use:
DB_HOST=mysql
DB_PORT=3306

Do not use localhost for the API-to-MySQL connection.

MySQL is exposed to the Windows host on port 3307.
