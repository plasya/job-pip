"""Load candidate profiles from YAML or JSON files."""

import json
from pathlib import Path
from typing import Any, Dict


def load_candidate_profile(path: str) -> Dict[str, Any]:
    """
    Load a candidate profile from YAML or JSON.

    Args:
        path: Path to the profile file.

    Returns:
        Parsed profile as a dictionary.
    """
    file_path = Path(path)
    text = file_path.read_text(encoding='utf-8')
    suffix = file_path.suffix.lower()

    if suffix in {'.yaml', '.yml'}:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError(
                'PyYAML is required to load YAML profiles. Install with: pip install pyyaml'
            ) from exc
        return yaml.safe_load(text) or {}

    if suffix == '.json':
        return json.loads(text)

    raise ValueError(f'Unsupported profile format: {suffix}')
