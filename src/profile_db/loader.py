"""Load experiences and projects from YAML files."""

from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError as exc:
    raise RuntimeError(
        'PyYAML is required for profile loading. Install with: pip install pyyaml'
    ) from exc


def load_experiences(dir_path: str) -> List[Dict[str, Any]]:
    """
    Load all experience YAML files from a directory.

    Args:
        dir_path: Path to experiences directory.

    Returns:
        List of parsed experience dictionaries.
    """
    directory = Path(dir_path)
    experiences = []

    if not directory.exists():
        return experiences

    for yaml_file in sorted(directory.glob('*.yaml')) + sorted(directory.glob('*.yml')):
        try:
            content = yaml.safe_load(yaml_file.read_text(encoding='utf-8'))
            if content:
                experiences.append(content)
        except Exception:
            continue

    return experiences


def load_projects(dir_path: str) -> List[Dict[str, Any]]:
    """
    Load all project YAML files from a directory.

    Args:
        dir_path: Path to projects directory.

    Returns:
        List of parsed project dictionaries.
    """
    directory = Path(dir_path)
    projects = []

    if not directory.exists():
        return projects

    for yaml_file in sorted(directory.glob('*.yaml')) + sorted(directory.glob('*.yml')):
        try:
            content = yaml.safe_load(yaml_file.read_text(encoding='utf-8'))
            if content:
                projects.append(content)
        except Exception:
            continue

    return projects
