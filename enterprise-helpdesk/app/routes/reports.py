from fastapi import APIRouter, Depends

from app.database import get_connection
from app.security import require_role

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/tickets/status")
def ticket_status_report(
    current_user: dict = Depends(require_role("ADMIN")),
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                status,
                COUNT(*) AS ticket_count
            FROM tickets
            GROUP BY status
            ORDER BY status
            """
        )

        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


@router.get("/tickets/priority")
def ticket_priority_report(
    current_user: dict = Depends(require_role("ADMIN")),
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                priority,
                COUNT(*) AS ticket_count
            FROM tickets
            GROUP BY priority
            ORDER BY priority
            """
        )

        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


@router.get("/tickets/category")
def ticket_category_report(
    current_user: dict = Depends(require_role("ADMIN")),
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                c.name AS category,
                COUNT(t.id) AS ticket_count
            FROM categories c
            LEFT JOIN tickets t
                ON c.id = t.category_id
            GROUP BY c.id, c.name
            ORDER BY ticket_count DESC
            """
        )

        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


@router.get("/engineers/workload")
def engineer_workload_report(
    current_user: dict = Depends(require_role("ADMIN")),
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                u.id AS engineer_id,
                u.name AS engineer_name,
                COUNT(t.id) AS assigned_tickets
            FROM users u
            LEFT JOIN tickets t
                ON u.id = t.assigned_to
            WHERE u.role = 'ENGINEER'
            GROUP BY u.id, u.name
            ORDER BY assigned_tickets DESC
            """
        )

        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()
