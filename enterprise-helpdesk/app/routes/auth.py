from fastapi import APIRouter, HTTPException

from app.database import get_connection
from app.models import UserLogin, UserRegister
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=201)
def register_user(user: UserRegister):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (user.email,),
        )

        if cursor.fetchone() is not None:
            raise HTTPException(
                status_code=409,
                detail="Email already registered",
            )

        password_hash = hash_password(user.password)

        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
            """,
            (user.name, user.email, password_hash, "EMPLOYEE"),
        )

        connection.commit()

        return {
            "user_id": cursor.lastrowid,
            "message": "User registered successfully",
        }

    except HTTPException:
        raise
    except Exception:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to register user",
        )
    finally:
        cursor.close()
        connection.close()


@router.post("/login")
def login_user(user: UserLogin):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, email, password_hash, role
            FROM users
            WHERE email = %s
            """,
            (user.email,),
        )

        existing_user = cursor.fetchone()

        if existing_user is None or not verify_password(
            user.password,
            existing_user["password_hash"],
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        access_token = create_access_token(
            existing_user["id"],
            existing_user["role"],
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Login failed",
        )
    finally:
        cursor.close()
        connection.close()
