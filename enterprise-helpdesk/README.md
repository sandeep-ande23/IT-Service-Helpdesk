# Enterprise Helpdesk & Ticket Management System

A beginner-friendly backend project built with **Python, FastAPI, MySQL and JWT authentication**.

The application models an internal company helpdesk where employees create support tickets, engineers work on assigned tickets, and administrators manage the system.

## Why this project?

This project is intentionally practical rather than over-engineered.

It demonstrates:

- Python backend development
- REST API design
- FastAPI
- MySQL and relational database design
- SQL joins and aggregations
- Authentication with JWT
- Password hashing with bcrypt
- Role-based authorization
- Resource-level authorization
- Request validation with Pydantic
- Business-rule validation
- Transactions
- Audit/history records
- API error handling

## Architecture

```text
Client / Swagger
       |
       v
   FastAPI API
       |
       +---- Authentication / Authorization
       |
       +---- Business Rules
       |
       v
     MySQL
```

## User roles

### Employee

- Register/login
- Create tickets
- View own tickets
- View comments/history for own tickets
- Add comments to own tickets

### Engineer

- Login
- View tickets assigned to them
- Update assigned tickets
- Change valid ticket statuses
- Add comments to assigned tickets

### Admin

- Login
- View all tickets
- Assign tickets to engineers
- Update tickets
- View all comments/history
- Access reports

## Ticket workflow

```text
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
```

The backend rejects invalid transitions.

For example:

```text
OPEN -> CLOSED
```

is rejected.

## Database design

### users

Stores employee, engineer and admin accounts.

Important fields:

- `id` - primary key
- `email` - unique login identifier
- `role` - EMPLOYEE, ENGINEER or ADMIN
- `password_hash` - bcrypt hash

### categories

Stores configurable ticket categories such as Network, Hardware and Software.

### tickets

Stores the current state of each support ticket.

Foreign keys:

- `created_by -> users.id`
- `assigned_to -> users.id`
- `category_id -> categories.id`

### comments

Stores conversation messages associated with tickets.

### ticket_history

Stores status changes for auditability.

Example:

```text
IN_PROGRESS -> RESOLVED
changed_by = engineer_id
```

## Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd enterprise-helpdesk
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the MySQL database

Open MySQL and run:

```sql
SOURCE database/schema.sql;
```

Or copy the contents of `database/schema.sql` into MySQL Workbench.

The script creates:

- `helpdesk_db`
- all required tables
- six starter categories

### 5. Configure environment variables

Copy:

```text
.env.example
```

to:

```text
.env
```

Then update:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=helpdesk_db

JWT_SECRET_KEY=replace_with_a_long_random_secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Never commit `.env`.

### 6. Create an admin account

Run:

```bash
python scripts/create_admin.py
```

The script asks for the admin name, email and password.

The password is hashed before it is stored.

### 7. Start the API

```bash
uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Main API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Register employee |
| POST | `/auth/login` | Login and receive JWT |
| POST | `/tickets/` | Create ticket |
| GET | `/tickets/` | Get tickets allowed for current user |
| GET | `/tickets/{ticket_id}` | Get one authorized ticket |
| PUT | `/tickets/{ticket_id}` | Engineer/admin ticket update |
| POST | `/tickets/{ticket_id}/comments` | Add comment |
| GET | `/tickets/{ticket_id}/comments` | View comments |
| GET | `/tickets/{ticket_id}/history` | View status history |
| GET | `/reports/tickets/status` | Admin status report |
| GET | `/reports/tickets/priority` | Admin priority report |
| GET | `/reports/tickets/category` | Admin category report |
| GET | `/reports/engineers/workload` | Admin engineer workload |

## Example API flow

### Register

```http
POST /auth/register
```

```json
{
  "name": "Sandeep",
  "email": "sandeep@example.com",
  "password": "password123"
}
```

### Login

```http
POST /auth/login
```

```json
{
  "email": "sandeep@example.com",
  "password": "password123"
}
```

Response:

```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

In Swagger, click **Authorize** and enter the token.

### Create a ticket

```http
POST /tickets/
```

```json
{
  "title": "VPN is not working",
  "description": "I cannot connect to the company VPN.",
  "priority": "HIGH",
  "category_id": 1
}
```

The server automatically takes the creator from the JWT.

The client does **not** provide `created_by`.

## Security design

### Authentication

JWT identifies the logged-in user.

The token contains:

```text
user_id
role
iat
exp
```

### Authorization

Authorization checks what the authenticated user can access.

Examples:

```text
EMPLOYEE -> own tickets
ENGINEER -> assigned tickets
ADMIN    -> all tickets
```

### Password security

Passwords are never stored as plaintext.

They are hashed using bcrypt.

### SQL injection protection

SQL parameters are passed separately:

```python
cursor.execute(
    "SELECT id FROM users WHERE email = %s",
    (email,)
)
```

Instead of constructing SQL with string concatenation.

## Error handling

The API uses meaningful HTTP status codes:

| Status | Meaning |
|---|---|
| 400 | Invalid business operation |
| 401 | Missing/invalid authentication |
| 403 | Authenticated but not authorized |
| 404 | Resource not found |
| 409 | Data conflict |
| 422 | Request validation failure |
| 500 | Unexpected server error |

## Transactions

Ticket status changes and their history record are written in the same transaction.

Conceptually:

```text
UPDATE tickets
       +
INSERT ticket_history
       |
       v
    COMMIT
```

If an unexpected error occurs:

```text
ROLLBACK
```

This prevents the ticket and its audit history from becoming inconsistent.

## SQL reporting

The project includes four small admin reports:

1. Tickets by status
2. Tickets by priority
3. Tickets by category
4. Engineer workload

Example:

```sql
SELECT
    status,
    COUNT(*) AS ticket_count
FROM tickets
GROUP BY status;
```

These demonstrate practical SQL aggregation without introducing a separate analytics platform.

## Project structure

```text
enterprise-helpdesk/
|
+-- app/
|   +-- main.py
|   +-- database.py
|   +-- models.py
|   +-- security.py
|   |
|   +-- routes/
|       +-- auth.py
|       +-- tickets.py
|       +-- comments.py
|       +-- reports.py
|
+-- database/
|   +-- schema.sql
|
+-- scripts/
|   +-- create_admin.py
|
+-- .env.example
+-- .gitignore
+-- requirements.txt
+-- README.md
```

## Interview explanation

A simple explanation:

> I built an internal enterprise helpdesk API using Python, FastAPI and MySQL. Employees can create support tickets, engineers can work on assigned tickets, and admins can manage tickets and access reports. I implemented JWT authentication and bcrypt password hashing, then added role-based and ticket-level authorization. I also designed the MySQL schema with foreign keys for users, tickets, categories, comments and ticket history. Ticket status transitions are validated in Python, and status changes are stored in an audit table within the same database transaction.

## What I intentionally did not use

The project does not use:

- Microservices
- Kubernetes
- Kafka
- Redis
- Celery
- PostgreSQL
- Complex cloud infrastructure
- AI-generated business logic
- An unnecessary frontend framework

The goal is to keep the project understandable and explainable while still demonstrating real backend engineering concepts.

## Future improvements

Possible future additions, if needed:

- Automated tests with pytest
- Docker deployment
- AWS deployment
- Pagination
- Email notifications
- A small frontend dashboard

These are optional and are not required for the core project.

## License

This project is intended as a portfolio and learning project.
