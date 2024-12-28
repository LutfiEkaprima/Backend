import sqlite3

# Path ke database
db_path = "data/NutriDish.db"

# Koneksi ke database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query untuk menghitung jumlah nilai NULL di kolom image
query = "SELECT COUNT(*) AS count_null_images FROM recipes WHERE image IS NULL;"
cursor.execute(query)

# Ambil hasil
result = cursor.fetchone()
count_null_images = result[0]

print(f"Jumlah nilai NULL di kolom 'image': {count_null_images}")

# Tutup koneksi
cursor.close()
conn.close()
