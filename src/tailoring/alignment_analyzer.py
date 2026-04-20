"""Analyze job alignment for resume tailoring."""

from typing import Any, Dict, List, Optional, Set

from src.scoring.rules import extract_all_skills, extract_job_signals, infer_job_lane


def flatten_skill_tags(skill_tags: Any) -> Set[str]:
    skills: Set[str] = set()
    if isinstance(skill_tags, dict):
        for value in skill_tags.values():
            if isinstance(value, list):
                skills.update(str(item).lower() for item in value)
    elif isinstance(skill_tags, list):
        skills.update(str(item).lower() for item in skill_tags)
    return skills


def get_job_text(job: Dict[str, Any]) -> str:
    title = str(job.get('title', '') or '')
    desc = str(job.get('description_text', job.get('description', '')) or '')
    return f"{title}\n{desc}".strip()


def map_anchor_to_lane(chosen_anchor_resume: Optional[str]) -> str:
    anchor_to_lane = {
        'anchor_backend_java': 'lane_java_spring_backend_fullstack',
        'anchor_backend_ai': 'lane_py_node_aws_genai_fullstack',
        'anchor_data_ml': 'lane_data_ml_analyst_engineer',
    }
    return anchor_to_lane.get(chosen_anchor_resume, 'lane_unknown')


def score_bullet(
    bullet: Dict[str, Any],
    target_lane: str,
    required_skills: Set[str],
    job_keywords: Set[str],
) -> float:
    lane_fit = bullet.get('lane_fit', {})
    if not isinstance(lane_fit, dict):
        lane_fit = {}

    target_fit = float(lane_fit.get(target_lane, 0) or 0)
    max_fit = max((float(v or 0) for v in lane_fit.values()), default=0.0)
    lane_score = target_fit / max_fit if max_fit > 0 else 0.0

    bullet_skills = flatten_skill_tags(bullet.get('skill_tags', []))
    overlap = len(required_skills.intersection(bullet_skills))
    overlap_score = overlap / max(len(required_skills), 1)

    text = str(bullet.get('text', '')).lower()
    keyword_matches = len([kw for kw in job_keywords if kw in text])
    keyword_score = keyword_matches / max(len(job_keywords), 1)

    return lane_score * 0.55 + overlap_score * 0.30 + keyword_score * 0.15


def select_bullets(
    items: List[Dict[str, Any]],
    target_lane: str,
    required_skills: Set[str],
    job_keywords: Set[str],
    limit: int = 3,
) -> List[str]:
    scored: List[Dict[str, Any]] = []
    for item in items:
        for bullet in item.get('bullets', []):
            text = str(bullet.get('text', '')).strip()
            if not text:
                continue
            score = score_bullet(bullet, target_lane, required_skills, job_keywords)
            scored.append({'score': score, 'text': text})

    scored.sort(key=lambda entry: (-entry['score'], entry['text']))
    return [entry['text'] for entry in scored[:limit]]


def extract_keywords_from_text(text: str) -> Set[str]:
    words = [word.strip(',.()[]') for word in text.lower().split()]
    return {word for word in words if len(word) > 2}


def analyze_alignment(
    job: Dict[str, Any],
    chosen_anchor_resume: Optional[str],
    experiences: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
    profile: Dict[str, Any],
) -> Dict[str, Any]:
    job_text = get_job_text(job)
    candidate_skills = set(extract_all_skills(experiences, projects, profile))
    signals = extract_job_signals(job_text, candidate_skills)

    required_skills = set(signals['must_have_skills'] + signals['preferred_skills'])
    matched_skills = sorted(skill for skill in required_skills if skill in candidate_skills)
    missing_skills = sorted(skill for skill in required_skills if skill not in candidate_skills)

    lane = map_anchor_to_lane(chosen_anchor_resume)
    if lane == 'lane_unknown':
        lane = infer_job_lane(job.get('title', ''), job_text)

    job_keywords = extract_keywords_from_text(job_text)
    recommended_experience_bullets = select_bullets(experiences, lane, required_skills, job_keywords)
    recommended_project_bullets = select_bullets(projects, lane, required_skills, job_keywords)

    keyword_insertions = []
    if missing_skills:
        keyword_insertions.extend(missing_skills)
    # Keep keywords deterministic and limited
    extra_keywords = sorted(job_keywords - candidate_skills - set(missing_skills))[:5]
    keyword_insertions.extend(extra_keywords)
    keyword_insertions = keyword_insertions[:10]

    positioning_summary = (
        f"The job is best aligned to {lane}. "
        f"You already match {len(matched_skills)} required skill(s) and miss {len(missing_skills)}. "
        f"Use top experience and project bullets that show {chosen_anchor_resume or lane} relevance."
    )

    return {
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'recommended_experience_bullets': recommended_experience_bullets,
        'recommended_project_bullets': recommended_project_bullets,
        'keyword_insertions': keyword_insertions,
        'positioning_summary': positioning_summary,
        'chosen_lane': lane,
        'chosen_anchor_resume': chosen_anchor_resume,
    }
