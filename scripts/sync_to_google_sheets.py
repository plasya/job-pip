#!/usr/bin/env python3
"""Sync review/shortlist jobs to Google Sheets."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.storage.db import get_connection, init_db

try:
    from dotenv import load_dotenv
    load_dotenv()
    from googleapiclient.discovery import build
    from google.oauth2.service_account import Credentials
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
print("GOOGLE_AVAILABLE =", GOOGLE_AVAILABLE)

def get_google_sheets_service():
    """Get Google Sheets service with credentials."""
    if not GOOGLE_AVAILABLE:
        return None

    # Check for credentials file
    creds_path = os.path.join(os.path.dirname(__file__), '..', 'credentials', 'service-account.json')
    print("CREDENTIALS PATH =", creds_path)
    print("CREDENTIALS EXISTS =", os.path.exists(creds_path))
    print("SPREADSHEET_ID =", os.getenv("SPREADSHEET_ID"))
    if not os.path.exists(creds_path):
        return None

    try:
        creds = Credentials.from_service_account_file(creds_path)
        return build('sheets', 'v4', credentials=creds)
    except Exception:
        return None


def main() -> None:
    """Sync jobs to Google Sheets."""
    # Check Google Sheets availability
    service = get_google_sheets_service()
    if not service:
        print("Google Sheets integration not available.")
        print("To enable:")
        print("1. Install: pip install google-api-python-client google-auth")
        print("2. Create service account and download credentials to credentials/service-account.json")
        print("3. Share your Google Sheet with the service account email")
        print("4. Set SPREADSHEET_ID environment variable")
        return

    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    if not spreadsheet_id:
        print("Error: SPREADSHEET_ID environment variable not set")
        return

    # Read data from database
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'jobs.db')
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT j.job_id, j.company, j.title, j.url, s.score_total, s.shortlist_status,
               s.chosen_lane, s.chosen_anchor_resume, s.notes, s.applied_status, s.doc_link
        FROM jobs j
        JOIN job_scores s ON j.job_id = s.job_id
        WHERE s.shortlist_status IN ('review', 'shortlist')
        ORDER BY s.score_total DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No jobs to sync")
        return

    # Prepare data for Google Sheets
    headers = ['job_id', 'company', 'title', 'url', 'score_total', 'shortlist_status',
               'chosen_lane', 'chosen_anchor_resume', 'notes', 'applied_status', 'doc_link']
    values = [headers] + [list(row) for row in rows]

    # Clear and update sheet
    range_name = 'review_queue!A:Z'
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range='review_queue!A1',
        valueInputOption='RAW',
        body={'values': values}
    ).execute()

    print(f"Synced {len(rows)} jobs to Google Sheets")


if __name__ == '__main__':
    main()