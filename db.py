import sqlite3


# Initialize database
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        chat_id INTEGER PRIMARY KEY,
        active INTEGER DEFAULT 0,
        frequency INTEGER DEFAULT 2
    )
    """)
    conn.commit()
    conn.close()

# Save or update a user
def save_user(chat_id, active=1, frequency=2):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (chat_id, active, frequency) VALUES (?, ?, ?)",
                   (chat_id, active, frequency))
    conn.commit()
    conn.close()

# Update user's reminder status
def update_status(chat_id, active):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET active = ? WHERE chat_id = ?", (active, chat_id))
    conn.commit()
    conn.close()

# Update user's reminder frequency
def update_frequency(chat_id, frequency):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET frequency = ?, active = 1 WHERE chat_id = ?", (frequency, chat_id))
    conn.commit()
    conn.close()

# Get user's status
def get_user_status(chat_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT active FROM users WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

# Get user's reminder frequency
def get_user_frequency(chat_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT frequency FROM users WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 2  # Default to 2 hours
