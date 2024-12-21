from flask import Blueprint, jsonify
import ijson
from pathlib import Path

# Define the Blueprint
recipe_details_blueprint = Blueprint("recipe_details_route", __name__)

def get_recipe_details(title):
    """
    Retrieve recipe details using a streaming parser.
    """
    try:
        # Path to the JSON file
        json_path = Path(__file__).resolve().parent.parent / "data" / "Recipe_Details.json"

        if not json_path.exists():
            return {"error": f"Recipe_Details.json file not found at {json_path}"}, 404

        # Open the JSON file and stream parse
        with open(json_path, "r", encoding="utf-8") as f:
            # ijson.items reads each top-level item as a Python dictionary
            recipes = ijson.items(f, "item")

            for recipe in recipes:
                # Case-insensitive match for the title
                if recipe["title"].strip().lower() == title.strip().lower():
                    # Return only the matched recipe
                    return {
                        "title": recipe["title"],
                        "description": recipe.get("desc", "No description"),
                        "calories": recipe.get("calories", 0),
                        "protein": recipe.get("protein", 0),
                        "fat": recipe.get("fat", 0),
                        "sodium": recipe.get("sodium", 0),
                        "rating": recipe.get("rating", 0),
                        "ingredients": recipe.get("ingredients", []),
                        "directions": recipe.get("directions", []),
                        "categories": recipe.get("categories", []),
                        "date": recipe.get("date", "Unknown"),
                    }

        # If no recipe is found, return an error
        return {"error": f"Recipe with title '{title}' not found"}, 404

    except Exception as e:
        return {"error": str(e)}, 500

@recipe_details_blueprint.route("/<string:title>/", methods=["GET"])
def details(title):
    """
    Fetch the full details of a recipe by title.
    """
    recipe = get_recipe_details(title)
    if "error" in recipe:
        return jsonify(recipe), 404
    return jsonify(recipe)