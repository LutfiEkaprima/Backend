import sqlite3
import json
from pathlib import Path

def import_json_to_db():
    """
    Import data from a large JSON file into an existing SQLite database.
    """
    # Define file paths
    json_path = Path(__file__).resolve().parent / "data" / "Recipe_Details.json"
    db_path = Path(__file__).resolve().parent / "data" / "NutriDish.db"

    # Check if the JSON file exists
    if not json_path.exists():
        print(f"Error: JSON file not found at {json_path}")
        return

    # Connect to the existing SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the new table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recipe_details (
        title TEXT PRIMARY KEY,
        description TEXT,
        calories REAL,
        protein REAL,
        fat REAL,
        sodium REAL,
        rating REAL,
        ingredients TEXT,
        directions TEXT,
        categories TEXT,
        date TEXT
    )
    """)

    # Load JSON data and insert into the database
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            recipes = json.load(f)

            for recipe in recipes:
                if not isinstance(recipe, dict):
                    print(f"Skipping invalid recipe format: {recipe}")
                    continue

                if "title" not in recipe:
                    print(f"Skipping recipe without title: {recipe}")
                    continue

                # Skip recipes with null values for calories, protein, fat, or sodium
                if any(recipe.get(field) is None for field in ["calories", "protein", "fat", "sodium"]):
                    print(f"Skipping recipe with null nutritional values: {recipe}")
                    continue

                try:
                    # Insert each recipe into the new table
                    cursor.execute("""
                    INSERT OR REPLACE INTO recipe_details (
                        title, description, calories, protein, fat, sodium, rating, ingredients, directions, categories, date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        recipe["title"].strip(),
                        recipe.get("desc", "No description"),
                        recipe.get("calories", 0),
                        recipe.get("protein", 0),
                        recipe.get("fat", 0),
                        recipe.get("sodium", 0),
                        recipe.get("rating", 0),
                        json.dumps(recipe.get("ingredients", [])),
                        json.dumps(recipe.get("directions", [])),
                        json.dumps(recipe.get("categories", [])),
                        recipe.get("date", "Unknown"),
                    ))
                except Exception as e:
                    print(f"Failed to insert recipe: {recipe}. Error: {e}")

        # Commit changes to the database
        conn.commit()
        print("Data successfully imported into the recipe_details table.")

    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        # Close the database connection
        conn.close()

if __name__ == "__main__":
    import_json_to_db()