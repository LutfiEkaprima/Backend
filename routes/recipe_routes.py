from flask import Blueprint, request, jsonify
from scripts.recipe_search import search_recipes, search_recipes_by_query
from routes.recipe_details_routes import get_recipe_details  # Import the new function

recipe_blueprint = Blueprint("recipe", __name__)

@recipe_blueprint.route("/", methods=["POST"])
def search():
    """
    Search for recipes based on query and filters with pagination.
    """
    try:
        user_input = request.get_json()
        page = int(request.args.get("page", 1))  # Default page = 1
        page_size = int(request.args.get("page_size", 100))  # Default page size = 100
        results = search_recipes(user_input, page=page, page_size=page_size)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@recipe_blueprint.route("/search", methods=["GET"])
def search_get():
    """
    Search for recipes based on a query passed as a URL parameter with pagination.
    """
    try:
        query = request.args.get("query", "").lower()  # Get query parameter from URL
        page = int(request.args.get("page", 1))  # Default page = 1
        page_size = int(request.args.get("page_size", 100))  # Default page size = 100
        results = search_recipes_by_query(query, page=page, page_size=page_size)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500