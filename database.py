import sqlite3
import os
import logging
from typing import List, Dict, Any, Optional

DB_PATH = 'data/resume_skills.db'

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Creates and returns a connection to the SQLite database."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path: str = DB_PATH) -> None:
    """Initializes the SQLite database with required tables."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Table for resumes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table for extracted skills mapping
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(resume_id) REFERENCES resumes(id) ON DELETE CASCADE,
            UNIQUE(resume_id, skill_name)
        )
    ''')
    
    conn.commit()
    conn.close()
    logging.info(f"Database initialized successfully at {db_path}.")

def save_resume_and_skills(filename: str, content: str, skills: List[str], db_path: str = DB_PATH) -> int:
    """
    Saves or updates a resume and stores its extracted skills in a transaction.
    Returns the resume ID.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        # Insert or ignore/replace resume
        cursor.execute('''
            INSERT INTO resumes (filename, content)
            VALUES (?, ?)
            ON CONFLICT(filename) DO UPDATE SET content=excluded.content
        ''', (filename, content))
        
        cursor.execute('SELECT id FROM resumes WHERE filename = ?', (filename,))
        resume_id = cursor.fetchone()[0]
        
        # Clear previous skills for this resume to keep data fresh
        cursor.execute('DELETE FROM extracted_skills WHERE resume_id = ?', (resume_id,))
        
        # Insert new extracted skills
        for skill in skills:
            cursor.execute('''
                INSERT OR IGNORE INTO extracted_skills (resume_id, skill_name)
                VALUES (?, ?)
            ''', (resume_id, skill))
            
        conn.commit()
        logging.info(f"Saved resume '{filename}' (ID: {resume_id}) with {len(skills)} skills.")
        return resume_id
    except Exception as e:
        conn.rollback()
        logging.error(f"Failed to save resume '{filename}': {e}")
        raise
    finally:
        conn.close()

def get_resume_skills(filename: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieves resume record and list of skills by filename."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, filename, content FROM resumes WHERE filename = ?', (filename,))
        row = cursor.fetchone()
        if not row:
            return None
        
        resume_id, fname, content = row
        cursor.execute('SELECT skill_name FROM extracted_skills WHERE resume_id = ? ORDER BY skill_name', (resume_id,))
        skills = [r[0] for r in cursor.fetchall()]
        return {
            "id": resume_id,
            "filename": fname,
            "content": content,
            "skills": skills
        }
    finally:
        conn.close()

def get_all_resumes_with_skills(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Fetches all stored resumes and their extracted skills."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, filename FROM resumes ORDER BY id')
        resumes = cursor.fetchall()
        results = []
        for r_id, fname in resumes:
            cursor.execute('SELECT skill_name FROM extracted_skills WHERE resume_id = ? ORDER BY skill_name', (r_id,))
            skills = [s[0] for s in cursor.fetchall()]
            results.append({
                "id": r_id,
                "filename": fname,
                "skills": skills
            })
        return results
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
