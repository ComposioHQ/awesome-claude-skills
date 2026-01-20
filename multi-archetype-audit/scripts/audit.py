#!/usr/bin/env python3
"""
Multi-Archetype Code Audit - FENRIR + NILE Integration
=======================================================
Version: 3.2.0

A two-stage code audit:
1. FENRIR (static analysis) - Fast regex + AST scanning
2. Claude API (intelligent triage) - Filters false positives

Usage:
    python audit.py /path/to/project                    # Full audit
    python audit.py /path/to/project --fenrir-only     # Static only
    python audit.py /path/to/project --ci              # CI mode (exit codes)
    python audit.py /path/to/project --json            # JSON output

No external dependencies except optional 'anthropic' for Claude API triage.

Author: Smash Coach AI Team
License: MIT
"""

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Optional Claude API for intelligent triage
try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


# =============================================================================
# FENRIR - Static Analysis Patterns
# =============================================================================

FENRIR_PATTERNS = {
    # MORTEL - Completely silent failures
    "bare_except_pass": {
        "regex": r"except\s*:\s*\n\s*pass",
        "severity": "MORTEL",
        "archetype": "FENRIR",
        "description": "except: pass - swallows ALL exceptions silently"
    },
    "except_pass": {
        "regex": r"except\s+\w+(\s+as\s+\w+)?:\s*\n\s*pass",
        "severity": "MORTEL",
        "archetype": "FENRIR",
        "description": "except XError: pass - specific exception ignored"
    },
    "except_return_empty": {
        "regex": r"except.*:\s*\n\s*return\s*(\[\]|\{\}|None|\"\"|\'\')?\s*$",
        "severity": "MORTEL",
        "archetype": "FENRIR",
        "description": "except: return [] - failure masked by empty value"
    },

    # GRAVE - Partially visible failures
    "broad_except": {
        "regex": r"except\s+Exception(\s+as\s+\w+)?:\s*\n\s*return",
        "severity": "GRAVE",
        "archetype": "DIONYSUS",
        "description": "except Exception: return - catches too broadly"
    },
    "logging_error_in_except": {
        "regex": r"except\s+\w+.*:\s*\n\s+(?:logger|logging)\.error\(",
        "severity": "GRAVE",
        "archetype": "ARGUS",
        "description": "Use logging.exception() to include traceback"
    },

    # Security patterns
    "hardcoded_password": {
        "regex": r"(password|passwd|pwd|secret|api_key)\s*=\s*['\"][^'\"]+['\"]",
        "severity": "GRAVE",
        "archetype": "PANDORA",
        "description": "Hardcoded secret detected"
    },
    "sql_injection": {
        "regex": r"(execute|query)\s*\(\s*f['\"]|format\s*\([^)]*%",
        "severity": "GRAVE",
        "archetype": "DIONYSUS",
        "description": "Potential SQL injection via string formatting"
    },

    # Performance patterns
    "sync_in_async": {
        "regex": r"async\s+def.*:\s*\n(?:.*\n)*?\s+(?:time\.sleep|requests\.|open\()",
        "severity": "GRAVE",
        "archetype": "RA",
        "description": "Blocking call in async function"
    },

    # AI Safety patterns
    "prompt_injection": {
        "regex": r"(prompt|message)\s*=\s*f['\"].*\{.*user.*\}",
        "severity": "GRAVE",
        "archetype": "DELPHI",
        "description": "User input directly in prompt - injection risk"
    },

    # SUSPECT - Potential issues
    "bare_except": {
        "regex": r"except\s*:",
        "severity": "SUSPECT",
        "archetype": "CASSANDRA",
        "description": "Bare except - should specify exception type"
    },
    "todo_fixme": {
        "regex": r"#\s*(TODO|FIXME|XXX|HACK):",
        "severity": "SUSPECT",
        "archetype": "CASSANDRA",
        "description": "TODO/FIXME marker found"
    },
    "debug_print": {
        "regex": r"print\s*\([^)]*debug|DEBUG\s*=\s*True",
        "severity": "SUSPECT",
        "archetype": "LETHE",
        "description": "Debug code left in production"
    },

    # =========================================================================
    # HERMES - API Patterns
    # =========================================================================
    "missing_auth_decorator": {
        "regex": r"@router\.(get|post|put|delete|patch)\([^)]*\)\s*\n\s*(async\s+)?def\s+\w+\([^)]*\)(?!.*Depends\(.*auth)",
        "severity": "SUSPECT",
        "archetype": "HERMES",
        "description": "Endpoint may be missing authentication"
    },
    "api_returns_dict": {
        "regex": r"@router\.\w+\([^)]*\)\s*\n\s*(async\s+)?def\s+\w+[^:]+:\s*\n(?:.*\n)*?\s+return\s+\{",
        "severity": "SUSPECT",
        "archetype": "HERMES",
        "description": "Endpoint returns raw dict - use Pydantic response_model"
    },

    # =========================================================================
    # SISYPHUS - DRY Violations
    # =========================================================================
    "magic_number": {
        "regex": r"(?:if|while|for|return|==|!=|<|>)\s+\d{4,}\b",
        "severity": "SUSPECT",
        "archetype": "SISYPHUS",
        "description": "Magic number (4+ digits) - extract to named constant"
    },
    "copy_paste_comment": {
        "regex": r"#\s*(?:copy|paste|copie|colle|duplicate)",
        "severity": "SUSPECT",
        "archetype": "SISYPHUS",
        "description": "Copy-paste marker found - potential DRY violation"
    },

    # =========================================================================
    # ICARUS - Complexity
    # =========================================================================
    "too_many_params": {
        "regex": r"def\s+\w+\s*\([^)]{200,}\)",
        "severity": "GRAVE",
        "archetype": "ICARUS",
        "description": "Function has too many parameters (>200 chars) - simplify"
    },
    "nested_if_deep": {
        "regex": r"^\s{16,}if\s+",
        "severity": "SUSPECT",
        "archetype": "ICARUS",
        "description": "Deeply nested if (4+ levels) - consider early returns"
    },
    "god_class_methods": {
        "regex": r"class\s+\w+[^:]*:(?:.*\n){500,}",
        "severity": "SUSPECT",
        "archetype": "ICARUS",
        "description": "Class has 500+ lines - consider splitting"
    },

    # =========================================================================
    # HEPHAESTUS - Build/Dependencies
    # =========================================================================
    "unpinned_dependency": {
        "regex": r"^\s*[\w-]+\s*$",
        "severity": "SUSPECT",
        "archetype": "HEPHAESTUS",
        "description": "Unpinned dependency - specify version"
    },
    "dockerfile_root": {
        "regex": r"^USER\s+root\s*$",
        "severity": "GRAVE",
        "archetype": "HEPHAESTUS",
        "description": "Dockerfile runs as root - security risk"
    },
    "dockerfile_latest": {
        "regex": r"^FROM\s+\w+:latest",
        "severity": "SUSPECT",
        "archetype": "HEPHAESTUS",
        "description": "FROM :latest tag - pin to specific version"
    },

    # =========================================================================
    # MIDAS - LLM Costs
    # =========================================================================
    "llm_no_cache": {
        "regex": r"(?:openai|anthropic|llm)\.\w+\([^)]*\)(?!.*cache)",
        "severity": "SUSPECT",
        "archetype": "MIDAS",
        "description": "LLM call without caching - consider semantic cache"
    },
    "expensive_model": {
        "regex": r"model\s*=\s*['\"](?:gpt-4|claude-3-opus|o1-preview)['\"]",
        "severity": "SUSPECT",
        "archetype": "MIDAS",
        "description": "Expensive model used - consider cheaper alternative for task"
    },
    "llm_max_tokens_high": {
        "regex": r"max_tokens\s*=\s*(?:[4-9]\d{3}|\d{5,})",
        "severity": "SUSPECT",
        "archetype": "MIDAS",
        "description": "High max_tokens (4000+) - optimize if possible"
    },

    # =========================================================================
    # ANTAEUS - Resilience
    # =========================================================================
    "http_no_timeout": {
        "regex": r"(?:requests|httpx|aiohttp)\.\w+\([^)]*(?!timeout)[^)]*\)",
        "severity": "GRAVE",
        "archetype": "ANTAEUS",
        "description": "HTTP call without timeout - add timeout parameter"
    },
    "no_retry_pattern": {
        "regex": r"(?:requests|httpx)\.\w+\([^)]*\)(?!.*(?:retry|tenacity|backoff))",
        "severity": "SUSPECT",
        "archetype": "ANTAEUS",
        "description": "HTTP call without retry logic - consider tenacity/backoff"
    },
    "db_no_pool": {
        "regex": r"create_engine\([^)]*(?!pool)",
        "severity": "SUSPECT",
        "archetype": "ANTAEUS",
        "description": "Database without connection pooling"
    },

    # =========================================================================
    # TIRESIAS - Testing
    # =========================================================================
    "assert_true_false": {
        "regex": r"assert\s+(?:True|False)\s*$",
        "severity": "SUSPECT",
        "archetype": "TIRESIAS",
        "description": "assert True/False - meaningless assertion"
    },
    "skip_test": {
        "regex": r"@pytest\.mark\.skip|@unittest\.skip",
        "severity": "SUSPECT",
        "archetype": "TIRESIAS",
        "description": "Skipped test - fix or remove"
    },

    # =========================================================================
    # MENTOR - Documentation
    # =========================================================================
    # MENTOR patterns removed - too noisy for static analysis
    # Use ruff/pylint for docstring enforcement instead

    # =========================================================================
    # PROTEUS - State Management
    # =========================================================================
    "mutable_default": {
        "regex": r"def\s+\w+\s*\([^)]*(?:\[\]|\{\}|set\(\))\s*\)",
        "severity": "GRAVE",
        "archetype": "PROTEUS",
        "description": "Mutable default argument - use None and initialize in body"
    },
    "global_state": {
        "regex": r"^\s*global\s+\w+",
        "severity": "GRAVE",
        "archetype": "PROTEUS",
        "description": "Global state mutation - consider class or context"
    },
    "singleton_pattern": {
        "regex": r"_instance\s*=\s*None.*\n.*def\s+__new__",
        "severity": "SUSPECT",
        "archetype": "PROTEUS",
        "description": "Singleton pattern - ensure thread safety"
    },

    # =========================================================================
    # MNEMOSYNE - Context/Tracing
    # =========================================================================
    # MNEMOSYNE: log_no_context removed - too noisy
    # Only keep critical context patterns
    "missing_trace_id": {
        "regex": r"@router\.(post|put|delete)\([^)]+\).*\n.*def\s+\w+\([^)]*\)(?!.*trace|request_id)",
        "severity": "SUSPECT",
        "archetype": "MNEMOSYNE",
        "description": "Mutation endpoint without trace/request_id"
    },

    # =========================================================================
    # ARIADNE - Dependencies
    # =========================================================================
    # TYPE_CHECKING is good practice, not a smell - removed
    "star_import": {
        "regex": r"from\s+\w+\s+import\s+\*",
        "severity": "GRAVE",
        "archetype": "ARIADNE",
        "description": "Star import - explicit imports preferred"
    },
    "relative_import_deep": {
        "regex": r"from\s+\.\.\.+",
        "severity": "SUSPECT",
        "archetype": "ARIADNE",
        "description": "Deep relative import (3+ levels) - use absolute"
    },

    # =========================================================================
    # JANUS - Versioning
    # =========================================================================
    "missing_api_version": {
        "regex": r"@router\.(get|post)\(['\"]\/(?!v\d|api\/v)",
        "severity": "SUSPECT",
        "archetype": "JANUS",
        "description": "Endpoint without API version prefix"
    },
    "deprecated_no_warning": {
        "regex": r"def\s+\w+[^:]+:\s*\n\s+['\"].*deprecated.*['\"](?!.*warnings\.warn)",
        "severity": "SUSPECT",
        "archetype": "JANUS",
        "description": "Deprecated function without warnings.warn()"
    },

    # =========================================================================
    # GARM - Zombie Patterns (Dead Code) - Tuned for low noise
    # =========================================================================
    # Note: unreachable_code and dead_assignment removed - too noisy
    # Use AST-based dead code detection instead (future)
    "pass_in_function": {
        "regex": r"def\s+\w+\s*\([^)]*\)\s*(?:->.*)?:\s*\n\s+pass\s*$",
        "severity": "SUSPECT",
        "archetype": "GARM",
        "description": "Empty function with only pass - implement or remove"
    },
}


@dataclass
class Finding:
    """A single audit finding."""
    file: str
    line: int
    pattern: str
    severity: str
    archetype: str
    code: str
    description: str


# =============================================================================
# AST String Filter - Reduces false positives in example_code/docstrings
# =============================================================================

def _get_string_ranges(content: str) -> List[tuple]:
    """
    Extract all string literal byte ranges from Python code using AST.
    Returns list of (start_offset, end_offset) tuples.
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []

    ranges = []
    lines = content.split('\n')
    line_offsets = [0]
    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line) + 1)

    def get_offset(lineno: int, col: int) -> int:
        """Convert line:col to byte offset."""
        if lineno <= 0 or lineno > len(line_offsets):
            return 0
        return line_offsets[lineno - 1] + col

    for node in ast.walk(tree):
        # String constants (including docstrings, f-strings, etc.)
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                start = get_offset(node.lineno, node.col_offset)
                end = get_offset(node.end_lineno, node.end_col_offset)
                ranges.append((start, end))
        # JoinedStr (f-strings) - the whole f-string
        elif isinstance(node, ast.JoinedStr):
            if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                start = get_offset(node.lineno, node.col_offset)
                end = get_offset(node.end_lineno, node.end_col_offset)
                ranges.append((start, end))

    return ranges


def _is_in_string(pos: int, string_ranges: List[tuple]) -> bool:
    """Check if a position is inside any string literal."""
    for start, end in string_ranges:
        if start <= pos < end:
            return True
    return False


def scan_file_regex(filepath: Path) -> List[Finding]:
    """Scan a file using regex patterns with AST string filtering."""
    findings = []

    try:
        content = filepath.read_text(errors='ignore')
    except OSError:
        return findings

    # Pre-compute string ranges for false positive filtering
    string_ranges = _get_string_ranges(content)

    for pattern_name, config in FENRIR_PATTERNS.items():
        for match in re.finditer(config["regex"], content, re.MULTILINE):
            # Skip if match is inside a string literal (example_code, docstring, etc.)
            if _is_in_string(match.start(), string_ranges):
                continue

            line_num = content[:match.start()].count('\n') + 1
            findings.append(Finding(
                file=str(filepath),
                line=line_num,
                pattern=pattern_name,
                severity=config["severity"],
                archetype=config["archetype"],
                code=match.group(0).strip()[:80],
                description=config["description"]
            ))

    return findings


def scan_file_ast(filepath: Path) -> List[Finding]:
    """Scan a file using AST analysis."""
    findings = []

    try:
        content = filepath.read_text(errors='ignore')
        tree = ast.parse(content)
    except (OSError, SyntaxError):
        return findings

    for node in ast.walk(tree):
        # Empty except handler
        if isinstance(node, ast.ExceptHandler):
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                findings.append(Finding(
                    file=str(filepath),
                    line=node.lineno,
                    pattern="empty_except_handler",
                    severity="MORTEL",
                    archetype="FENRIR",
                    code="[AST] except: pass",
                    description="Empty exception handler - error completely hidden"
                ))

            # Dead exception variable
            if node.name and not _is_exception_used(node):
                findings.append(Finding(
                    file=str(filepath),
                    line=node.lineno,
                    pattern="dead_exception",
                    severity="GRAVE",
                    archetype="FENRIR",
                    code=f"[AST] except ... as {node.name}",
                    description=f"Exception '{node.name}' captured but never used"
                ))

    return findings


def _is_exception_used(handler: ast.ExceptHandler) -> bool:
    """Check if the exception variable is used in the handler body."""
    if not handler.name:
        return True  # No variable to check

    class UseFinder(ast.NodeVisitor):
        def __init__(self):
            self.found = False

        def visit_Name(self, node):
            if node.id == handler.name and isinstance(node.ctx, ast.Load):
                self.found = True
            self.generic_visit(node)

    finder = UseFinder()
    for stmt in handler.body:
        finder.visit(stmt)
        if finder.found:
            return True
    return False


def scan_directory(path: Path) -> List[Finding]:
    """Scan all Python files in a directory."""
    findings = []

    if path.is_file():
        files = [path]
    else:
        files = list(path.rglob("*.py"))
        # Exclude common non-project directories
        # Exclude common non-project directories
        files = [f for f in files if not any(
            x in str(f) for x in ["__pycache__", "venv", ".venv", "node_modules", ".git", "site-packages"]
        )]
        # Ouroboros: Exclude audit files to avoid self-detection
        files = [f for f in files if not any(
            x in str(f) for x in ["audit.py", "audit_v", "multi-archetype-audit", "archetypes/"]
        )]

    for filepath in files:
        findings.extend(scan_file_regex(filepath))
        findings.extend(scan_file_ast(filepath))

    # Deduplicate
    seen = set()
    unique = []
    for f in findings:
        key = (f.file, f.line, f.pattern)
        if key not in seen:
            seen.add(key)
            unique.append(f)

    return unique


# =============================================================================
# Claude API Triage
# =============================================================================

TRIAGE_PROMPT = """You are a code security expert. Analyze these FENRIR findings and triage them.

TRIAGE RULES:
- FALSE_POSITIVE: Pattern in strings/docstrings, defensive parsing, status checks, test fixtures
- TRUE_POSITIVE: Real issues in production code
- LOW: Acceptable but could be improved

For each finding, provide:
1. verdict: "TP" (true positive), "FP" (false positive), or "LOW"
2. reason: Short explanation (10 words max)

Return valid JSON:
{
  "triaged": [
    {"file": "...", "line": N, "verdict": "TP|FP|LOW", "reason": "..."}
  ],
  "summary": {
    "true_positives": N,
    "false_positives": N,
    "low_priority": N,
    "recommendation": "short phrase"
  }
}

FINDINGS:
"""


def triage_with_claude(findings: List[Finding]) -> dict:
    """Use Claude API to triage findings."""
    if not HAS_ANTHROPIC:
        return _fallback_triage(findings)

    client = Anthropic()

    # Limit to avoid token overflow
    limited = findings[:50]
    findings_json = [
        {"file": f.file, "line": f.line, "pattern": f.pattern,
         "severity": f.severity, "code": f.code}
        for f in limited
    ]

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": TRIAGE_PROMPT + json.dumps(findings_json, indent=2)}]
        )

        content = response.content[0].text
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        return json.loads(content.strip())

    except Exception as e:
        print(f"WARNING: Claude API error: {e}", file=sys.stderr)
        return _fallback_triage(findings)


def _fallback_triage(findings: List[Finding]) -> dict:
    """Fallback triage without Claude API."""
    return {
        "triaged": [
            {"file": f.file, "line": f.line, "verdict": f.severity, "reason": f.description[:50]}
            for f in findings
        ],
        "summary": {
            "true_positives": len([f for f in findings if f.severity == "MORTEL"]),
            "false_positives": 0,
            "low_priority": len([f for f in findings if f.severity != "MORTEL"]),
            "recommendation": "FENRIR only - manual triage recommended"
        }
    }


# =============================================================================
# Output Formatting
# =============================================================================

def format_markdown(findings: List[Finding], triage: Optional[dict]) -> str:
    """Format results as Markdown."""
    lines = [
        f"# Audit Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

    if triage:
        lines.extend([
            "## Summary",
            "",
            f"- **Raw Findings**: {len(findings)}",
            f"- **True Positives**: {triage['summary']['true_positives']}",
            f"- **False Positives**: {triage['summary']['false_positives']}",
            f"- **Low Priority**: {triage['summary']['low_priority']}",
            "",
            f"> {triage['summary']['recommendation']}",
            "",
        ])

        tp = [t for t in triage.get("triaged", []) if t["verdict"] == "TP"]
        if tp:
            lines.append("## True Positives (Action Required)")
            lines.append("")
            for t in tp:
                lines.append(f"- **{Path(t['file']).name}:{t['line']}** - {t['reason']}")
            lines.append("")
    else:
        # FENRIR only output
        by_severity = {"MORTEL": [], "GRAVE": [], "SUSPECT": []}
        for f in findings:
            by_severity.get(f.severity, []).append(f)

        lines.extend([
            "## Summary (FENRIR Only)",
            "",
            f"- **MORTEL**: {len(by_severity['MORTEL'])} (critical)",
            f"- **GRAVE**: {len(by_severity['GRAVE'])} (high)",
            f"- **SUSPECT**: {len(by_severity['SUSPECT'])} (medium)",
            "",
        ])

        for severity in ["MORTEL", "GRAVE"]:
            items = by_severity[severity]
            if items:
                lines.append(f"## {severity} Findings")
                lines.append("")
                for f in items[:20]:
                    lines.append(f"- **{Path(f.file).name}:{f.line}** [{f.archetype}] {f.description}")
                if len(items) > 20:
                    lines.append(f"- ... and {len(items) - 20} more")
                lines.append("")

    lines.append("---")
    lines.append("*Generated by multi-archetype-audit v3.2.0 (NILE Integration)*")

    return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Multi-Archetype Code Audit (FENRIR + Claude API)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python audit.py /path/to/project
    python audit.py /path/to/project --fenrir-only
    python audit.py /path/to/project --ci --threshold 0
    python audit.py /path/to/project --json
        """
    )
    parser.add_argument("path", help="File or directory to audit")
    parser.add_argument("--fenrir-only", action="store_true", help="Skip Claude API triage")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--ci", action="store_true", help="CI mode: exit 1 if issues found")
    parser.add_argument("--threshold", type=int, default=0, help="Max allowed true positives (CI mode)")
    parser.add_argument("-o", "--output", help="Output file")

    args = parser.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"ERROR: Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    # Step 1: FENRIR scan
    print(f"[1/2] FENRIR scanning {args.path}...", file=sys.stderr)
    findings = scan_directory(target)
    print(f"      Found {len(findings)} raw findings", file=sys.stderr)

    if not findings:
        print("No findings. Code is clean!", file=sys.stderr)
        if args.json:
            print(json.dumps({"findings": [], "triage": None}))
        sys.exit(0)

    # Step 2: Triage
    triage = None
    if not args.fenrir_only:
        print(f"[2/2] Claude API triage...", file=sys.stderr)
        triage = triage_with_claude(findings)
        tp_count = triage["summary"]["true_positives"]
        print(f"      {tp_count} true positives identified", file=sys.stderr)

    # Output
    if args.json:
        output = json.dumps({
            "findings": [{"file": f.file, "line": f.line, "pattern": f.pattern,
                         "severity": f.severity, "archetype": f.archetype,
                         "code": f.code, "description": f.description} for f in findings],
            "triage": triage
        }, indent=2)
    else:
        output = format_markdown(findings, triage)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Report saved to {args.output}", file=sys.stderr)
    else:
        print(output)

    # CI exit code
    if args.ci:
        if triage:
            tp_count = triage["summary"]["true_positives"]
        else:
            tp_count = len([f for f in findings if f.severity == "MORTEL"])

        if tp_count > args.threshold:
            print(f"CI FAILED: {tp_count} issues (threshold: {args.threshold})", file=sys.stderr)
            sys.exit(1)
        print(f"CI PASSED", file=sys.stderr)


if __name__ == "__main__":
    main()
