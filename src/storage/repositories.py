"""Data access repositories."""

import json
import sqlite3
from typing import Optional

from src.normalize.models import Job, NormalizedJob
from src.scoring.models import ScoreResult


class JobRepository:
    """Repository for job entities."""
    
    def __init__(self, connection: sqlite3.Connection) -> None:
        """
        Initialize job repository.
        
        Args:
            connection: SQLite database connection.
        """
        self.conn = connection
    

    def insert_normalized_job(self, job: NormalizedJob) -> int:
        """
        Insert a normalized job record.
        
        Args:
            job: NormalizedJob object to insert.
        
        Returns:
            ID of inserted record.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO jobs 
            (source, company, title, location_raw, url, description_text, posted_at_raw,
             employment_type_raw, salary_raw, dedupe_key, discovered_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job.source,
            job.company,
            job.title,
            job.location_raw,
            job.url,
            job.description_text,
            job.posted_at_raw,
            job.employment_type_raw,
            job.salary_raw,
            job.dedupe_key,
            job.discovered_at,
            job.status,
        ))
        self.conn.commit()
        return cursor.lastrowid or 0
    
    def get_by_url(self, url: str) -> Optional[Job]:
        """
        Retrieve job by URL.
        
        Args:
            url: Job posting URL.
        
        Returns:
            Job object or None if not found.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE url = ?", (url,))
        row = cursor.fetchone()
        return self._row_to_job(row) if row else None
    
    def get_all(self) -> list[Job]:
        """
        Retrieve all jobs.
        
        Returns:
            List of Job objects.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [self._row_to_job(row) for row in rows]
    
    def insert_score(self, score_result: ScoreResult) -> None:
        """
        Insert or replace a score result.
        
        Args:
            score_result: ScoreResult object to insert.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO job_scores 
            (job_id, score_total, decision, matched_skills, missing_skills, reasons, shortlist_status, chosen_lane, chosen_anchor_resume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            score_result.job_id,
            score_result.score_total,
            score_result.decision,
            json.dumps(score_result.matched_skills),
            json.dumps(score_result.missing_skills),
            json.dumps(score_result.reasons),
            score_result.shortlist_status,
            score_result.chosen_lane,
            score_result.chosen_anchor_resume,
        ))
        self.conn.commit()
    

