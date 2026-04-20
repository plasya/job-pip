"""Command-line interface for job aggregation platform."""

import sys
from typing import Optional


def main(args: Optional[list[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command-line arguments. If None, uses sys.argv[1:].
    
    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    if args is None:
        args = sys.argv[1:]
    
    # TODO: Implement command parsing and dispatch
    print("Job aggregation CLI")
    return 0


if __name__ == "__main__":
    sys.exit(main())
