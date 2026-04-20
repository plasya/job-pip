#!/usr/bin/env python3
"""Check Serper API integration with backend_java palette."""

import sys
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Note: python-dotenv not installed. Install with: pip install python-dotenv")
    print("Environment variables will be read from system environment only.")

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from search.palette_loader import load_palettes, load_locations
from search.palette_query_builder import build_palette_queries
from search.serper_runner import run_serper_queries


def main():
    """Run Serper check for backend_java palette."""
    # Check for API key
    if not os.getenv("SERPER_API_KEY"):
        print("Error: SERPER_API_KEY environment variable is not set")
        print("Please set it with: export SERPER_API_KEY=your_api_key_here")
        sys.exit(1)

    # Load configurations
    palettes = load_palettes()
    locations = load_locations()

    # Build queries for backend_java
    backend_java_config = palettes['backend_java']
    queries = build_palette_queries('backend_java', backend_java_config, locations)

    # Run first 2 queries with 5 results each
    test_queries = queries[:2]
    results = run_serper_queries(test_queries, num_results=5)

    # Print results
    print(f"\nCollected {len(results)} results from {len(test_queries)} queries")
    print("\nFirst 2 results:")
    for i, result in enumerate(results[:2], 1):
        print(f"\n{i}. Track: {result['track']}")
        print(f"   Location: {result['location']}")
        print(f"   Title: {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Position: {result['position']}")


if __name__ == "__main__":
    main()