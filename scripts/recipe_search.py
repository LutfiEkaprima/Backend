from scripts.data_storage import get_db_connection
from fuzzywuzzy import fuzz
import os

def get_matching_image(title, image_directory, threshold=65):
    """
    Find matching image for recipe title using fuzzy string matching.
    
    :param title: Recipe title
    :param image_directory: Directory containing recipe images
    :param threshold: Minimum similarity score (default 65 for 65% match)
    :return: Image filename if match found, None otherwise
    """
    # Get list of image files from directory
    image_files = [f for f in os.listdir(image_directory) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    # Remove file extensions for matching
    title_clean = title.lower()
    best_match = None
    best_score = 0
    
    for image_file in image_files:
        # Remove extension for comparison
        image_name = os.path.splitext(image_file)[0].lower()
        # Calculate similarity score
        score = fuzz.ratio(title_clean, image_name)
        
        if score > best_score and score >= threshold:
            best_score = score
            best_match = image_file
    
    if best_match:
        # Use forward slash and manually join paths
        return f"/{image_directory}/{best_match}".replace('\\', '/')
    return None

def search_recipes(user_input, image_directory="image"):
    """
    Search for recipes based on a query and user-defined filters.
    :param user_input: Dictionary containing the search query and filter criteria.
    :param image_directory: Directory containing recipe images
    :return: A list of recipes matching the search query and filters.
    """
    query = user_input.get("query", "").lower()
    filters = user_input.get("filters", {})

    filter_column_mapping = {
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
    }

    conn = get_db_connection()
    cursor = conn.cursor()

    query_conditions = []
    params = []

    if query:
        query_conditions.append("(title LIKE ? OR ingredients LIKE ?)")
        params.extend([f"%{query}%", f"%{query}%"])

    for tag, value in filters.items():
        if value:
            column_name = filter_column_mapping.get(tag, tag)
            query_conditions.append(f"{column_name} = 1")

    where_clause = " AND ".join(query_conditions) if query_conditions else "1 = 1"
    sql_query = f"SELECT * FROM recipes WHERE {where_clause}"

    cursor.execute(sql_query, params)
    recipes = cursor.fetchall()
    conn.close()

    formatted_recipes = []
    for recipe in recipes:
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

        dietary = dict(list(dietary.items())[:2])
        ingredients = dict(list(ingredients.items())[:3])
        
        # Find matching image for recipe
        image_path = get_matching_image(recipe["title"], image_directory)

        formatted_recipes.append({
            "title": recipe["title"],
            "image": image_path,  # Will be None if no matching image found
            "meal_type": {
                "breakfast": recipe["is_breakfast"],
                "lunch": recipe["is_lunch"],
                "dinner": recipe["is_dinner"],
                "snack": recipe["is_snack"],
                "dessert": recipe["is_dessert"]
            },
            "dietary": dietary,
            "ingredients": ingredients
        })

    return formatted_recipes

def search_recipes_by_query(query, image_directory="image"):
    """
    Search for recipes based on a query string.
    :param query: The search query string.
    :param image_directory: Directory containing recipe images
    :return: A list of recipes matching the search query.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM recipes
        WHERE title LIKE ? OR ingredients LIKE ?
    """, (f"%{query}%", f"%{query}%"))

    recipes = cursor.fetchall()
    conn.close()

    formatted_recipes = []
    for recipe in recipes:
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

        dietary = dict(list(dietary.items())[:2])
        ingredients = dict(list(ingredients.items())[:3])

        # Find matching image for recipe
        image_path = get_matching_image(recipe["title"], image_directory)

        formatted_recipes.append({
            "title": recipe["title"],
            "image": image_path,  # Will be None if no matching image found
            "meal_type": {
                "breakfast": recipe["is_breakfast"],
                "lunch": recipe["is_lunch"],
                "dinner": recipe["is_dinner"],
                "snack": recipe["is_snack"],
                "dessert": recipe["is_dessert"]
            },
            "dietary": dietary,
            "ingredients": ingredients
        })

    return formatted_recipes