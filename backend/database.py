import sqlite3

def create_database():

    conn = sqlite3.connect("database/predictions.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            news TEXT,

            prediction TEXT,

            confidence REAL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    conn.commit()

    conn.close()


create_database()