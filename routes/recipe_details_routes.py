from flask import Blueprint, jsonify
import json
from pathlib import Path

# Define the Blueprint
recipe_details_blueprint = Blueprint("recipe_details_route", __name__)

def get_recipe_details(title):
    """
    Retrieve the details of a specific recipe by title.
    """
    try:
        # Path to the JSON file
        json_path = Path(__file__).resolve().parent.parent / "data" / "Recipe_Details.json"

        if not json_path.exists():
            return {"error": f"Recipe_Details.json file not found at {json_path}"}, 404

        # Load the JSON file
        with open(json_path, "r", encoding="utf-8") as f:
            recipes = json.load(f)

        # Find the recipe with the given title (case-insensitive match)
        recipe = next((r for r in recipes if r["title"].strip().lower() == title.strip().lower()), None)

        if not recipe:
            return {"error": f"Recipe with title '{title}' not found"}, 404

        # Format the response to exclude unnecessary keys (if needed)
        formatted_recipe = {
            "title": recipe["title"],
            "description": recipe["desc"],
            "calories": recipe["calories"],
            "protein": recipe["protein"],
            "fat": recipe["fat"],
            "sodium": recipe["sodium"],
            "rating": recipe.get("rating", 0),  # Default to 0 if not provided
            "ingredients": recipe["ingredients"],
            "directions": recipe["directions"],
            "categories": recipe["categories"],
            "date": recipe["date"]
        }

        return formatted_recipe
    except json.JSONDecodeError:
        return {"error": "Invalid JSON file. Please check the format."}, 500
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