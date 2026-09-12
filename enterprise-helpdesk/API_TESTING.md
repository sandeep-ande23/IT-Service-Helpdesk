# API Testing Checklist

Use Swagger at:

```text
http://127.0.0.1:8000/docs
```

## 1. Create employee

`POST /auth/register`

```json
{
  "name": "Employee One",
  "email": "employee1@example.com",
  "password": "password123"
}
```

Expected:

```text
201
```

## 2. Login employee

`POST /auth/login`

```json
{
  "email": "employee1@example.com",
  "password": "password123"
}
```

Copy the returned JWT and click **Authorize**.

## 3. Create ticket

`POST /tickets/`

```json
{
  "title": "VPN problem",
  "description": "The company VPN does not connect.",
  "priority": "HIGH",
  "category_id": 1
}
```

Expected:

```text
201
```

## 4. View tickets as employee

`GET /tickets/`

Expected:

- The employee sees their own tickets.
- They do not see another employee's tickets.

## 5. Create an engineer

Use `/auth/register`.

New users are created as EMPLOYEE by design.

For local development, change that user's role in MySQL:

```sql
UPDATE users
SET role = 'ENGINEER'
WHERE email = 'engineer@example.com';
```

Then log in again to receive a JWT containing the new role.

## 6. Create an admin

Run:

```bash
python scripts/create_admin.py
```

Then log in.

## 7. Assign a ticket

As admin:

`PUT /tickets/{ticket_id}`

```json
{
  "assigned_to": 2,
  "status": "ASSIGNED"
}
```

Use the actual engineer's user ID.

## 8. Update status as engineer

Login as the assigned engineer.

```json
{
  "status": "IN_PROGRESS"
}
```

Then:

```json
{
  "status": "RESOLVED"
}
```

Then admin can close it:

```json
{
  "status": "CLOSED"
}
```

## 9. Test invalid transition

Try:

```json
{
  "status": "CLOSED"
}
```

while the ticket is `OPEN`.

Expected:

```text
400
```

## 10. Test comments

As an authorized user:

`POST /tickets/{ticket_id}/comments`

```json
{
  "comment": "I have attached the requested information."
}
```

Then:

`GET /tickets/{ticket_id}/comments`

## 11. Test history

`GET /tickets/{ticket_id}/history`

You should see every status transition.

## 12. Test authorization

Try to access another employee's ticket using an employee JWT.

Expected:

```text
403
```

Try an admin report using an employee JWT.

Expected:

```text
403
```

Try a protected endpoint without a token.

Expected:

```text
401
```
