"""Database-backed ingestion of Serper search results."""

import sqlite3
from typing import Dict, Any, List

from src.discover.url_router import route_job_url
from src.fetchers.greenhouse_job import fetch_greenhouse_job
from src.fetchers.lever_job import fetch_lever_job
from src.ingest.normalize_search_result import normalize_search_result
from src.normalize.models import NormalizedJob
from src.storage.db import get_connection, init_db
from src.storage.repositories import JobRepository


def ingest_search_results(db_path: str, search_results: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Ingest search results into SQLite storage.
    
    Args:
        db_path: Path to SQLite database file.
        search_results: List of Serper search result dictionaries.
    
    Returns:
        Summary dictionary with ingestion counts.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    repository = JobRepository(conn)
    
    summary = {
        "total_results": 0,
        "attempted": 0,
        "inserted": 0,
        "duplicates": 0,
        "skipped_non_greenhouse": 0,
        "failed": 0,
    }
    
    for result in search_results:
        summary["total_results"] += 1
        url = result.get("url", "")
        if not url:
            summary["failed"] += 1
            continue

        route = route_job_url(url)
        if route not in {"greenhouse", "lever"}:
            summary["skipped_non_greenhouse"] += 1
            continue

        summary["attempted"] += 1
        if route == "greenhouse":
            fetched_job = fetch_greenhouse_job(url)
        else:
            fetched_job = fetch_lever_job(url)

        try:
            normalized_job = normalize_search_result(result, fetched_job, source=route)
            repository.insert_normalized_job(normalized_job)
            summary["inserted"] += 1
        except sqlite3.IntegrityError:
            summary["duplicates"] += 1
        except Exception:
            summary["failed"] += 1
    
    conn.close()
    return summary
