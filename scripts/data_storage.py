import sqlite3
from pathlib import Path

def get_db_connection():
    """
    Create a database connection to the NutriDish database.
    """
    db_path = Path(__file__).resolve().parent.parent / "data" / "NutriDish.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn
