import sqlite3
import json

# Path ke file JSON dan SQLite
json_file = "data/Recipe_Details.json"
db_file = "data/NutriDish.db"

# Load data dari file JSON
with open(json_file, "r") as file:
    recipes = json.load(file)  # JSON ini diharapkan sebagai list

# Koneksi ke database SQLite
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Iterasi setiap resep
for recipe_data in recipes:
    # Pastikan data memiliki kunci 'title'
    if "title" not in recipe_data:
        print("Data tanpa title ditemukan. Melewatkan data ini:", recipe_data)
        continue  # Lewati data ini

    # Data dari JSON yang ingin ditambahkan dengan tipe datanya
    columns_to_add = {
        "calories": ("REAL", recipe_data.get("calories")),
        "protein": ("REAL", recipe_data.get("protein")),
        "fat": ("REAL", recipe_data.get("fat")),
        "sodium": ("REAL", recipe_data.get("sodium")),
        "ingredients": ("TEXT", json.dumps(recipe_data.get("ingredients")) if recipe_data.get("ingredients") else None),
        "directions": ("TEXT", json.dumps(recipe_data.get("directions")) if recipe_data.get("directions") else None),
        "categories": ("TEXT", json.dumps(recipe_data.get("categories")) if recipe_data.get("categories") else None),
        "rating": ("REAL", recipe_data.get("rating")),
        "desc": ("TEXT", recipe_data.get("desc")),
        "date": ("TEXT", recipe_data.get("date"))
    }

    # Periksa apakah title dari JSON ada di database
    title_to_check = recipe_data["title"].strip()

    cursor.execute("SELECT title FROM recipes WHERE title = ?", (title_to_check,))
    result = cursor.fetchone()

    if result:
        # Title cocok, tambahkan kolom jika belum ada dan data tidak kosong
        for column_name, (column_type, value) in columns_to_add.items():
            if value is not None:  # Hanya tambahkan jika nilai tidak kosong
                try:
                    cursor.execute(f"ALTER TABLE recipes ADD COLUMN `{column_name}` {column_type}")
                except sqlite3.OperationalError:
                    # Kolom sudah ada
                    pass

                # Update data di kolom tersebut
                cursor.execute(f"UPDATE recipes SET `{column_name}` = ? WHERE title = ?", (value, title_to_check))
        print(f"Data berhasil ditambahkan untuk title: {title_to_check}")
    else:
        print(f"Title '{title_to_check}' tidak ditemukan di database.")

# Commit perubahan dan tutup koneksi
conn.commit()
conn.close()
