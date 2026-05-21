import sqlite3

def init_db():
    conn = sqlite3.connect("sudoku.db")
    cursor = conn.cursor()
    conn.row_factory = sqlite3.Row

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # cursor.execute("""
    #     CREATE TABLE IF NOT EXISTS scores (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         user_id INTEGER,
    #         level TEXT,
    #         score INTEGER,
    #         time INTEGER
    #     )
    # """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    difficulty TEXT,
    score INTEGER,
    time_taken INTEGER,
    mistakes INTEGER,
    result TEXT,
    played_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
    """)

    conn.commit()
    conn.close()
