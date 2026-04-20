#!/usr/bin/env python3
"""Run end-to-end ingestion from Serper search results into SQLite."""

import argparse
import sys
import os

# Load environment variables from .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Note: python-dotenv not installed. Install with: pip install python-dotenv")
    print("Environment variables will be read from system environment only.")

# Add project root to path so src package imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.search.palette_loader import load_palettes, load_locations
from src.search.palette_query_builder import build_palette_queries
from src.search.serper_runner import run_serper_queries
from src.ingest.ingest_search_results import ingest_search_results


def main() -> None:
    parser = argparse.ArgumentParser(description='Run job ingestion from Serper search')
    parser.add_argument('--role_query', default='backend_java', help='Role query palette to use')
    parser.add_argument('--location_preset', default='major_cities', help='Location preset to use')
    parser.add_argument('--query_limit', type=int, default=4, help='Maximum number of queries to run')
    parser.add_argument('--num_results', type=int, default=10, help='Number of results per query')
    args = parser.parse_args()

    palettes = load_palettes()
    locations = load_locations()

    if args.role_query not in palettes:
        print(f"Error: Role query '{args.role_query}' not found in palettes")
        print(f"Available: {list(palettes.keys())}")
        return

    if args.location_preset not in locations:
        print(f"Error: Location preset '{args.location_preset}' not found")
        print(f"Available: {list(locations.keys())}")
        return

    role_config = palettes[args.role_query]
    location_list = locations[args.location_preset]

    print(f"Using role query: {args.role_query}")
    print(f"Using location preset: {args.location_preset} ({len(location_list)} locations)")
    print(f"Query limit: {args.query_limit}, Results per query: {args.num_results}")

    # Create temporary locations dict with just the selected preset
    temp_locations = {args.location_preset: location_list}
    queries = build_palette_queries(args.role_query, role_config, temp_locations)

    search_results = run_serper_queries(queries[:args.query_limit], num_results=args.num_results)

    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'jobs.db')
    summary = ingest_search_results(db_path, search_results)

    print('Ingestion summary:')
    for key, value in summary.items():
        print(f'  {key}: {value}')


if __name__ == '__main__':
    main()
