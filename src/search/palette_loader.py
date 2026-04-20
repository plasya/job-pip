"""Load search palette and location configurations."""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_palettes() -> Dict[str, Dict[str, Any]]:
    """
    Load search palettes from YAML configuration.
    
    Returns:
        Dictionary of palette configurations.
    """
    config_path = Path(__file__).parent.parent.parent / "configs" / "search_palettes.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_locations() -> Dict[str, list[str]]:
    """
    Load location configurations from YAML.
    
    Returns:
        Dictionary mapping location keys to lists of location strings.
    """
    config_path = Path(__file__).parent.parent.parent / "configs" / "locations.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)