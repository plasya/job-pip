"""Database connection and initialization."""

import sqlite3
from pathlib import Path


def get_connection(db_path: str) -> sqlite3.Connection:
    """
    Get a SQLite database connection.
    
    Args:
        db_path: Path to SQLite database file.
    
    Returns:
        SQLite connection object.
    """
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    """
    Initialize database schema.
    
    Args:
        db_path: Path to SQLite database file.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            company TEXT,
            title TEXT,
            location_raw TEXT,
            url TEXT,
            description_text TEXT,
            posted_at_raw TEXT,
            employment_type_raw TEXT,
            salary_raw TEXT,
            dedupe_key TEXT NOT NULL UNIQUE,
            discovered_at TIMESTAMP,
            status TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_scores (
            job_id INTEGER PRIMARY KEY,
            score_total REAL,
            decision TEXT,
            matched_skills TEXT,
            missing_skills TEXT,
            reasons TEXT,
            shortlist_status TEXT,
            chosen_lane TEXT,
            chosen_anchor_resume TEXT,
            notes TEXT,
            applied_status TEXT,
            doc_link TEXT,
            scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

