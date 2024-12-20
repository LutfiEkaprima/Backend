from scripts.data_storage import get_db_connection

def search_recipes(user_input):
    """
    Search for recipes based on a query and user-defined filters.
    :param user_input: Dictionary containing the search query and filter criteria.
    :return: A list of recipes matching the search query and filters.
    """
    query = user_input.get("query", "").lower()  # Extract query from user input
    filters = user_input.get("filters", {})  # Extract filters

    # Mapping of user-friendly filter names to actual column names
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

    # Build the WHERE clause dynamically
    query_conditions = []
    params = []

    if query:
        query_conditions.append("(title LIKE ? OR ingredients LIKE ?)")
        params.extend([f"%{query}%", f"%{query}%"])  # Partial matching

    for tag, value in filters.items():
        if value:
            # Map user-friendly names to actual column names
            column_name = filter_column_mapping.get(tag, tag)
            query_conditions.append(f"{column_name} = 1")

    # Combine all conditions
    where_clause = " AND ".join(query_conditions) if query_conditions else "1 = 1"  # Default to no filter
    sql_query = f"SELECT * FROM recipes WHERE {where_clause}"

    cursor.execute(sql_query, params)
    recipes = cursor.fetchall()
    conn.close()

    # Format and return the results
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

        # Limit dietary preferences to 2 and ingredients to 3
        dietary = dict(list(dietary.items())[:2])
        ingredients = dict(list(ingredients.items())[:3])

        formatted_recipes.append({
            "title": recipe["title"],
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

def search_recipes_by_query(query):
    """
    Search for recipes based on a query string.
    :param query: The search query string.
    :return: A list of recipes matching the search query.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL query to search in title or ingredients
    cursor.execute("""
        SELECT * FROM recipes
        WHERE title LIKE ? OR ingredients LIKE ?
    """, (f"%{query}%", f"%{query}%"))

    recipes = cursor.fetchall()
    conn.close()

    # Format and return the results
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

        # Limit dietary preferences to 2 and ingredients to 3
        dietary = dict(list(dietary.items())[:2])
        ingredients = dict(list(ingredients.items())[:3])

        formatted_recipes.append({
            "title": recipe["title"],
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
