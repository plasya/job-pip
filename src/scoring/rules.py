"""Scoring rules for job matching."""

from typing import Any, Dict, List, Optional, Set
import re

from src.normalize.models import NormalizedJob
from src.scoring.models import ScoreResult


def extract_all_skills(
    experiences: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
    profile: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """
    Extract all skill tags from experiences, projects, and profile.

    Args:
        experiences: List of experience dictionaries.
        projects: List of project dictionaries.
        profile: Profile dictionary containing certifications and skill groups.

    Returns:
        Flattened list of skill tags.
    """
    skills = set()

    # Extract from experiences
    for exp in experiences:
        skill_tags = exp.get('skill_tags', {})
        if isinstance(skill_tags, dict):
            for category_skills in skill_tags.values():
                if isinstance(category_skills, list):
                    skills.update(s.lower() for s in category_skills)
        elif isinstance(skill_tags, list):
            skills.update(s.lower() for s in skill_tags)

    # Extract from projects
    for proj in projects:
        skill_tags = proj.get('skill_tags', {})
        if isinstance(skill_tags, dict):
            for category_skills in skill_tags.values():
                if isinstance(category_skills, list):
                    skills.update(s.lower() for s in category_skills)
        elif isinstance(skill_tags, list):
            skills.update(s.lower() for s in skill_tags)

    # Extract from profile certifications
    if profile:
        certifications = profile.get('certifications', [])
        if isinstance(certifications, list):
            for cert in certifications:
                cert_skills = cert.get('skill_tags', {})
                if isinstance(cert_skills, dict):
                    for category_skills in cert_skills.values():
                        if isinstance(category_skills, list):
                            skills.update(s.lower() for s in category_skills)
                elif isinstance(cert_skills, list):
                    skills.update(s.lower() for s in cert_skills)

        # Extract from top-level skill groups
        skill_groups = [
            'languages', 'backend', 'frontend', 'cloud',
            'data_engineering', 'databases', 'ml_ai', 'devops'
        ]
        for group in skill_groups:
            group_skills = profile.get(group, [])
            if isinstance(group_skills, list):
                skills.update(s.lower() for s in group_skills)
            elif isinstance(group_skills, dict):
                for category_skills in group_skills.values():
                    if isinstance(category_skills, list):
                        skills.update(s.lower() for s in category_skills)

    return sorted(list(skills))


def score_job(
    job: NormalizedJob,
    experiences: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
    profile: Optional[Dict[str, Any]] = None,
) -> ScoreResult:
    candidate_skills = candidate_skill_set(experiences, projects, profile)
    domain_tags = extract_domain_tags(experiences, projects)
    target_roles = extract_target_roles(profile)

    description_text = job.description_text or ""
    job_title = job.title or ""

    signals = extract_job_signals(description_text, candidate_skills)

    must_have_skills = signals["must_have_skills"]
    preferred_skills = signals["preferred_skills"]

    must_have_score = score_overlap(must_have_skills, candidate_skills)
    preferred_score = score_overlap(preferred_skills, candidate_skills)
    title_score = score_title(job_title, target_roles)
    domain_score = score_domain(description_text, domain_tags)
    seniority_score = score_seniority(job_title, profile)
    
    job_lane = infer_job_lane(job_title, description_text)
    lane_fit_score = score_lane_fit(job_lane, experiences, projects)

    score_total = (
        0.30 * title_score +
        0.30 * must_have_score +
        0.15 * preferred_score +
        0.10 * domain_score +
        0.05 * seniority_score +
        0.10 * lane_fit_score
    )

    if score_total >= 0.6:
        decision = "strong_fit"
    elif score_total >= 0.35:
        decision = "possible_fit"
    else:
        decision = "weak_fit"

    matched_skills = sorted([
        skill for skill in must_have_skills + preferred_skills
        if skill in candidate_skills
    ])
    missing_skills = sorted([
        skill for skill in must_have_skills + preferred_skills
        if skill not in candidate_skills
    ])

    component_scores = {
        "title_score": round(title_score, 4),
        "must_have_skill_score": round(must_have_score, 4),
        "preferred_skill_score": round(preferred_score, 4),
        "domain_score": round(domain_score, 4),
        "seniority_score": round(seniority_score, 4),
        "lane_fit_score": round(lane_fit_score, 4),
    }

    reasons = [
        f"title_score={title_score:.2f}",
        f"must_have_skill_score={must_have_score:.2f}",
        f"preferred_skill_score={preferred_score:.2f}",
        f"domain_score={domain_score:.2f}",
        f"seniority_score={seniority_score:.2f}",
        f"lane_fit_score={lane_fit_score:.2f} ({job_lane})",
    ]

    # Calculate shortlist status
    if score_total >= 0.40:
        shortlist_status = "shortlist"
    elif score_total >= 0.30:
        shortlist_status = "review"
    else:
        shortlist_status = "reject"

    # Map lane to anchor resume
    lane_to_anchor = {
        "lane_java_spring_backend_fullstack": "anchor_backend_java",
        "lane_py_node_aws_genai_fullstack": "anchor_backend_ai",
        "lane_data_ml_analyst_engineer": "anchor_data_ml",
        "lane_unknown": None,
    }
    chosen_anchor_resume = lane_to_anchor.get(job_lane)

    return ScoreResult(
        job_id=job.job_id or 0,
        score_total=score_total,
        decision=decision,
        component_scores=component_scores,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        reasons=reasons,
        shortlist_status=shortlist_status,
        chosen_lane=job_lane,
        chosen_anchor_resume=chosen_anchor_resume,
    )

def normalize_text(text: str) -> str:
    return (text or "").lower()


def candidate_skill_set(
    experiences: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
    profile: Optional[Dict[str, Any]] = None,
) -> Set[str]:
    return set(extract_all_skills(experiences, projects, profile))


def extract_domain_tags(
    experiences: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
) -> Set[str]:
    tags: Set[str] = set()

    for item in experiences + projects:
        domain_tags = item.get("domain_tags", [])
        if isinstance(domain_tags, list):
            tags.update(str(tag).lower() for tag in domain_tags)

    return tags


def extract_target_roles(profile: Optional[Dict[str, Any]] = None) -> List[str]:
    if not profile:
        return []

    possible_keys = ["target_roles", "roles", "preferred_roles"]
    roles: List[str] = []

    for key in possible_keys:
        value = profile.get(key, [])
        if isinstance(value, list):
            roles.extend(str(v).lower() for v in value)

    return roles


def extract_job_signals(
    description_text: str,
    candidate_skills: Set[str],
) -> Dict[str, List[str]]:
    text = normalize_text(description_text)

    must_patterns = [
        r"required[:\-\s]",
        r"requirements[:\-\s]",
        r"must have[:\-\s]",
        r"experience with[:\-\s]",
        r"qualifications[:\-\s]",
    ]
    preferred_patterns = [
        r"preferred[:\-\s]",
        r"nice to have[:\-\s]",
        r"bonus[:\-\s]",
        r"plus[:\-\s]",
    ]

    must_have_skills: Set[str] = set()
    preferred_skills: Set[str] = set()

    # Simple sentence-ish splitting
    chunks = re.split(r"[\n\.•]", text)

    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        for skill in candidate_skills:
            if skill not in chunk:
                continue

            if any(re.search(p, chunk) for p in must_patterns):
                must_have_skills.add(skill)
            elif any(re.search(p, chunk) for p in preferred_patterns):
                preferred_skills.add(skill)

    # Fallback: if no must/preferred sections detected, use all matched skills as must-have-lite
    if not must_have_skills and not preferred_skills:
        for skill in candidate_skills:
            if skill in text:
                must_have_skills.add(skill)

    return {
        "must_have_skills": sorted(must_have_skills),
        "preferred_skills": sorted(preferred_skills),
    }


def score_overlap(required: List[str], candidate: Set[str]) -> float:
    if not required:
        return 0.0
    matched = [skill for skill in required if skill in candidate]
    return len(matched) / len(required)


def score_title(job_title: str, target_roles: List[str]) -> float:
    jt = normalize_text(job_title)
    if not jt or not target_roles:
        return 0.0

    for role in target_roles:
        if role in jt or jt in role:
            return 1.0

    jt_words = set(jt.split())
    best = 0.0
    for role in target_roles:
        role_words = set(role.split())
        if not role_words:
            continue
        overlap = len(jt_words & role_words) / len(role_words)
        best = max(best, overlap)

    return best


def score_domain(
    description_text: str,
    domain_tags: Set[str],
) -> float:
    text = normalize_text(description_text)
    if not domain_tags:
        return 0.0

    mentioned = [tag for tag in domain_tags if tag in text]
    if not mentioned:
        return 0.0

    return min(1.0, len(mentioned) / 3)


def score_seniority(job_title: str, profile: Optional[Dict[str, Any]] = None) -> float:
    jt = normalize_text(job_title)
    desired = normalize_text(str((profile or {}).get("seniority_level", "")))

    if not jt:
        return 0.0

    if "senior" in jt:
        return 1.0 if desired in {"senior", "mid", ""} else 0.5
    if "staff" in jt or "lead" in jt or "principal" in jt:
        return 0.8
    if "junior" in jt:
        return 0.2 if desired in {"senior"} else 0.8

    return 0.6

def infer_job_lane(job_title: str, description_text: str) -> str:
    """Infer the job lane from title and description with strict priority order."""
    # Check title first, then description
    title_text = normalize_text(job_title)
    desc_text = normalize_text(description_text)
    full_text = title_text + " " + desc_text
    
    # Priority 1: Data/ML analyst engineer - strict check for data-focused roles
    data_title_keywords = ["data scientist", "data engineer", "machine learning", "ml engineer", "analytics engineer", "analyst"]
    if any(term in title_text for term in data_title_keywords):
        return "lane_data_ml_analyst_engineer"
    
    # Only classify as Data/ML if multiple data terms are present
    data_ml_keywords = ["spark", "etl", "data pipeline", "data warehouse", "data lake", "data science", "pandas", "numpy", "scikit", "tensorflow", "pytorch", "feature engineering", "analyst", "analytics"]
    data_term_count = sum(1 for term in data_ml_keywords if term in full_text)
    if data_term_count >= 2:  # Require at least 2 data-specific terms
        return "lane_data_ml_analyst_engineer"
    
    # Priority 2: Java/Spring backend fullstack - specific Java terms (avoid substring matches)
    java_keywords = ["spring", "spring boot", "kafka", "microservices", "hibernate", "maven", "gradle", "jpa"]
    # Handle Java separately with word-boundary check
    java_check = bool(re.search(r'\bjava\b', full_text)) or any(term in full_text for term in java_keywords)
    if java_check:
        return "lane_java_spring_backend_fullstack"
    
    # Priority 3: Python/Node GenAI fullstack
    py_genai_keywords = ["python", "django", "flask", "fastapi", "node", "express", "javascript", "typescript", "llm", "rag", "langchain", "transformers", "genai", "openai", "aws", "lambda", "s3", "docker", "kubernetes"]
    if any(term in full_text for term in py_genai_keywords):
        return "lane_py_node_aws_genai_fullstack"
    
    return "lane_unknown"


def score_lane_fit(
    job_lane: str,
    experiences: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
) -> float:
    """Compute lane fit score as max matching lane_fit / target_lane_fit."""
    if job_lane == "lane_unknown":
        return 0.0
    
    max_fit = 0.0
    
    for item in experiences + projects:
        lane_fit = item.get("lane_fit", {})
        if not isinstance(lane_fit, dict):
            continue
            
        target_fit = lane_fit.get(job_lane, 0.0)
        if target_fit > 0:
            # Find the highest lane_fit value for this item
            max_lane_fit = max(lane_fit.values()) if lane_fit else 0.0
            if max_lane_fit > 0:
                fit_score = target_fit / max_lane_fit
                max_fit = max(max_fit, fit_score)
    
    return min(1.0, max_fit)