#!/usr/bin/env python3
"""Generate application packet for a specific job."""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.profile_db.loader import load_experiences, load_projects
from src.scoring.profile_loader import load_candidate_profile
from src.storage.db import get_connection, init_db
from src.tailoring.alignment_analyzer import analyze_alignment


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate application packet for a job')
    parser.add_argument('job_id', type=int, help='Job ID to generate packet for')
    args = parser.parse_args()

    # Load profile data
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
    cursor = conn.cursor()

    # Load job data
    cursor.execute('SELECT * FROM jobs WHERE job_id = ?', (args.job_id,))
    job_row = cursor.fetchone()
    if not job_row:
        print(f"Error: Job {args.job_id} not found")
        conn.close()
        return

    # Convert row to dict
    job = dict(job_row)

    # Load job scores
    cursor.execute('SELECT * FROM job_scores WHERE job_id = ?', (args.job_id,))
    score_row = cursor.fetchone()
    conn.close()

    if not score_row:
        print(f"Error: No scores found for job {args.job_id}")
        return

    chosen_anchor_resume = score_row['chosen_anchor_resume']

    # Map anchor to file
    anchor_files = {
        'anchor_backend_java': 'LASYA_SWE_Java.docx',
        'anchor_backend_ai': 'LASYA_SWE_AI.docx',
        'anchor_data_ml': 'LASYA_SWE_D_ML.docx',
    }

    anchor_file = anchor_files.get(chosen_anchor_resume)
    if not anchor_file:
        print(f"Error: No anchor file mapped for {chosen_anchor_resume}")
        return

    anchor_path = os.path.join('configs', 'profile_db', 'anchors', anchor_file)
    if not os.path.exists(anchor_path):
        print(f"Error: Anchor file not found: {anchor_path}")
        return

    # Run alignment analysis
    alignment = analyze_alignment(job, chosen_anchor_resume, experiences, projects, profile or {})

    # Create output directory
    output_dir = os.path.join('outputs', str(args.job_id))
    os.makedirs(output_dir, exist_ok=True)

    # Copy anchor resume
    shutil.copy2(anchor_path, os.path.join(output_dir, 'resume.docx'))

    # Write alignment report
    report_path = os.path.join(output_dir, 'alignment_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(alignment, f, indent=2, ensure_ascii=False)

    # Write suggested edits
    edits_path = os.path.join(output_dir, 'suggested_edits.md')
    with open(edits_path, 'w', encoding='utf-8') as f:
        f.write(f"# Suggested Edits for {job['company']} - {job['title']}\n\n")
        f.write("## Positioning Summary\n")
        f.write(f"{alignment['positioning_summary']}\n\n")

        f.write("## Matched Skills\n")
        for skill in alignment['matched_skills']:
            f.write(f"- {skill}\n")
        f.write("\n")

        f.write("## Missing Skills\n")
        for skill in alignment['missing_skills']:
            f.write(f"- {skill}\n")
        f.write("\n")

        f.write("## Recommended Experience Bullets\n")
        for bullet in alignment['recommended_experience_bullets']:
            f.write(f"- {bullet}\n")
        f.write("\n")

        f.write("## Recommended Project Bullets\n")
        for bullet in alignment['recommended_project_bullets']:
            f.write(f"- {bullet}\n")
        f.write("\n")

        f.write("## Keyword Insertions\n")
        for keyword in alignment['keyword_insertions']:
            f.write(f"- {keyword}\n")
        f.write("\n")

    # Print summary
    print(f"Generated application packet for:")
    print(f"  Company: {job['company']}")
    print(f"  Title: {job['title']}")
    print(f"  Anchor Resume: {chosen_anchor_resume} ({anchor_file})")
    print(f"  Output: {output_dir}")


if __name__ == '__main__':
    main()