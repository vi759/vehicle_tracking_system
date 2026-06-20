import mysql.connector
from config import Config


def get_database_connection():
    """
    Returns a MySQL connection or raises RuntimeError on failure.
    FIX: Previously returned None on error — callers would crash with
    AttributeError when calling .cursor() on None. Now raises so callers
    can handle it explicitly with try/except.
    """
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return connection
    except mysql.connector.Error as err:
        print("Database error:", err)
        raise RuntimeError(f"Database connection failed: {err}") from err
