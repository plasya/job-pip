"""Normalize search results into NormalizedJob objects."""

import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

from src.normalize.models import NormalizedJob


def normalize_search_result(
    serper_result: Dict[str, Any], 
    fetched_job: Dict[str, Optional[str]],
    source: str = 'greenhouse'
) -> NormalizedJob:
    """
    Combine Serper search result with fetched job data into a NormalizedJob.
    
    Args:
        serper_result: Result from Serper search.
        fetched_job: Fetched job data from ATS platform.
        source: Source platform identifier.
    
    Returns:
        NormalizedJob object.
    """
    # Use fetched data if available, otherwise fall back to Serper data
    company = fetched_job.get('company')
    title = fetched_job.get('title')
    
    # If fetched data is missing, parse from Serper title
    if not company or not title:
        serper_title = serper_result.get('title', '')
        if ' - ' in serper_title:
            # Try to parse "Company - Title - Platform" format
            parts = serper_title.split(' - ')
            if len(parts) >= 2:
                if not company:
                    company = parts[0].strip()
                if not title:
                    # Join all parts except first and last (if last is platform)
                    title_parts = parts[1:-1] if len(parts) > 2 and parts[-1].lower() in ['lever', 'greenhouse'] else parts[1:]
                    title = ' - '.join(title_parts).strip()
        else:
            # Fallback to entire title
            if not company:
                company = serper_title
            if not title:
                title = serper_title
    
    location_raw = fetched_job.get('location') or ''
    description_text = fetched_job.get('description_text') or serper_result.get('snippet', '')
    url = serper_result.get('url', '')
    
    # Generate deterministic dedupe key (hash() changes per session; use hashlib instead)
    dedupe_input = f"{source}|{company}|{title}|{url}"
    dedupe_key = hashlib.md5(dedupe_input.encode()).hexdigest()
    
    return NormalizedJob(
        source=source,
        company=company,
        title=title,
        location_raw=location_raw,
        url=url,
        description_text=description_text,
        dedupe_key=dedupe_key,
        discovered_at=datetime.utcnow(),
        status='discovered'
    )