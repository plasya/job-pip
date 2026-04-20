"""Build search queries from palette configurations."""

from typing import Dict, Any, List


def build_palette_queries(palette_name: str, palette_config: Dict[str, Any], locations: Dict[str, List[str]]) -> List[Dict[str, str]]:
    """
    Build Boolean search queries from palette and location configurations.
    
    Args:
        palette_name: Name of the search palette.
        palette_config: Palette configuration dictionary.
        locations: Location configuration dictionary.
    
    Returns:
        List of query objects with track, location, and query fields.
    """
    queries = []
    
    # Build role terms OR clause
    role_terms = palette_config["role_terms"]
    role_clause = " OR ".join(f'"{term}"' for term in role_terms)
    if len(role_terms) > 1:
        role_clause = f"({role_clause})"
    
    # Build stack terms OR clause
    stack_terms = palette_config["stack_terms"]
    stack_clause = " OR ".join(f'"{term}"' for term in stack_terms)
    if len(stack_terms) > 1:
        stack_clause = f"({stack_clause})"
    
    # Combine role and stack terms
    base_query = f"{role_clause} {stack_clause}"
    
    # Generate queries for each location and ATS domain combination
    for location_key in locations.keys():
        for ats_domain in palette_config["ats_domains"]:
            query_obj = {
                "track": palette_name,
                "location": location_key,
                "query": f"{base_query} site:{ats_domain}"
            }
            queries.append(query_obj)
    
    return queries