import os
import mysql.connector # type: ignore
from mysql.connector import Error # type: ignore
from dotenv import load_dotenv # type: ignore

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "harborwing_db"),
        autocommit=False  # Explicit transaction control
    )

def format_db_error(err: Error) -> str:
    """Translates MySQL error codes into human-readable messages."""
    if err.errno == 1451:
        return "Cannot delete or update this record because other records in the database reference it."
    if err.errno == 1452:
        return "Operation failed: Referenced parent record (foreign key) does not exist."
    if err.errno == 1062:
        return "Duplicate entry prevented: This record or relationship link already exists."
    return f"Database error ({err.errno}): {err.msg}"