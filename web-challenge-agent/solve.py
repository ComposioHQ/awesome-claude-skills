#!/usr/bin/env python3
"""
Main entry point for solving the Browser Navigation Challenge.
Automatically selects the best solver based on available resources.
"""

import os
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description="Browser Navigation Challenge Solver")
    parser.add_argument("--url", default="https://serene-frangipane-7fd25b.netlify.app/",
                       help="Challenge URL")
    parser.add_argument("--output", default="/tmp/challenge_results",
                       help="Output directory")
    parser.add_argument("--visible", action="store_true",
                       help="Show browser window")
    parser.add_argument("--solver", choices=["ai", "heuristic", "auto"], default="auto",
                       help="Solver type (default: auto)")
    args = parser.parse_args()
    
    # Check for API key
    has_api_key = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    # Select solver
    if args.solver == "auto":
        solver_type = "ai" if has_api_key else "heuristic"
    else:
        solver_type = args.solver
    
    print(f"Using {solver_type} solver")
    print(f"API Key available: {has_api_key}")
    
    # Set environment variables
    os.environ["CHALLENGE_URL"] = args.url
    os.environ["OUTPUT_DIR"] = args.output
    
    # Import and run appropriate solver
    if solver_type == "ai" and has_api_key:
        from ai_solver import AISolver
        solver = AISolver(headless=not args.visible)
    else:
        from final_solver import FinalSolver
        solver = FinalSolver(headless=not args.visible)
    
    report = solver.run()
    
    print(f"\n{'='*60}")
    print("FINAL REPORT")
    print(f"{'='*60}")
    print(f"Challenges Solved: {report['challenges']['solved']}/30")
    print(f"Success Rate: {report['challenges']['success_rate']}")
    print(f"Time: {report['duration_formatted']}")
    print(f"Under 5 minutes: {report['under_5_minutes']}")
    if 'tokens' in report:
        print(f"Tokens Used: {report['tokens']['total']}")
        print(f"Cost: {report['cost_usd']}")
    print(f"{'='*60}")
    
    # Exit code
    sys.exit(0 if report['challenges']['solved'] >= 25 else 1)


if __name__ == "__main__":
    main()
