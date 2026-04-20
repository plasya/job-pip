"""Execute Serper searches for palette-based job discovery."""

import os
import requests
from typing import List, Dict, Any


def run_serper_queries(queries: List[Dict[str, str]], num_results: int = 10) -> List[Dict[str, Any]]:
    """
    Execute Serper searches for the given query objects.
    
    Args:
        queries: List of query objects from build_palette_queries().
        num_results: Number of results to request per query.
    
    Returns:
        List of deduplicated job result objects.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        raise ValueError("SERPER_API_KEY environment variable not set")
    
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    all_results = []
    seen_urls = set()
    
    for query_obj in queries:
        payload = {
            "q": query_obj["query"],
            "num": num_results
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            organic_results = data.get("organic", [])
            
            for position, result in enumerate(organic_results, 1):
                result_url = result.get("link", "")
                
                # Skip if URL already seen
                if result_url in seen_urls:
                    continue
                
                seen_urls.add(result_url)
                
                job_result = {
                    "track": query_obj["track"],
                    "location": query_obj["location"],
                    "title": result.get("title", ""),
                    "url": result_url,
                    "snippet": result.get("snippet", ""),
                    "position": position
                }
                
                all_results.append(job_result)
                
        except requests.RequestException as e:
            print(f"Error executing query for {query_obj['track']} in {query_obj['location']}: {e}")
            continue
    
    # Print summary
    print(f"Executed {len(queries)} queries, collected {len(all_results)} unique job URLs")
    
    return all_results