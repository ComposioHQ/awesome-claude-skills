#!/usr/bin/env python3
"""
dev-card: Git identity analyzer.

Analyzes a git repo and emits a JSON profile of the developer's patterns:
language breakdown, commit timing, message vocabulary, commit sizes, and
derived signals Claude uses to assign an archetype.

Usage:
    uv run analyze.py [path]          # analyze repo at path (default: cwd)
    uv run analyze.py [path] --debug  # pretty-print JSON to stdout
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone, timedelta


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LANG_EXTENSIONS = {
    '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
    '.jsx': 'JavaScript', '.tsx': 'TypeScript', '.java': 'Java',
    '.go': 'Go', '.rb': 'Ruby', '.php': 'PHP', '.cs': 'C#',
    '.cpp': 'C++', '.c': 'C', '.h': 'C/C++', '.swift': 'Swift',
    '.kt': 'Kotlin', '.rs': 'Rust', '.scala': 'Scala',
    '.vue': 'Vue', '.svelte': 'Svelte', '.sh': 'Shell', '.bash': 'Shell',
    '.dart': 'Dart', '.ex': 'Elixir', '.exs': 'Elixir',
    '.lua': 'Lua', '.r': 'R', '.R': 'R', '.m': 'MATLAB/ObjC',
    '.pl': 'Perl', '.groovy': 'Groovy', '.tf': 'Terraform',
    '.hs': 'Haskell', '.clj': 'Clojure', '.elm': 'Elm',
    '.ml': 'OCaml', '.fs': 'F#', '.jl': 'Julia',
}

IGNORE_DIRS = {
    'node_modules', '.git', 'vendor', '.venv', 'venv', '__pycache__',
    'dist', 'build', '.next', '.nuxt', 'coverage', '.nyc_output',
    'target', '.gradle', 'pods', 'Pods', '.cache', '.parcel-cache',
    'out', '.svelte-kit', '.turbo', 'tmp', '.tmp', '.idea', '.vscode',
}

# Commit message keyword signals
FIX_WORDS = re.compile(
    r'\b(fix|fixes|fixed|bug|patch|hotfix|repair|correct|resolve|resolved)\b',
    re.IGNORECASE,
)
FEAT_WORDS = re.compile(
    r'\b(feat|feature|add|adds|added|new|implement|implement|create|build|introduce)\b',
    re.IGNORECASE,
)
REFACTOR_WORDS = re.compile(
    r'\b(refactor|refactoring|cleanup|clean up|reorganize|restructure|rename|move|extract|simplify)\b',
    re.IGNORECASE,
)
WIP_WORDS = re.compile(
    r'\b(wip|temp|tmp|hack|test|testing|debug|draft|experimental|todo|checkpoint)\b',
    re.IGNORECASE,
)
DOCS_WORDS = re.compile(
    r'\b(docs|doc|documentation|readme|comment|comments|changelog|update docs)\b',
    re.IGNORECASE,
)
CHORE_WORDS = re.compile(
    r'\b(chore|deps|dependency|dependencies|upgrade|update|bump|lint|format|ci|cd|ci/cd|build)\b',
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_git(args: list, cwd: Path) -> str:
    try:
        result = subprocess.run(
            ['git'] + args, cwd=cwd,
            capture_output=True, text=True, timeout=30,
        )
        return result.stdout.strip()
    except Exception:
        return ''


def parse_iso(ts: str):
    """Parse git's ISO-8601 timestamp to a datetime (UTC)."""
    try:
        # git uses format like: 2024-03-15T23:42:01+05:00
        return datetime.fromisoformat(ts).astimezone(timezone.utc)
    except Exception:
        return None


def count_lines(fpath: Path) -> int:
    try:
        content = fpath.read_bytes()
        return content.count(b'\n') + 1
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# Language analysis
# ---------------------------------------------------------------------------

def analyze_languages(root: Path) -> dict:
    """Count files and approximate line counts by language via git ls-files."""
    raw = run_git(['ls-files'], root)
    if not raw:
        return {}

    by_lang: dict[str, dict] = defaultdict(lambda: {'files': 0, 'lines': 0})
    for rel_path in raw.splitlines():
        fpath = root / rel_path
        # Skip ignored dirs
        parts = set(fpath.parts)
        if parts & IGNORE_DIRS:
            continue
        ext = fpath.suffix.lower()
        lang = LANG_EXTENSIONS.get(ext)
        if lang:
            by_lang[lang]['files'] += 1
            by_lang[lang]['lines'] += count_lines(fpath)

    return dict(by_lang)


# ---------------------------------------------------------------------------
# Commit analysis
# ---------------------------------------------------------------------------

def analyze_commits(root: Path) -> dict:
    """
    Returns rich commit-level data:
    - timing distribution (hour-of-day, day-of-week)
    - message pattern ratios
    - commit size distribution
    - author info
    - streaks
    """
    # Format: hash | author name | author email | ISO timestamp | subject
    log = run_git(
        ['log', '--no-merges', '--format=%H\x1f%aN\x1f%aE\x1f%aI\x1f%s', '--numstat'],
        root
    )
    if not log:
        return {}

    # Parse commits: each commit block starts with the %H line,
    # followed by blank line, then numstat lines, then next commit.
    commits = []
    current = None
    for line in log.splitlines():
        parts = line.split('\x1f')
        if len(parts) == 5:
            # New commit header
            if current:
                commits.append(current)
            dt = parse_iso(parts[3])
            current = {
                'hash': parts[0],
                'author': parts[1].strip(),
                'email': parts[2].strip(),
                'dt': dt,
                'subject': parts[4].strip(),
                'added': 0,
                'removed': 0,
            }
        elif current and line.strip() and line[0].isdigit():
            # numstat line: "added\tremoved\tfilename"
            numparts = line.split('\t')
            if len(numparts) >= 2:
                try:
                    current['added'] += int(numparts[0])
                    current['removed'] += int(numparts[1])
                except ValueError:
                    pass  # binary files show '-'

    if current:
        commits.append(current)

    if not commits:
        return {}

    # --- Author ---
    # Use the most frequent author (handles repos with multiple contributors)
    author_count: dict[str, int] = defaultdict(int)
    for c in commits:
        author_count[c['author']] += 1
    primary_author = max(author_count, key=lambda k: author_count[k])
    primary_email = next(
        (c['email'] for c in commits if c['author'] == primary_author), ''
    )
    # Filter to primary author's commits for personal stats
    mine = [c for c in commits if c['author'] == primary_author]
    if not mine:
        mine = commits  # solo repo

    # --- Timing ---
    hour_dist = defaultdict(int)
    day_dist = defaultdict(int)
    for c in mine:
        if c['dt']:
            hour_dist[c['dt'].hour] += 1
            day_dist[c['dt'].weekday()] += 1  # 0=Mon, 6=Sun

    # --- Peak timing ---
    peak_hour = max(hour_dist, key=lambda h: hour_dist[h]) if hour_dist else 12
    peak_day_num = max(day_dist, key=lambda d: day_dist[d]) if day_dist else 1
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    peak_day = day_names[peak_day_num]

    # Night owl: ≥30% of commits between 9pm–4am
    night_hours = set(range(21, 24)) | set(range(0, 5))
    night_commits = sum(hour_dist[h] for h in night_hours)
    is_night_owl = (night_commits / max(len(mine), 1)) >= 0.30

    # Early bird: ≥30% of commits between 5am–9am
    morning_hours = set(range(5, 10))
    morning_commits = sum(hour_dist[h] for h in morning_hours)
    is_early_bird = (morning_commits / max(len(mine), 1)) >= 0.30

    # Weekend warrior: ≥40% of commits on Sat/Sun
    weekend_commits = day_dist[5] + day_dist[6]
    is_weekend_warrior = (weekend_commits / max(len(mine), 1)) >= 0.40

    # --- Commit size ---
    sizes = [c['added'] + c['removed'] for c in mine if c['added'] + c['removed'] > 0]
    avg_size = round(sum(sizes) / len(sizes)) if sizes else 0
    tiny   = sum(1 for s in sizes if s < 10)
    small  = sum(1 for s in sizes if 10 <= s < 50)
    medium = sum(1 for s in sizes if 50 <= s < 200)
    large  = sum(1 for s in sizes if 200 <= s < 500)
    epic   = sum(1 for s in sizes if s >= 500)

    # --- Message patterns ---
    total = len(mine)
    def ratio(pattern):
        return round(sum(1 for c in mine if pattern.search(c['subject'])) / max(total, 1), 3)

    fix_ratio      = ratio(FIX_WORDS)
    feat_ratio     = ratio(FEAT_WORDS)
    refactor_ratio = ratio(REFACTOR_WORDS)
    wip_ratio      = ratio(WIP_WORDS)
    docs_ratio     = ratio(DOCS_WORDS)
    chore_ratio    = ratio(CHORE_WORDS)

    # --- Repo age & streak ---
    dated = [c['dt'] for c in mine if c['dt']]
    dated_sorted = sorted(dated)
    repo_age_days = 0
    if dated_sorted:
        repo_age_days = (datetime.now(timezone.utc) - dated_sorted[0]).days

    # Streak: consecutive days (relative to most recent commit)
    commit_dates = sorted({d.date() for d in dated_sorted}, reverse=True)
    streak = 0
    if commit_dates:
        expected = commit_dates[0]
        for d in commit_dates:
            if d == expected:
                streak += 1
                expected -= timedelta(days=1)
            else:
                break

    return {
        'primary_author': primary_author,
        'primary_email': primary_email,
        'total_commits': len(mine),
        'repo_age_days': repo_age_days,
        'streak_days': streak,
        'hour_distribution': dict(sorted(hour_dist.items())),
        'day_distribution': {day_names[k]: v for k, v in day_dist.items()},
        'peak_hour': peak_hour,
        'peak_day': peak_day,
        'is_night_owl': is_night_owl,
        'is_early_bird': is_early_bird,
        'is_weekend_warrior': is_weekend_warrior,
        'avg_lines_per_commit': avg_size,
        'commit_sizes': {
            'tiny_under10': tiny,
            'small_10_50': small,
            'medium_50_200': medium,
            'large_200_500': large,
            'epic_over500': epic,
        },
        'message_patterns': {
            'fix_ratio': fix_ratio,
            'feat_ratio': feat_ratio,
            'refactor_ratio': refactor_ratio,
            'wip_ratio': wip_ratio,
            'docs_ratio': docs_ratio,
            'chore_ratio': chore_ratio,
        },
    }


# ---------------------------------------------------------------------------
# Derived signals
# ---------------------------------------------------------------------------

def derive_signals(langs: dict, commits: dict) -> dict:
    """Compute higher-level signals for archetype classification."""
    mp = commits.get('message_patterns', {})
    cs = commits.get('commit_sizes', {})

    # Language diversity
    lang_count = len(langs)
    is_polyglot = lang_count >= 4

    # Primary language
    primary_lang = ''
    if langs:
        primary_lang = max(langs, key=lambda l: langs[l].get('lines', 0))

    # Language percentages
    total_lines = sum(l.get('lines', 0) for l in langs.values())
    lang_pct = {}
    if total_lines > 0:
        for lang, data in langs.items():
            pct = round(data.get('lines', 0) / total_lines * 100, 1)
            lang_pct[lang] = pct

    # Commit style
    total_sized = sum(cs.values())
    small_ratio = ((cs.get('tiny_under10', 0) + cs.get('small_10_50', 0))
                   / max(total_sized, 1))
    epic_ratio  = cs.get('epic_over500', 0) / max(total_sized, 1)
    is_sprinter  = small_ratio >= 0.65
    is_marathon  = epic_ratio >= 0.15

    # Dominant commit intent
    dominant_intent = max(
        ['fix', 'feat', 'refactor', 'wip', 'docs', 'chore'],
        key=lambda k: mp.get(f'{k}_ratio', 0)
    )

    return {
        'primary_language': primary_lang,
        'language_count': lang_count,
        'language_percentages': dict(
            sorted(lang_pct.items(), key=lambda x: -x[1])
        ),
        'is_polyglot': is_polyglot,
        'is_sprinter': is_sprinter,
        'is_marathon_coder': is_marathon,
        'dominant_intent': dominant_intent,
        'small_commit_ratio': round(small_ratio, 3),
        'epic_commit_ratio': round(epic_ratio, 3),
    }


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def analyze(root: Path) -> dict:
    repo_name = root.name

    # Check it's a git repo
    git_dir = run_git(['rev-parse', '--git-dir'], root)
    is_git = bool(git_dir)

    langs    = analyze_languages(root) if is_git else {}
    commits  = analyze_commits(root)   if is_git else {}
    signals  = derive_signals(langs, commits) if (langs or commits) else {}

    return {
        'repo_name': repo_name,
        'repo_path': str(root),
        'analyzed_at': datetime.now(timezone.utc).isoformat(),
        'is_git_repo': is_git,
        'languages': langs,
        'commits': commits,
        'signals': signals,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args = sys.argv[1:]
    debug = '--debug' in args
    paths = [a for a in args if not a.startswith('--')]

    root = Path(paths[0]).resolve() if paths else Path.cwd()

    if not root.exists():
        print(f'Error: path not found: {root}', file=sys.stderr)
        sys.exit(1)

    data = analyze(root)

    if debug:
        print(json.dumps(data, indent=2))
    else:
        print(json.dumps(data))


if __name__ == '__main__':
    main()
