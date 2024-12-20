from flask import Blueprint, jsonify, request
from datetime import datetime
import random
from scripts.data_storage import get_db_connection

daily_recommendations_blueprint = Blueprint("daily_recommendations", __name__)

def get_recommendations(meal_type, user_restrictions, num_recommendations=10):
    """
    Fetch recommendations for the given meal type and user restrictions.
    :param meal_type: The type of meal (e.g., breakfast, lunch, etc.).
    :param user_restrictions: User's restrictions like cons_pork and cons_alcohol.
    :param num_recommendations: Number of recipes to recommend.
    :return: A list of recommended recipes.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query recipes matching the meal type and excluding restricted ingredients
    restrictions = []
    if user_restrictions.get("cons_pork") == 0:  # User doesn't allow pork
        restrictions.append("has_pork = 0")
    if user_restrictions.get("cons_alcohol") == 0:  # User doesn't allow alcohol
        restrictions.append("has_alcohol = 0")

    # Build the query
    where_clause = " AND ".join([f"is_{meal_type} = 1"] + restrictions)
    query = f"SELECT * FROM recipes WHERE {where_clause}"
    cursor.execute(query)
    recipes = cursor.fetchall()
    conn.close()

    if not recipes:
        return []

    # Convert sqlite3.Row objects to dictionaries
    recipes = [dict(recipe) for recipe in recipes]

    # Randomly select the required number of recipes
    return random.sample(recipes, min(len(recipes), num_recommendations))

@daily_recommendations_blueprint.route("/", methods=["POST"])
def recommend():
    """
    Recommend recipes based on the current time and user restrictions.
    """
    try:
        # Get user data from the request
        user_data = request.get_json()
        if not user_data or "userId" not in user_data:
            return jsonify({"error": "Missing userId in the request body"}), 400

        user_id = user_data["userId"]

        # Fetch user restrictions from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT cons_pork, cons_alcohol FROM users WHERE userId = ?", (user_id,))
        user_restrictions = cursor.fetchone()
        conn.close()

        if not user_restrictions:
            return jsonify({"error": "User not found"}), 404

        # Convert sqlite3.Row to dictionary
        user_restrictions = dict(user_restrictions)

        # Determine current time and meal type
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            meal_type = "breakfast"
        elif 12 <= current_hour < 17:
            meal_type = "lunch"
        elif 17 <= current_hour < 21:
            meal_type = "dinner"
        else:
            meal_type = random.choice(["snack", "dessert"])  # Nighttime can be either snack or dessert

        # Fetch recommendations
        recommendations = get_recommendations(meal_type, user_restrictions)

        if not recommendations:
            return jsonify({"message": f"No {meal_type} recipes found"}), 404

        # Format the response
        formatted_recommendations = []
        for recipe in recommendations:
            dietary = {key: recipe[val] for key, val in {
                "vegetarian": "is_vegetarian",
                "vegan": "is_vegan",
                "pescatarian": "is_pescatarian",
                "paleo": "is_paleo",
                "dairy free": "is_dairy_free",
                "fat free": "is_fat_free",
                "peanut free": "is_peanut_free",
                "soy free": "is_soy_free",
                "wheat free": "is_wheat_free",
                "low carb": "is_low_carb",
                "low cal": "is_low_cal",
                "low fat": "is_low_fat",
                "low sodium": "is_low_sodium",
                "low sugar": "is_low_sugar",
                "low cholesterol": "is_low_cholesterol"
            }.items() if recipe[val] == 1}

            ingredients = {ingredient: recipe[f'has_{ingredient}'] for ingredient in [
                'pork', 'alcohol', 'beef', 'bread', 'butter', 'cabbage', 'carrot', 'cheese',
                'chicken', 'egg', 'eggplant', 'fish', 'onion', 'pasta', 'peanut', 'potato',
                'rice', 'shrimp', 'tofu', 'tomato', 'zucchini'
            ] if recipe[f'has_{ingredient}'] == 1}

            # Limit dietary preferences to 2 and ingredients to 3
            dietary = dict(list(dietary.items())[:2])
            ingredients = dict(list(ingredients.items())[:3])

            formatted_recommendations.append({
                "title": recipe["title"],
                "meal_type": meal_type,
                "dietary": dietary,
                "ingredients": ingredients
            })

        return jsonify({"meal_type": meal_type, "recommendations": formatted_recommendations}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
