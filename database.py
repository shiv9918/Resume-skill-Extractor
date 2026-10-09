import sqlite3
import os

DB_PATH = 'data/resume_skills.db'

def init_db():
    """Initializes the SQLite database with required tables."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table for resumes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    
    # Table for extracted skills mapping
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER,
            skill_name TEXT NOT NULL,
            FOREIGN KEY(resume_id) REFERENCES resumes(id),
            UNIQUE(resume_id, skill_name)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
