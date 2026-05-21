import sqlite3

def migrate():
    db = sqlite3.connect("sudoku.db")
    cursor = db.cursor()

    # ✅ Check if users table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='users'
    """)
    table_exists = cursor.fetchone()

    if not table_exists:
        print("⚠️ users table does not exist yet. Skipping migration.")
        db.close()
        return

    # ✅ Check existing columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]

    if "password" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN password TEXT")
        print("✅ password column added")

    db.commit()
    db.close()
