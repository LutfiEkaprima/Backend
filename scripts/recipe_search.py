from scripts.data_storage import get_db_connection

def search_recipes(user_input):
    """
    Search for recipes based on a query and user-defined filters.
    :param user_input: Dictionary containing the search query and filter criteria.
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
    sql_query = f"SELECT title, image, is_breakfast, is_lunch, is_dinner, is_snack, is_dessert, " \
                f"is_vegetarian, is_vegan, is_pescatarian, is_paleo, is_dairy_free, is_fat_free, " \
                f"is_peanut_free, is_soy_free, is_wheat_free, is_low_carb, is_low_cal, is_low_fat, " \
                f"is_low_sodium, is_low_sugar, is_low_cholesterol FROM recipes WHERE {where_clause}"

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

        formatted_recipes.append({
            "title": recipe["title"],
            "image": recipe["image"],  # Path image langsung dari database
            "meal_type": {
                "breakfast": recipe["is_breakfast"],
                "lunch": recipe["is_lunch"],
                "dinner": recipe["is_dinner"],
                "snack": recipe["is_snack"],
                "dessert": recipe["is_dessert"]
            },
            "dietary": dietary,
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

    cursor.execute("""
        SELECT title, image, is_breakfast, is_lunch, is_dinner, is_snack, is_dessert FROM recipes
        WHERE title LIKE ? OR ingredients LIKE ?
    """, (f"%{query}%", f"%{query}%"))

    recipes = cursor.fetchall()
    conn.close()

    formatted_recipes = []
    for recipe in recipes:
        formatted_recipes.append({
            "title": recipe["title"],
            "image": recipe["image"],  # Path image langsung dari database
            "meal_type": {
                "breakfast": recipe["is_breakfast"],
                "lunch": recipe["is_lunch"],
                "dinner": recipe["is_dinner"],
                "snack": recipe["is_snack"],
                "dessert": recipe["is_dessert"]
            }
        })

    return formatted_recipes