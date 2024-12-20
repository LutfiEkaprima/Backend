from flask import Blueprint, request, jsonify
from scripts.user_management import create_user, get_user

user_blueprint = Blueprint("user", __name__)

@user_blueprint.route("/", methods=["POST"])
def create_or_update_user():
    """  
    Create or update a user.

    {
        "userId": "1",
        "dateReg": "2024-12-08",
        "userName": "John Doe",
        "email": "john.doe@example.com",
        "password": "12345",
        "age": "34",
        "weight": 70,
        "dateBirth": "1990-05-15",
    }

    """
    try:
        user_data = request.get_json()
        response, status_code = create_user(user_data)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_blueprint.route("/<user_id>", methods=["GET"])
def fetch_user(user_id):
    return get_user(user_id)

