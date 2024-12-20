from flask import Blueprint, request, jsonify
from scripts.user_management import register_user, login_user
from scripts.weekly_meal_plan import generate_meal_plan  # Import fungsi generate_meal_plan

# Inisialisasi Blueprint
auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route("/register", methods=["GET"])
def register():
    """
    Endpoint untuk registrasi pengguna baru.
    """
    user_data = request.get_json()  # Ambil data dari request body
    if not user_data:
        return jsonify({"error": "Invalid input"}), 400

    # Register user
    response, status = register_user(user_data)
    
    if status == 201:  # Jika berhasil terdaftar
        user_id = user_data.get('userId')  # Ambil user_id dari respons registrasi
        if not user_id:
            return jsonify({"error": "User ID not found"}), 500
        
        # Generate meal plan untuk user yang baru terdaftar
        try:
            meal_plan = generate_meal_plan(user_id)
            response["meal_plan"] = meal_plan  # Sertakan meal plan dalam respons
        except Exception as e:
            return jsonify({"error": "Failed to generate meal plan", "details": str(e)}), 500

    return jsonify(response), status


@auth_blueprint.route("/login", methods=["GET"]) 
def login():
    """
    Endpoint untuk login pengguna.
    """
    user_data = request.get_json()  # Ambil data dari request body
    if not user_data:
        return jsonify({"error": "Invalid input"}), 400

    response, status = login_user(user_data)
    return jsonify(response), status
