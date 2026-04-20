"""Scoring models for job matches."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ScoreResult:
    """Represents scoring output for a job posting."""

    job_id: int
    score_total: float
    decision: str
    component_scores: Dict[str, float]
    matched_skills: List[str]
    missing_skills: List[str]
    reasons: List[str]
    shortlist_status: str
    chosen_lane: str
    chosen_anchor_resume: Optional[str]
