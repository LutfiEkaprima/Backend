from flask import Blueprint, jsonify, request
from datetime import datetime
import random
from scripts.data_storage import get_db_connection

daily_recommendations_blueprint = Blueprint("daily_recommendations", __name__)

def get_recommendations(meal_type, user_restrictions, num_recommendations=10):
    """
    Fetch recommendations for the given meal type and user restrictions.
    :param meal_type: The type of meal (breakfast, lunch, dinner, snack, dessert)
    :param user_restrictions: User's dietary restrictions
    :param num_recommendations: Number of recipes to recommend
    :return: List of recommended recipes
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Build the base query with all necessary fields
    base_query = """
        SELECT title, image, is_breakfast, is_lunch, is_dinner, is_snack, is_dessert, 
               is_vegetarian, is_vegan, is_pescatarian, is_paleo, is_dairy_free, 
               is_fat_free, is_peanut_free, is_soy_free, is_wheat_free, is_low_carb,
               is_low_cal, is_low_fat, is_low_sodium, is_low_sugar, is_low_cholesterol,
               calories, protein, fat, sodium, ingredients, directions, rating,
               categories, desc, date
        FROM recipes
        WHERE is_{} = 1
    """.format(meal_type)

    # Add restriction conditions
    conditions = []
    params = []

    # Handle dietary restrictions
    if user_restrictions:
        for restriction, value in user_restrictions.items():
            if value == 0:  # User doesn't allow this
                if restriction == "cons_pork":
                    conditions.append("(ingredients NOT LIKE ? OR ingredients IS NULL)")
                    params.append("%pork%")
                elif restriction == "cons_alcohol":
                    conditions.append("(ingredients NOT LIKE ? OR ingredients IS NULL)")
                    params.append("%alcohol%")
                # Add more restrictions as needed

    # Combine all conditions
    if conditions:
        base_query += " AND " + " AND ".join(conditions)

    # Add randomization and limit
    base_query += " ORDER BY RANDOM() LIMIT ?"
    params.append(num_recommendations)

    # Execute query
    cursor.execute(base_query, params)
    recipes = cursor.fetchall()
    conn.close()

    if not recipes:
        return []

    # Format the recipes
    formatted_recipes = []
    for recipe in recipes:
        # Get dietary tags
        dietary = {
            tag: recipe[f"is_{tag.replace(' ', '_')}"]
            for tag in [
                "vegetarian", "vegan", "pescatarian", "paleo", "dairy_free",
                "fat_free", "peanut_free", "soy_free", "wheat_free", "low_carb",
                "low_cal", "low_fat", "low_sodium", "low_sugar", "low_cholesterol"
            ]
            if recipe[f"is_{tag.replace(' ', '_')}"] == 1
        }

        # Format recipe data
        formatted_recipe = {
            "title": recipe["title"],
            "image": recipe["image"],
            "meal_type": meal_type,
            "dietary": dietary,
            "nutrition": {
                "calories": recipe["calories"],
                "protein": recipe["protein"],
                "fat": recipe["fat"],
                "sodium": recipe["sodium"]
            },
            "rating": recipe["rating"],
            "ingredients": recipe["ingredients"],
            "directions": recipe["directions"],
            "categories": recipe["categories"],
            "description": recipe["desc"],
            "date_added": recipe["date"]
        }
        formatted_recipes.append(formatted_recipe)

    return formatted_recipes

@daily_recommendations_blueprint.route("/", methods=["POST"])
def recommend():
    """
    Get recipe recommendations based on current time and user preferences.
    """
    try:
        # Get user data from request
        user_data = request.get_json()
        if not user_data or "userId" not in user_data or "current_time" not in user_data:
            return jsonify({"error": "Missing userId or current_time in request body"}), 400

        user_id = user_data["userId"]
        current_time = user_data["current_time"]

        # Validate current_time format (e.g., HH:MM)
        try:
            current_hour, current_minute = map(int, current_time.split(":"))
            if not (0 <= current_hour < 24 and 0 <= current_minute < 60):
                raise ValueError
        except ValueError:
            return jsonify({"error": "Invalid current_time format. Expected HH:MM"}), 400

        # Fetch user restrictions from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cons_pork, cons_alcohol
            FROM users 
            WHERE userId = ?
        """, (user_id,))
        user_restrictions = cursor.fetchone()
        conn.close()

        if not user_restrictions:
            return jsonify({"error": "User not found"}), 404

        # Convert to dictionary
        user_restrictions = dict(user_restrictions)

        # Determine meal type based on user-provided current_time
        if 5 <= current_hour < 11:
            meal_type = "breakfast"
        elif 11 <= current_hour < 16:
            meal_type = "lunch"
        elif 16 <= current_hour < 22:
            meal_type = "dinner"
        else:
            meal_type = random.choice(["snack", "dessert"])

        # Get recommendations
        recommendations = get_recommendations(
            meal_type=meal_type,
            user_restrictions=user_restrictions,
            num_recommendations=10
        )

        if not recommendations:
            return jsonify({
                "message": f"No {meal_type} recipes found matching your preferences"
            }), 404

        response_data = {
            "meal_type": meal_type,
            "provided_time": current_time,
            "recommendations": recommendations
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500