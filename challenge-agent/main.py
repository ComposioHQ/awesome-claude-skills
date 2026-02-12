#!/usr/bin/env python3
"""
main.py - CLI entry point for Browser Challenge Agent
"""

import asyncio
import argparse
import os
import sys

from runner import ChallengeRunner


def main():
    parser = argparse.ArgumentParser(
        description='Browser Challenge Agent - Solve 30 challenges in under 5 minutes'
    )
    parser.add_argument(
        '--provider', 
        choices=['anthropic', 'openai'], 
        default='anthropic',
        help='LLM provider (default: anthropic)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help='Model name (default: claude-sonnet-4-20250514 for anthropic, gpt-4o for openai)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='Total timeout in seconds (default: 300 = 5 minutes)'
    )
    parser.add_argument(
        '--visible',
        action='store_true',
        help='Show browser window (for debugging)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Reduce output verbosity'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='run_stats.json',
        help='Output file for metrics (default: run_stats.json)'
    )
    
    args = parser.parse_args()
    
    # Validate API key
    if args.provider == 'anthropic':
        if not os.environ.get('ANTHROPIC_API_KEY'):
            print("ERROR: ANTHROPIC_API_KEY environment variable not set")
            print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
            sys.exit(1)
    elif args.provider == 'openai':
        if not os.environ.get('OPENAI_API_KEY'):
            print("ERROR: OPENAI_API_KEY environment variable not set")
            sys.exit(1)
            
    print("="*60)
    print("Browser Challenge Agent")
    print("="*60)
    print(f"Provider: {args.provider}")
    print(f"Model: {args.model or 'default'}")
    print(f"Timeout: {args.timeout}s")
    print(f"Headless: {not args.visible}")
    print("="*60)
    print()
    
    # Create runner
    runner = ChallengeRunner(
        provider=args.provider,
        model=args.model,
        headless=not args.visible,
        verbose=not args.quiet
    )
    
    # Run
    try:
        metrics = asyncio.run(runner.run(timeout=args.timeout))
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
        
    # Save and print results
    runner.save_metrics(args.output)
    runner.print_summary()
    
    # Exit code based on success
    if metrics.challenges_completed >= 30 and metrics.under_5_minutes:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
