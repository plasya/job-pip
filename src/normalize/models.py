"""Data models for job information."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Job:
    """Represents a normalized job posting."""
    
    title: str
    company: str
    url: str
    description: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    source: Optional[str] = None
    posted_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __hash__(self) -> int:
        """Make Job hashable based on unique identifiers."""
        return hash((self.title, self.company, self.url))


@dataclass
class NormalizedJob:
    """Step-1 ingestion model for raw job data."""
    
    job_id: Optional[int] = None
    source: str = ""
    company: str = ""
    title: str = ""
    location_raw: Optional[str] = None
    url: str = ""
    description_text: Optional[str] = None
    posted_at_raw: Optional[str] = None
    employment_type_raw: Optional[str] = None
    salary_raw: Optional[str] = None
    dedupe_key: str = ""
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"
