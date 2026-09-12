from fastapi import APIRouter, Depends, HTTPException

from app.database import get_connection
from app.models import CommentCreate
from app.security import get_current_user
from app.routes.tickets import _ticket_access_allowed

router = APIRouter(prefix="/tickets", tags=["Comments"])


@router.post("/{ticket_id}/comments", status_code=201)
def add_comment(
    ticket_id: int,
    comment_data: CommentCreate,
    current_user: dict = Depends(get_current_user),
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, created_by, assigned_to
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
            INSERT INTO comments
            (ticket_id, user_id, comment)
            VALUES (%s, %s, %s)
            """,
            (
                ticket_id,
                current_user["user_id"],
                comment_data.comment,
            ),
        )

        connection.commit()

        return {
            "comment_id": cursor.lastrowid,
            "message": "Comment added successfully",
        }

    except HTTPException:
        raise
    except Exception:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to add comment",
        )
    finally:
        cursor.close()
        connection.close()


@router.get("/{ticket_id}/comments")
def get_comments(
    ticket_id: int,
    current_user: dict = Depends(get_current_user),
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, created_by, assigned_to
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
                c.id,
                c.comment,
                c.created_at,
                u.id AS user_id,
                u.name AS user_name,
                u.role
            FROM comments c
            JOIN users u
                ON c.user_id = u.id
            WHERE c.ticket_id = %s
            ORDER BY c.created_at ASC
            """,
            (ticket_id,),
        )

        return cursor.fetchall()

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve comments",
        )
    finally:
        cursor.close()
        connection.close()
