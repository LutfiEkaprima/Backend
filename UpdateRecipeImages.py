import os
from scripts.data_storage import get_db_connection
from fuzzywuzzy import fuzz

def update_all_recipe_images(image_directory):
    """
    Update the "image" field in the "recipes" table for all rows using
    images in the specified directory.

    :param image_directory: Directory containing recipe images.
    """
    # Get list of image files in the directory
    image_files = [f for f in os.listdir(image_directory) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

    # Replace spaces with dashes in image file names
    image_files = [f.replace(" ", "-") for f in image_files]

    # Establish database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all recipe titles from the database
    cursor.execute("SELECT title FROM recipes")
    recipes = cursor.fetchall()

    for recipe in recipes:
        (title,) = recipe
        title_clean = title.lower().replace(" ", "-")  # Replace spaces with dashes in the title

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
            image_path = f"http://158.140.161.26:8080/{image_directory}/{best_match}"

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
    update_all_recipe_images(image_dir)
