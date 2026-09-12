"""
Create an admin user without storing a plaintext password in the database.

Usage:
    python scripts/create_admin.py
"""

import getpass
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import get_connection
from app.security import hash_password

load_dotenv()

name = input("Admin name: ").strip()
email = input("Admin email: ").strip().lower()
password = getpass.getpass("Admin password: ")

if len(password) < 8:
    raise SystemExit("Password must contain at least 8 characters.")

connection = get_connection()
cursor = connection.cursor()

try:
    cursor.execute(
        "SELECT id FROM users WHERE email = %s",
        (email,),
    )

    if cursor.fetchone():
        raise SystemExit("A user with this email already exists.")

    cursor.execute(
        """
        INSERT INTO users (name, email, password_hash, role)
        VALUES (%s, %s, %s, 'ADMIN')
        """,
        (name, email, hash_password(password)),
    )

    connection.commit()
    print("Admin user created successfully.")

finally:
    cursor.close()
    connection.close()
