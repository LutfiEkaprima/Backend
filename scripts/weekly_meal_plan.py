import random
from scripts.data_storage import get_db_connection

def get_recipes_not_in_cooldown(user_id, meal_type, selected_tags=None, cooldown_days=7):
    """
    Fetch recipes that are not in cooldown and match selected tags for a specific user and meal type.
    """
    conn = get_db_connection()
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
                INSERT INTO mealPlan (
                    userId, recipeTitle, mealType, dateUsed, image,
                    calories, protein, fat, sodium, 
                    is_breakfast, is_lunch, is_dinner, is_snack, is_dessert,
                    is_vegetarian, is_vegan, is_pescatarian, is_paleo, 
                    is_dairy_free, is_fat_free, is_peanut_free, is_soy_free, is_wheat_free,
                    is_low_carb, is_low_cal, is_low_fat, is_low_sodium, is_low_sugar, is_low_cholesterol,
                    is_winter, is_spring, is_summer, is_fall,
                    has_pork, has_alcohol, has_beef, has_bread, has_butter, 
                    has_cabbage, has_carrot, has_cheese, has_chicken, has_egg, has_eggplant, has_fish, 
                    has_onion, has_pasta, has_peanut, has_potato, has_rice, has_shrimp, has_tofu, 
                    has_tomato, has_zucchini, ingredients, directions, 
                    categories, rating, date, desc
                ) VALUES (
                    ?, ?, ?, DATE('now'), ?,
                    ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, 
                    ?, ?, ?, ?
                )
            """, (
                user_id, selected_recipe["title"], meal_type, selected_recipe["image"],
                selected_recipe["calories"],
                selected_recipe["protein"],
                selected_recipe["fat"],
                selected_recipe["sodium"],
                selected_recipe["is_breakfast"],
                selected_recipe["is_lunch"],
                selected_recipe["is_dinner"],
                selected_recipe["is_snack"],
                selected_recipe["is_dessert"],
                selected_recipe["is_vegetarian"],
                selected_recipe["is_vegan"],
                selected_recipe["is_pescatarian"],
                selected_recipe["is_paleo"],
                selected_recipe["is_dairy_free"],
                selected_recipe["is_fat_free"],
                selected_recipe["is_peanut_free"],
                selected_recipe["is_soy_free"],
                selected_recipe["is_wheat_free"],
                selected_recipe["is_low_carb"],
                selected_recipe["is_low_cal"],
                selected_recipe["is_low_fat"],
                selected_recipe["is_low_sodium"],
                selected_recipe["is_low_sugar"],
                selected_recipe["is_low_cholesterol"],
                selected_recipe["is_winter"],
                selected_recipe["is_spring"],
                selected_recipe["is_summer"],
                selected_recipe["is_fall"],
                selected_recipe["has_pork"],
                selected_recipe["has_alcohol"],
                selected_recipe["has_beef"],
                selected_recipe["has_bread"],
                selected_recipe["has_butter"],
                selected_recipe["has_cabbage"],
                selected_recipe["has_carrot"],
                selected_recipe["has_cheese"],
                selected_recipe["has_chicken"],
                selected_recipe["has_egg"],
                selected_recipe["has_eggplant"],
                selected_recipe["has_fish"],
                selected_recipe["has_onion"],
                selected_recipe["has_pasta"],
                selected_recipe["has_peanut"],
                selected_recipe["has_potato"],
                selected_recipe["has_rice"],
                selected_recipe["has_shrimp"],
                selected_recipe["has_tofu"],
                selected_recipe["has_tomato"],
                selected_recipe["has_zucchini"],
                selected_recipe["ingredients"],
                selected_recipe["directions"],
                selected_recipe["categories"],
                selected_recipe["rating"],
                selected_recipe["date"], 
                selected_recipe["desc"], 
            ))

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
                "ingredients": ingredients,
            }

        meal_plan[f"Day {day + 1}"] = daily_meals

    conn.commit()
    conn.close()
    return meal_plan
