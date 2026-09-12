from fastapi import APIRouter, Depends, HTTPException

from app.database import get_connection
from app.models import TicketCreate, TicketUpdate
from app.security import get_current_user, require_role

router = APIRouter(prefix="/tickets", tags=["Tickets"])

ALLOWED_TRANSITIONS = {
    "OPEN": ["ASSIGNED"],
    "ASSIGNED": ["IN_PROGRESS"],
    "IN_PROGRESS": ["RESOLVED"],
    "RESOLVED": ["CLOSED"],
    "CLOSED": ["REOPENED"],
    "REOPENED": ["IN_PROGRESS"],
}


def _ticket_access_allowed(ticket: dict, current_user: dict) -> bool:
    role = current_user["role"]
    user_id = current_user["user_id"]

    if role == "ADMIN":
        return True

    if role == "EMPLOYEE":
        return ticket["created_by"] == user_id

    if role == "ENGINEER":
        return ticket["assigned_to"] == user_id

    return False


@router.post("/", status_code=201)
def create_ticket(
    ticket: TicketCreate,
    current_user: dict = Depends(get_current_user),
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id FROM categories WHERE id = %s",
            (ticket.category_id,),
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        cursor.execute(
            """
            INSERT INTO tickets
            (title, description, priority, status, created_by, category_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                ticket.title,
                ticket.description,
                ticket.priority.value,
                "OPEN",
                current_user["user_id"],
                ticket.category_id,
            ),
        )

        connection.commit()

        return {
            "ticket_id": cursor.lastrowid,
            "message": "Ticket created successfully",
        }

    except HTTPException:
        raise
    except Exception:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create ticket",
        )
    finally:
        cursor.close()
        connection.close()


@router.get("/")
def get_tickets(
    current_user: dict = Depends(get_current_user),
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        base_query = """
            SELECT
                t.id,
                t.title,
                t.description,
                t.priority,
                t.status,
                t.created_by,
                creator.name AS created_by_name,
                t.assigned_to,
                engineer.name AS assigned_engineer,
                c.name AS category,
                t.created_at,
                t.updated_at
            FROM tickets t
            JOIN users creator
                ON t.created_by = creator.id
            JOIN categories c
                ON t.category_id = c.id
            LEFT JOIN users engineer
                ON t.assigned_to = engineer.id
        """

        role = current_user["role"]
        user_id = current_user["user_id"]

        if role == "EMPLOYEE":
            cursor.execute(
                base_query + " WHERE t.created_by = %s ORDER BY t.created_at DESC",
                (user_id,),
            )
        elif role == "ENGINEER":
            cursor.execute(
                base_query + " WHERE t.assigned_to = %s ORDER BY t.created_at DESC",
                (user_id,),
            )
        elif role == "ADMIN":
            cursor.execute(base_query + " ORDER BY t.created_at DESC")
        else:
            raise HTTPException(
                status_code=403,
                detail="Invalid user role",
            )

        return cursor.fetchall()

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve tickets",
        )
    finally:
        cursor.close()
        connection.close()


@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: int,
    current_user: dict = Depends(get_current_user),
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                t.id,
                t.title,
                t.description,
                t.priority,
                t.status,
                t.created_by,
                creator.name AS created_by_name,
                t.assigned_to,
                engineer.name AS assigned_engineer,
                c.name AS category,
                t.created_at,
                t.updated_at
            FROM tickets t
            JOIN users creator
                ON t.created_by = creator.id
            JOIN categories c
                ON t.category_id = c.id
            LEFT JOIN users engineer
                ON t.assigned_to = engineer.id
            WHERE t.id = %s
            """,
            (ticket_id,),
        )

        ticket = cursor.fetchone()

        if ticket is None:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found",
            )

        if not _ticket_access_allowed(ticket, current_user):
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this ticket",
            )

        return ticket

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve ticket",
        )
    finally:
        cursor.close()
        connection.close()


@router.put("/{ticket_id}")
def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    current_user: dict = Depends(
        require_role("ENGINEER", "ADMIN")
    ),
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, status, assigned_to
            FROM tickets
            WHERE id = %s
            """,
            (ticket_id,),
        )

        existing_ticket = cursor.fetchone()

        if existing_ticket is None:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found",
            )

        role = current_user["role"]

        if (
            role == "ENGINEER"
            and ticket_update.assigned_to is not None
        ):
            raise HTTPException(
                status_code=403,
                detail="Only admins can assign tickets",
            )

        if (
            role == "ENGINEER"
            and existing_ticket["assigned_to"]
            != current_user["user_id"]
        ):
            raise HTTPException(
                status_code=403,
                detail="You can only update tickets assigned to you",
            )

        current_status = existing_ticket["status"]
        new_status = current_status

        if ticket_update.status is not None:
            new_status = ticket_update.status.value
            allowed_statuses = ALLOWED_TRANSITIONS.get(
                current_status,
                [],
            )

            if new_status not in allowed_statuses:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Cannot change status from "
                        f"{current_status} to {new_status}"
                    ),
                )

        assigned_to = existing_ticket["assigned_to"]

        if ticket_update.assigned_to is not None:
            cursor.execute(
                """
                SELECT id, role
                FROM users
                WHERE id = %s
                """,
                (ticket_update.assigned_to,),
            )

            assigned_user = cursor.fetchone()

            if assigned_user is None:
                raise HTTPException(
                    status_code=404,
                    detail="Assigned user not found",
                )

            if assigned_user["role"] != "ENGINEER":
                raise HTTPException(
                    status_code=400,
                    detail="Tickets can only be assigned to engineers",
                )

            assigned_to = ticket_update.assigned_to

        if new_status == "ASSIGNED" and assigned_to is None:
            raise HTTPException(
                status_code=400,
                detail="An engineer must be assigned before using ASSIGNED status",
            )

        cursor.execute(
            """
            UPDATE tickets
            SET status = %s,
                assigned_to = %s
            WHERE id = %s
            """,
            (new_status, assigned_to, ticket_id),
        )

        if ticket_update.status is not None:
            cursor.execute(
                """
                INSERT INTO ticket_history
                (ticket_id, changed_by, old_status, new_status)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    ticket_id,
                    current_user["user_id"],
                    current_status,
                    new_status,
                ),
            )

        connection.commit()

        return {
            "ticket_id": ticket_id,
            "message": "Ticket updated successfully",
        }

    except HTTPException:
        raise
    except Exception:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update ticket",
        )
    finally:
        cursor.close()
        connection.close()


@router.get("/{ticket_id}/history")
def get_ticket_history(
    ticket_id: int,
    current_user: dict = Depends(get_current_user),
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                id,
                created_by,
                assigned_to
            FROM tickets
            WHERE id = %s
            """,
            (ticket_id,),
        )

        ticket = cursor.fetchone()

        if ticket is None:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found",
            )

        if not _ticket_access_allowed(ticket, current_user):
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this ticket",
            )

        cursor.execute(
            """
            SELECT
                h.id,
                h.ticket_id,
                h.old_status,
                h.new_status,
                h.changed_at,
                u.id AS changed_by,
                u.name AS changed_by_name,
                u.role AS changed_by_role
            FROM ticket_history h
            JOIN users u
                ON h.changed_by = u.id
            WHERE h.ticket_id = %s
            ORDER BY h.changed_at ASC
            """,
            (ticket_id,),
        )

        return cursor.fetchall()

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve ticket history",
        )
    finally:
        cursor.close()
        connection.close()
