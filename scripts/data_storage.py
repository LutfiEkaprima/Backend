import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """
    Create a database connection to the NutriDish database using MySQL.
    """
    try:
        conn = mysql.connector.connect(
            host='Name Server',
            database='Database Name',
            user='Database User',
            password='Database Password'
        )
        if conn.is_connected():
            print("Connected to MySQL database")
            return conn
    except Error as e:
        print(f"Error: {e}")
        return None
