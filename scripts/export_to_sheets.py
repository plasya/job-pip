#!/usr/bin/env python3
"""Export review/shortlist jobs to CSV for Google Sheets."""

import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.storage.db import get_connection, init_db


def main() -> None:
    """Export jobs to CSV."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'jobs.db')
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Query jobs with scores
    cursor.execute("""
        SELECT j.company, j.title, j.url, s.score_total, s.shortlist_status,
               s.chosen_lane, s.chosen_anchor_resume,
               COALESCE(s.notes, '') as notes,
               COALESCE(s.applied_status, '') as applied_status,
               COALESCE(s.doc_link, '') as doc_link
        FROM jobs j
        JOIN job_scores s ON j.job_id = s.job_id
        WHERE s.shortlist_status IN ('review', 'shortlist')
        ORDER BY s.score_total DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    # Write to CSV
    output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'review_queue.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['company', 'title', 'url', 'score_total', 'shortlist_status', 'chosen_lane', 'chosen_anchor_resume', 'notes', 'applied_status', 'doc_link'])
        writer.writerows(rows)

    print(f"Exported {len(rows)} jobs to {output_path}")


if __name__ == '__main__':
    main()