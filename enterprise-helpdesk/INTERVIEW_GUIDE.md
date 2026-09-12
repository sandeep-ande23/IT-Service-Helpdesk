# Interview Guide

## 1. Explain the project

> This is an internal enterprise helpdesk system. Employees create support tickets for issues such as VPN, hardware, software or access problems. Engineers work on tickets assigned to them, while admins manage tickets and view reports.

## 2. Why FastAPI?

> I used FastAPI because it provides a simple way to build REST APIs in Python, has automatic request validation through Pydantic, and automatically generates Swagger documentation.

## 3. Why MySQL?

> The application has strongly related data such as users, tickets, categories, comments and ticket history. MySQL is a relational database, so foreign keys and joins are useful for maintaining those relationships.

## 4. Explain authentication

> Authentication answers who the user is. The user logs in with email and password. The password is checked against a bcrypt hash, and the API returns a signed JWT containing the user's ID and role.

## 5. Explain authorization

> Authorization answers what the authenticated user is allowed to do. Employees can access their own tickets, engineers can access tickets assigned to them, and admins can access all tickets.

## 6. Why don't you accept created_by from the client?

> Because the client should not be trusted to identify itself. I take the user ID from the verified JWT, so a user cannot simply send another user's ID.

## 7. Why bcrypt?

> Passwords should not be stored as plaintext. bcrypt is designed for password hashing and includes a salt, so the database stores a password hash instead of the original password.

## 8. Why use an enum for status?

> Ticket status has a fixed set of valid values. Using an enum lets the request model reject invalid values before the business logic runs.

## 9. Why is category a table instead of an enum?

> Categories are business data that can change. An administrator could add a new category without changing application code.

## 10. Explain the status workflow

> I keep the allowed status transitions in a Python dictionary. Before updating a ticket, the API checks whether the requested next status is allowed from the current status.

## 11. Why ticket_history?

> The tickets table only stores the current status. The history table preserves previous transitions, who made the change and when it happened, which provides an audit trail.

## 12. Why a transaction?

> A status update and its history record should represent one logical operation. If one succeeds and the other fails, the data becomes inconsistent. Therefore both operations are committed together and rolled back on unexpected failure.

## 13. What is a foreign key?

> A foreign key connects a column in one table to a primary key in another table. For example, tickets.created_by references users.id.

## 14. Why LEFT JOIN for assigned engineer?

> A ticket can be unassigned, so assigned_to can be NULL. A LEFT JOIN still returns the ticket even when no engineer exists.

## 15. Difference between 401 and 403

> 401 means authentication failed or is missing. 403 means the server knows who the user is but the user does not have permission for that operation.

## 16. Difference between 404 and 409

> 404 means the requested resource doesn't exist. 409 means the request conflicts with existing data, such as registering an email that is already registered.

## 17. Why parameterized SQL?

> Parameterized queries keep user input separate from SQL syntax and help prevent SQL injection.

## 18. What would you improve next?

> I would add automated tests, containerize the application with Docker, add pagination for larger ticket lists, and deploy it to AWS. I would add these only when there is a real requirement rather than making the initial application unnecessarily complex.
