import os
from flask import Flask
from routes.user_routes import user_blueprint
from routes.recipe_routes import recipe_blueprint
from routes.meal_plan_routes import meal_plan_blueprint
from routes.recipe_details_routes import recipe_details_blueprint
from routes.daily_recommendation_routes import daily_recommendations_blueprint 
from routes.image_classification_routes import image_classification_blueprint

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(recipe_blueprint, url_prefix="/recipes")
app.register_blueprint(meal_plan_blueprint, url_prefix="/meal_plan")
app.register_blueprint(recipe_details_blueprint, url_prefix="/recipe_details")
app.register_blueprint(daily_recommendations_blueprint, url_prefix="/daily_recommendations")
app.register_blueprint(image_classification_blueprint, url_prefix="/image")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)