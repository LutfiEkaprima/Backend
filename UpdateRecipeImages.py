import os
from scripts.data_storage import get_db_connection
from fuzzywuzzy import fuzz

def update_recipe_images(image_directory):
    """
    Update the "image" field in the "recipes" table by matching images in the specified directory
    to the recipe titles, only if the "image" field is NULL.

    :param image_directory: Directory containing recipe images.
    """
    # Get list of image files in the directory
    image_files = [f for f in os.listdir(image_directory) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

    # Establish database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all recipe titles and their current image status from the database
    cursor.execute("SELECT title FROM recipes WHERE image IS NULL")
    recipes = cursor.fetchall()

    for recipe in recipes:
        (title,) = recipe
        title_clean = title.lower()

        best_match = None
        best_score = 0

        for image_file in image_files:
            # Remove extension for comparison
            image_name = os.path.splitext(image_file)[0].lower()

            # Calculate similarity score
            score = fuzz.ratio(title_clean, image_name)

            if score > best_score and score >= 55:  # Set a threshold for match
                best_score = score
                best_match = image_file

        if best_match:
            # Construct the image path
            image_path = f"{image_directory}/{best_match}"

            # Update the database with the matched image path
            cursor.execute(
                "UPDATE recipes SET image = ? WHERE title = ? AND image IS NULL",
                (image_path, title)
            )
            print(f"Updated recipe '{title}' with image '{image_path}'")

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("Image update process completed.")

if __name__ == "__main__":
    # Define the image directory (adjust the path as needed)
    image_dir = "image"

    # Run the image update script
    update_recipe_images(image_dir)
