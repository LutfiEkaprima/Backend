def filter_recipes_by_tags(recipes, tags):
    """
    Filter recipes by selected tags.
    :param recipes: A list of recipes (rows from the database).
    :param tags: A dictionary of selected tags (e.g., {"vegetarian": true}).
    :return: A list of recipes that match the tags.
    """
    if not tags:
        return recipes  # No filtering needed if no tags are provided

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
