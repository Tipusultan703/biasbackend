# backend/db.py
import sqlite3

def init_db():
    """Initialize SQLite database."""
    conn = sqlite3.connect('bias_news.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY, 
            original TEXT, 
            rewritten TEXT, 
            bias_score REAL, 
            sources TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    """Connect to SQLite database."""
    return sqlite3.connect('bias_news.db')

def save_article(original, rewritten, bias_score, sources):
    """Save analyzed article to DB."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO articles (original, rewritten, bias_score, sources) VALUES (?, ?, ?, ?)",
                   (original, rewritten, bias_score, ", ".join(sources)))
    conn.commit()
    conn.close()
