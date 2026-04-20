#!/usr/bin/env python3
"""Score jobs against candidate profile."""

import sys
import os
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.profile_db.loader import load_experiences, load_projects
from src.scoring.profile_loader import load_candidate_profile
from src.scoring.rules import score_job
from src.normalize.models import NormalizedJob
from src.storage.db import get_connection, init_db
from src.storage.repositories import JobRepository


def row_to_normalized_job(row: sqlite3.Row) -> NormalizedJob:
    """Convert database row to NormalizedJob."""
    return NormalizedJob(
        job_id=row['job_id'],
        source=row['source'],
        company=row['company'],
        title=row['title'],
        location_raw=row['location_raw'],
        url=row['url'],
        description_text=row['description_text'],
        posted_at_raw=row['posted_at_raw'],
        employment_type_raw=row['employment_type_raw'],
        salary_raw=row['salary_raw'],
        dedupe_key=row['dedupe_key'],
        discovered_at=row['discovered_at'],
        status=row['status'],
    )


def main() -> None:
    # Load candidate profile data
    experiences = load_experiences('configs/profile_db/experiences')
    projects = load_projects('configs/profile_db/projects')
    
    profile = None
    if os.path.exists('configs/profile_db/profile.yaml'):
        profile = load_candidate_profile('configs/profile_db/profile.yaml')
    elif os.path.exists('configs/profile_db/profile.json'):
        profile = load_candidate_profile('configs/profile_db/profile.json')

    # Connect to database
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'jobs.db')
    init_db(db_path)
    conn = get_connection(db_path)
    repository = JobRepository(conn)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs ORDER BY job_id DESC LIMIT 10')
    rows = cursor.fetchall()

    print(f'Scoring {len(rows)} most recent jobs...\n')
    print(f'{"Company":<25} {"Title":<35} {"Score":<8} {"Decision":<15} {"Lane":<25} {"Status":<10} {"Anchor":<15} {"Top Skills"}')
    print('-' * 145)

    for row in rows:
        job = row_to_normalized_job(row)
        result = score_job(job, experiences, projects, profile)
        
        # Save score to database
        repository.insert_score(result)
        
        matched_str = ', '.join(result.matched_skills[:3])
        if len(result.matched_skills) > 3:
            matched_str += '...'
        
        # Extract lane from reasons
        lane_info = "unknown"
        for reason in result.reasons:
            if "lane_fit_score" in reason and "(" in reason:
                lane_info = reason.split("(")[1].rstrip(")")
                break
        
        print(
            f'{job.company[:25]:<25} '
            f'{job.title[:35]:<35} '
            f'{result.score_total:>6.1%} '
            f'{result.decision:<15} '
            f'{lane_info:<25} '
            f'{result.shortlist_status:<10} '
            f'{result.chosen_anchor_resume or "":<15} '
            f'{matched_str}'
        )
    
    conn.close()


if __name__ == '__main__':
    main()
