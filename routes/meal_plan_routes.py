import sqlite3
from pathlib import Path
from flask import Blueprint, request, jsonify
from scripts.data_storage import get_db_connection
from scripts.weekly_meal_plan import generate_meal_plan #update_meal_plan_with_cooldown

meal_plan_blueprint = Blueprint("meal_plan", __name__)

@meal_plan_blueprint.route("/", methods=["POST"])
def create_meal_plan():
    """
    Generate a weekly meal plan based on user preferences and tags.
    Request body should include: {"user_id": 1, "tags": {"vegetarian": true, "low carb": true}}
    """
    try:
        # Retrieve data from request body
        data = request.get_json()
        user_id = data["userId"]
        selected_tags = data.get("tags", {})

        # Generate the meal plan
        meal_plan = generate_meal_plan(user_id, selected_tags)

        # Save meal plan with cooldown information
        # update_meal_plan_with_cooldown(user_id, meal_plan)

        return jsonify({"message": "Meal plan generated successfully", "meal_plan": meal_plan}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@meal_plan_blueprint.route("/<string:user_id>/", methods=["GET"])
def get_user_meal_plan(user_id):
    """
    Retrieve the meal plan for the given user.
    """
    try:
        conn = get_db_connection()  # Use the centralized function
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM mealPlan WHERE userId = ?
        """, (user_id,))
        meal_plan = cursor.fetchall()

        conn.close()

        if not meal_plan:
            return jsonify({"error": "No meal plan found for this user"}), 404

        # Format meal plan data
        formatted_meal_plan = {}
        for meal in meal_plan:
            meal_type = meal["mealType"]  # Using column names
            if meal_type not in formatted_meal_plan:
                formatted_meal_plan[meal_type] = []
            formatted_meal_plan[meal_type].append({
                "title": meal["recipeTitle"],  # Using column names
                "date_used": meal["dateUsed"]  # Using column names
            })

        return jsonify({"user_id": user_id, "meal_plan": formatted_meal_plan}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
