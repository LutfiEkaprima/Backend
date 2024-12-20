from scripts.data_storage import get_db_connection
import json
from datetime import datetime

def create_user(user_data):
    """
    Create or update a user in the users table.
    """
    try:
        user_id = user_data.get("userId")
        user_name = user_data.get("userName", "")
        email = user_data.get("email", "")
        password = user_data.get("password", "")
        date_birth = user_data.get("dateBirth", "")
        loc = user_data.get("loc", None)
        temp = user_data.get("temp", None)
        cons_pork = user_data.get("cons_pork", 0)
        cons_alcohol = user_data.get("cons_alcohol", 0)
        date_reg = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        age = calculate_age(date_birth) if date_birth else None

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE userId = ?", (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            # Update existing user
            cursor.execute("""
                UPDATE users 
                SET userName = ?, email = ?, password = ?, dateBirth = ?, age = ?, loc = ?, temp = ?, cons_pork = ?, cons_alcohol = ?
                WHERE userId = ?
            """, (user_name, email, password, date_birth, age, loc, temp, cons_pork, cons_alcohol, user_id))
        else:
            # Insert new user
            cursor.execute("""
                INSERT INTO users (userId, dateReg, userName, email, password, dateBirth, age, loc, temp, cons_pork, cons_alcohol)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, date_reg, user_name, email, password, date_birth, age, loc, temp, cons_pork, cons_alcohol))

        conn.commit()
        conn.close()
        return {"message": "User information updated successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
    
def calculate_age(dob):
    """
    Calculate age from date of birth.
    """
    if not dob:
        return None
    try:
        today = datetime.today()
        birth_date = datetime.strptime(dob, "%Y-%m-%d")
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except ValueError:
        return None  # Handle invalid date format


def get_user(user_id):
    """
    Retrieve user details by userId.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE userId = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return {"error": f"User with ID {user_id} not found"}, 404

        return dict(user), 200
    except Exception as e:
        return {"error": str(e)}, 500


