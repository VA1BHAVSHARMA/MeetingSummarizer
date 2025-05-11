import sqlite3

def init_db():
    conn = sqlite3.connect("summaries.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY,
            user_id TEXT,
            summary TEXT
        )"""
    )
    conn.commit()
    conn.close()

def save_summary(user_id, summary):
    conn = sqlite3.connect("summaries.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO summaries (user_id, summary) VALUES (?, ?)", (user_id, summary))
    conn.commit()
    conn.close()

def get_user_history(user_id):
    conn = sqlite3.connect("summaries.db")
    cursor = conn.cursor()
    cursor.execute("SELECT summary FROM summaries WHERE user_id = ?", (user_id,))
    return cursor.fetchall()