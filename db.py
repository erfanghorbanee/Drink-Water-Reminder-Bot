import sqlite3

DB_FILE = "users.db"

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            frequency INTEGER DEFAULT NULL,
            active INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def save_user(chat_id, active=1):
    """Save a new user or update their active status."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (chat_id, active) VALUES (?, ?) ON CONFLICT(chat_id) DO UPDATE SET active=?", 
                   (chat_id, active, active))
    conn.commit()
    conn.close()

def update_frequency(chat_id, frequency):
    """Update the user's reminder frequency and activate reminders."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET frequency=?, active=1 WHERE chat_id=?", (frequency, chat_id))
    conn.commit()
    conn.close()

def get_user_frequency(chat_id):
    """Retrieve the user's reminder frequency."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT frequency FROM users WHERE chat_id=?", (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_user_status(chat_id):
    """Retrieve whether the user has active reminders."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT active FROM users WHERE chat_id=?", (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0  # Default to inactive

def deactivate_reminders(chat_id):
    """Deactivate reminders for a user."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET active=0 WHERE chat_id=?", (chat_id,))
    conn.commit()
    conn.close()
