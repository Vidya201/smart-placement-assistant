"""MySQL connection helper. Settings come from environment variables / .env."""
import os
from contextlib import contextmanager

import mysql.connector
from dotenv import load_dotenv

load_dotenv()  # reads backend/.env if it exists


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "placement_assistant"),
    )


@contextmanager
def get_cursor():
    """Yields a dict cursor, commits on success, always closes the connection."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        yield cursor
        conn.commit()
    finally:
        cursor.close()
        conn.close()
