# Database Design

## Relationships

```text
users
  |
  +----< tickets.created_by
  |
  +----< tickets.assigned_to
  |
  +----< comments.user_id
  |
  +----< ticket_history.changed_by

categories
  |
  +----< tickets.category_id

tickets
  |
  +----< comments.ticket_id
  |
  +----< ticket_history.ticket_id
```

## Why two user foreign keys?

A ticket has two different relationships with users:

```text
created_by  -> employee who opened the ticket
assigned_to -> engineer working on the ticket
```

Both reference `users.id`, but they represent different business relationships.

## Normalized design

Comments and history are separate tables because one ticket can have many comments and many history records.

This avoids storing repeating information inside the tickets table.
