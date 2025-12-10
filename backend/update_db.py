import sqlite3
import os

# Database path
db_path = "jerrytech.db"

if not os.path.exists(db_path):
    print(f"Database file {db_path} not found.")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(products)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if "images" not in columns:
        print("Adding 'images' column to products table...")
        cursor.execute("ALTER TABLE products ADD COLUMN images TEXT")
        conn.commit()
        print("Column added successfully.")
    else:
        print("'images' column already exists.")
        
    conn.close()
    
except Exception as e:
    print(f"Error updating database: {e}")
