IT Service Request Management System

A backend REST API for managing IT service requests (tickets) with authentication, role-based access control, ticket assignment, status workflow, comments, and ticket history.

Overview

This project simulates a simple internal IT helpdesk system.

Employees can create and track their own service requests. Engineers can work on tickets assigned to them, while administrators have broader access to manage tickets and assignments.

The application is built with Python and FastAPI and uses MySQL for persistent data storage.

Features

User registration and login

JWT-based authentication

Bcrypt password hashing

Role-based access control

Employee, Engineer, and Admin roles

Create and view service tickets

Ticket assignment to engineers

Ticket priority and category

Controlled ticket status transitions

Ticket comments

Ticket status history / audit trail

MySQL relational database

Input validation with Pydantic

RESTful API endpoints

Swagger/OpenAPI API documentation

Docker and Docker Compose support

Technology Stack

Technology

Purpose

Python

Backend programming

FastAPI

REST API framework

MySQL

Relational database

Pydantic

Request/data validation

JWT

Authentication

Bcrypt

Password hashing

Uvicorn

ASGI server

Docker

Containerization

Docker Compose

Running API and MySQL together

Git/GitHub

Version control

System Architecture

Client / Swagger UI
        |
        v
     FastAPI
        |
  +-----+-----+
  |           |
Auth       Ticket Logic
  |           |
  +-----+-----+
        |
        v
      MySQL
        |
  +-----+----------------------+
  |        |        |          |
 users  categories tickets  comments
                         |
                    ticket_history

User Roles

Employee

Register and log in

Create service requests

View their own tickets

Add comments to accessible tickets

Engineer

View tickets assigned to them

Update assigned tickets

Change ticket status according to the allowed workflow

Assignments are controlled by the application

Admin

Access tickets across the system

Assign tickets to engineers

Update ticket information

View ticket history and perform administrative operations

Ticket Workflow

Tickets follow a controlled lifecycle:

OPEN
  |
  v
ASSIGNED
  |
  v
IN_PROGRESS
  |
  v
RESOLVED
  |
  v
CLOSED
  |
  v
REOPENED
  |
  v
IN_PROGRESS

The API validates status changes instead of allowing arbitrary transitions.

Authentication

Authentication uses JWT access tokens.

The basic flow is:

Register
   |
   v
Login
   |
   v
JWT Access Token
   |
   v
Authorization: Bearer <token>
   |
   v
Protected API Endpoints

Passwords are never stored as plain text. They are stored as bcrypt hashes.

The user's identity and role are obtained from the authenticated request rather than trusting role information supplied by the client.

Authorization

The API separates authentication from authorization.

401 Unauthorized — authentication is missing or invalid.

403 Forbidden — the user is authenticated but does not have permission for the requested operation.

Access is also checked at the ticket level.

For example:

An employee can access their own tickets.

An engineer can access tickets assigned to them.

An admin has broader ticket access.

Database Design

The system uses five main tables:

users
categories
tickets
comments
ticket_history

Main relationships

users
  |
  +----< tickets >---- categories
  |
  +----< comments
  |
  +----< ticket_history

A ticket stores information such as:

title

description

priority

status

category

creator

assigned engineer

creation time

update time

assigned_to can be empty when a newly created ticket has not yet been assigned.

comments and ticket_history are stored separately because a ticket can have multiple comments and multiple status changes.

API Endpoints

Authentication

POST /auth/register
POST /auth/login

Tickets

POST   /tickets/
GET    /tickets/
GET    /tickets/{ticket_id}
PUT    /tickets/{ticket_id}
GET    /tickets/{ticket_id}/history

Additional endpoints can be added as the application grows.

API Documentation

When running locally, FastAPI provides interactive Swagger documentation at:

http://localhost:8000/docs

The documentation can be used to:

View available endpoints

Understand request and response schemas

Authenticate using a JWT

Send test requests

Inspect API responses

Project Structure

it-service-request-management/
|
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── auth.py
│   │
│   └── routes/
│       ├── auth.py
│       └── tickets.py
│
├── database/
│   └── schema.sql
│
├── scripts/
│   └── ...
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── requirements.txt
└── README.md

Running Locally

1. Clone the repository

git clone <your-repository-url>
cd it-service-request-management

2. Create a virtual environment

python -m venv venv

Activate it on Windows:

venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

4. Configure environment variables

Create a .env file using .env.example as a template.

Example:

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=helpdesk_db

JWT_SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60

Do not commit the real .env file to GitHub.

5. Start the API

uvicorn app.main:app --reload

Open:

http://localhost:8000/docs

Running With Docker

The project also supports Docker Compose.

docker compose up --build

This starts:

FastAPI container
       |
       v
MySQL container

The API is available at:

http://localhost:8000

Swagger:

http://localhost:8000/docs

The Docker Compose setup uses:

API       -> port 8000
MySQL     -> host port 3307 / container port 3306

Inside Docker Compose, the API connects to MySQL using the service name:

DB_HOST=mysql
DB_PORT=3306

localhost should not be used for the MySQL host from inside the API container because localhost would refer to the API container itself.

Environment Variables

Variable

Purpose

DB_HOST

MySQL host

DB_PORT

MySQL port

DB_USER

MySQL username

DB_PASSWORD

MySQL password

DB_NAME

Database name

JWT_SECRET_KEY

Secret used to sign JWTs

ACCESS_TOKEN_EXPIRE_MINUTES

JWT expiration time

Keep secrets and passwords in environment variables rather than source code.

Error Handling

The API uses HTTP status codes to communicate request results.

Common responses include:

200 OK
201 Created
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
500 Internal Server Error

Examples:

Invalid login credentials → 401

Accessing another employee's ticket → 403

Ticket does not exist → 404

Invalid ticket status transition → 400

Data Integrity

Database operations use parameterized SQL queries to avoid directly inserting user input into SQL statements.

Transactions are used for database changes:

Operation
   |
   +---- success ----> COMMIT
   |
   +---- failure ----> ROLLBACK

This helps prevent partially completed database operations.

Testing the API

Swagger UI can be used for manual API testing.

A typical flow is:

1. Register user
2. Login
3. Copy JWT token
4. Authorize in Swagger
5. Create a ticket
6. View the ticket
7. Assign the ticket (Admin)
8. Update ticket status
9. View ticket history

Docker Architecture

The Docker setup contains two services:

docker-compose
      |
      +------------------+
      |                  |
      v                  v
    API                MySQL
 FastAPI             MySQL 8
    |                  |
    +------ network ---+

A named Docker volume is used for MySQL data so that database data can persist across container restarts.

Deployment

The application is containerized so it can be deployed to a cloud platform that supports Docker containers.

The deployment target can be changed without changing the core application architecture.

For a portfolio deployment, the goal is to provide a public API URL and Swagger documentation that recruiters can use to inspect the backend.

Security Considerations

The project includes several basic security practices:

Password hashing with bcrypt

JWT authentication

Role-based authorization

Ticket-level access checks

Parameterized SQL queries

Environment variables for secrets

Restricted role assignment during normal registration

Controlled ticket status transitions

Future Improvements

Possible improvements for a production-scale version include:

Automated tests with Pytest

Redis caching

API rate limiting

Background task processing

Centralized logging

Monitoring and metrics

Separate production database such as managed MySQL

CI/CD pipeline

Load balancing

Horizontal scaling

These are future improvements and are not required for the current implementation.

Learning Goals

This project was built to demonstrate practical understanding of:

REST API development

Python backend development

FastAPI

Authentication and authorization

JWT

Password security

Relational database design

MySQL

SQL queries and joins

Transactions

Role-based access control

Docker

API testing

Git/GitHub

Backend deployment concepts

Author

Sandeep Kumar Ande

Python | SQL | FastAPI | MySQL | Docker | AWS
