from flask import Blueprint, request, jsonify
from scripts.model_utils import predict_ingredient

image_classification_blueprint = Blueprint("image_classification", __name__)

@image_classification_blueprint.route("/", methods=["POST"])
def classify_image():
    """
    Classify the uploaded image and predict the ingredient.
    """
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        image_file = request.files["image"]
        image_bytes = image_file.read()

        # Predict ingredient
        predicted_label, confidence = predict_ingredient(image_bytes)

        return jsonify({
            "ingredient": predicted_label,
            "confidence": float(confidence)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
