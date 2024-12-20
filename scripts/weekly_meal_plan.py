import random
import sqlite3
from scripts.data_storage import get_db_connection

def get_recipes_not_in_cooldown(user_id, meal_type, selected_tags=None, cooldown_days=7):
    """
    Fetch recipes that are not in cooldown and match selected tags for a specific user and meal type.
    """
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row  # Ensure rows can be accessed as dictionaries
    cursor = conn.cursor()

    # Query to exclude recipes in cooldown
    cursor.execute("""
        SELECT * FROM recipes
        WHERE title NOT IN (
            SELECT recipeTitle
            FROM mealPlan
            WHERE userId = ? AND mealType = ? AND dateUsed > DATE('now', ?)
        )
        AND is_{} = 1
    """.format(meal_type), (user_id, meal_type, f"-{cooldown_days} days"))

    recipes = cursor.fetchall()
    conn.close()

    # Convert sqlite3.Row objects to dictionaries
    recipes = [dict(row) for row in recipes]

    # Filter recipes by selected tags if any
    if selected_tags:
        recipes = filter_recipes_by_tags(recipes, selected_tags)

    return recipes


def filter_recipes_by_tags(recipes, tags):
    """
    Filters recipes by the selected tags.
    :param recipes: The list of recipes (as dictionaries).
    :param tags: The selected tags for filtering.
    :return: A filtered list of recipes based on selected tags.
    """
    filtered_recipes = []
    for recipe in recipes:
        match = True
        for tag, value in tags.items():
            if recipe.get(tag) != value:
                match = False
                break
        if match:
            filtered_recipes.append(recipe)
    return filtered_recipes


def generate_meal_plan(user_id, selected_tags=None):
    """
    Generate a weekly meal plan for a user, respecting cooldowns and filtering by tags.
    """
    meal_types = ["breakfast", "lunch", "dinner", "snack", "dessert"]
    meal_plan = {f"Day {day + 1}": {} for day in range(7)}  # Initialize a 7-day plan

    conn = get_db_connection()
    cursor = conn.cursor()

    for day in range(7):
        daily_meals = {}
        for meal_type in meal_types:
            recipes = get_recipes_not_in_cooldown(user_id, meal_type, selected_tags)

            if not recipes:
                continue

            # Select a random recipe
            selected_recipe = random.choice(recipes)

            # Insert into mealPlan table
            cursor.execute("""
                INSERT INTO mealPlan (userId, recipeTitle, mealType, dateUsed)
                VALUES (?, ?, ?, DATE('now'))
            """, (user_id, selected_recipe["title"], meal_type))

            dietary = {key: selected_recipe[key] for key in [
                "is_vegetarian", "is_vegan", "is_pescatarian", "is_paleo", 
                "is_dairy_free", "is_fat_free", "is_peanut_free", "is_soy_free",
                "is_wheat_free", "is_low_carb", "is_low_cal", "is_low_fat",
                "is_low_sodium", "is_low_sugar", "is_low_cholesterol"
            ] if selected_recipe[key] == 1}

            ingredients = {ingredient: selected_recipe[f'has_{ingredient}'] for ingredient in [
                'pork', 'alcohol', 'beef', 'bread', 'butter', 'cabbage', 'carrot', 'cheese',
                'chicken', 'egg', 'eggplant', 'fish', 'onion', 'pasta', 'peanut', 'potato',
                'rice', 'shrimp', 'tofu', 'tomato', 'zucchini'
            ] if selected_recipe[f'has_{ingredient}'] == 1}

            dietary = dict(list(dietary.items())[:2])
            ingredients = dict(list(ingredients.items())[:3])

            daily_meals[meal_type] = {
                "title": selected_recipe["title"],
                "meal_type": meal_type,
                "dietary": dietary,
                "ingredients": ingredients
            }

        meal_plan[f"Day {day + 1}"] = daily_meals

    conn.commit()
    conn.close()
    return meal_plan
