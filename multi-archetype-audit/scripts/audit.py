#!/usr/bin/env python3
"""
Multi-Archetype Code Audit System
=================================

A comprehensive code audit tool with 19 specialized archetypes,
each providing a unique perspective on code quality.

Core 7: HERMES (API), RA (Performance), CASSANDRA (Warnings),
        SISYPHUS (DRY), ICARUS (Complexity), DIONYSUS (Robustness),
        HEPHAESTUS (Build)

Extended 12: PANDORA (Security), DELPHI (AI Safety), MIDAS (LLM Costs),
             LETHE (Data Leakage), ANTAEUS (Resilience), TIRESIAS (Testing),
             MENTOR (Docs), PROTEUS (State), MNEMOSYNE (Context),
             ARIADNE (Dependencies), JANUS (Versioning), ARGUS (Observability)

Usage:
    python audit.py /path/to/project --quick    # Fast pre-commit check
    python audit.py /path/to/project --security # Security focused
    python audit.py /path/to/project            # Full 19-archetype audit

Author: Smash Coach AI Team
License: MIT
Version: 2.0.0 (January 2026)
"""

import re
import json
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type


# =============================================================================
# CORE DATA STRUCTURES
# =============================================================================


class Severity(IntEnum):
    """Audit finding severity levels."""
    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


@dataclass
class AuditFinding:
    """A single audit finding."""
    archetype: str
    severity: Severity
    category: str
    title: str
    description: str = ""
    file_path: str = ""
    line_number: Optional[int] = None
    code_snippet: str = ""
    suggestion: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "archetype": self.archetype,
            "severity": self.severity.name,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "suggestion": self.suggestion,
        }


@dataclass
class AuditReport:
    """Report from a single archetype audit."""
    archetype: str
    timestamp: datetime
    findings: List[AuditFinding]
    summary: str
    duration_ms: float = 0


# =============================================================================
# BASE ARCHETYPE
# =============================================================================


class BaseArchetype(ABC):
    """Base class for all audit archetypes."""

    name: str = "BASE"
    description: str = "Base Archetype"
    domain: str = "general"
    icon: str = "🔍"

    def __init__(self, root_path: Optional[Path] = None):
        self.root_path = root_path or Path.cwd()

    @abstractmethod
    def audit(self) -> AuditReport:
        """Run the audit and return findings."""
        pass

    def _find_files(self, pattern: str) -> List[Path]:
        """Find files matching glob pattern, excluding common non-source directories."""
        exclude_dirs = {
            "venv", ".venv", "env", ".env",
            "node_modules", ".git", "__pycache__",
            "dist", "build", ".tox", ".pytest_cache",
            "site-packages", ".mypy_cache", ".ruff_cache",
        }

        results = []
        for path in self.root_path.rglob(pattern):
            # Skip excluded directories
            if any(excluded in path.parts for excluded in exclude_dirs):
                continue
            results.append(path)
        return results

    def _grep_files(
        self, pattern: str, glob: str = "*.py"
    ) -> List[Tuple[Path, int, str]]:
        """Search for pattern in files using ripgrep or fallback."""
        results = []
        exclude_globs = [
            "!**/venv/**", "!**/.venv/**", "!**/node_modules/**",
            "!**/__pycache__/**", "!**/site-packages/**", "!**/.git/**",
            "!**/dist/**", "!**/build/**",
        ]

        try:
            cmd = ["rg", "-n", "--no-heading", "-g", glob]
            for excl in exclude_globs:
                cmd.extend(["-g", excl])
            cmd.extend([pattern, str(self.root_path)])

            output = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            for line in output.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    file_path = Path(parts[0])
                    line_num = int(parts[1])
                    content = parts[2]
                    results.append((file_path, line_num, content))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback to Python-based search
            for file_path in self._find_files(glob):
                try:
                    content = file_path.read_text(errors="ignore")
                    for i, line in enumerate(content.split("\n"), 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            results.append((file_path, i, line))
                except Exception:
                    pass
        return results

    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file."""
        try:
            return len(file_path.read_text(errors="ignore").split("\n"))
        except Exception:
            return 0


# =============================================================================
# HERMES - API AUDITOR
# =============================================================================


class HermesAuditor(BaseArchetype):
    """API contract and protocol auditor."""

    name = "HERMES"
    description = "API Contract & Protocol Auditor"
    domain = "api"
    icon = "⚡"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        # Find endpoint naming issues
        findings.extend(self._audit_endpoint_naming())
        # Find missing auth
        findings.extend(self._audit_auth_decorators())
        # Find response model issues
        findings.extend(self._audit_response_models())

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=self._generate_summary(findings),
        )

    def _audit_endpoint_naming(self) -> List[AuditFinding]:
        findings = []
        matches = self._grep_files(r'@(app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']', "*.py")

        for file_path, line_num, line in matches:
            # Check for verbs in GET endpoints
            if ".get(" in line.lower():
                if re.search(r'["\']/(get_|fetch_|retrieve_)', line, re.IGNORECASE):
                    findings.append(AuditFinding(
                        archetype=self.name,
                        severity=Severity.LOW,
                        category="endpoint_naming",
                        title="Redundant verb in GET endpoint",
                        description="GET endpoints shouldn't have verb prefixes",
                        file_path=str(file_path),
                        line_number=line_num,
                        code_snippet=line,
                        suggestion="Use noun-based paths: /users instead of /get_users",
                    ))
        return findings

    def _audit_auth_decorators(self) -> List[AuditFinding]:
        findings = []
        admin_patterns = [r"/admin", r"/internal", r"/private", r"/manage"]

        for pattern in admin_patterns:
            matches = self._grep_files(pattern, "*.py")
            for file_path, line_num, line in matches:
                if "@" in line and ("router" in line or "app" in line):
                    findings.append(AuditFinding(
                        archetype=self.name,
                        severity=Severity.MEDIUM,
                        category="auth_check",
                        title=f"Admin endpoint - verify auth",
                        description="Ensure this endpoint has proper authentication",
                        file_path=str(file_path),
                        line_number=line_num,
                        code_snippet=line,
                    ))
        return findings

    def _audit_response_models(self) -> List[AuditFinding]:
        findings = []
        matches = self._grep_files(r"return\s+\{", "*.py")

        for file_path, line_num, line in matches[:20]:
            if "router" in str(file_path) or "api" in str(file_path):
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.INFO,
                    category="response_model",
                    title="Dict return in API endpoint",
                    description="Consider using Pydantic response models",
                    file_path=str(file_path),
                    line_number=line_num,
                ))
        return findings

    def _generate_summary(self, findings: List[AuditFinding]) -> str:
        if not findings:
            return "API contracts look solid."
        return f"Found {len(findings)} API concerns."


# =============================================================================
# RA - PERFORMANCE AUDITOR
# =============================================================================


class RaAuditor(BaseArchetype):
    """Performance and latency auditor."""

    name = "RA"
    description = "Performance & Latency Auditor"
    domain = "performance"
    icon = "☀️"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        findings.extend(self._audit_blocking_calls())
        findings.extend(self._audit_n_plus_one())
        findings.extend(self._audit_missing_cache())

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=self._generate_summary(findings),
        )

    def _audit_blocking_calls(self) -> List[AuditFinding]:
        findings = []
        blocking_patterns = [
            (r"time\.sleep\(", "time.sleep() blocks event loop"),
            (r"requests\.(get|post)", "Sync requests in potentially async context"),
            (r"open\([^)]+\)\.read\(\)", "Sync file read"),
        ]

        for pattern, desc in blocking_patterns:
            matches = self._grep_files(pattern, "*.py")
            for file_path, line_num, line in matches[:10]:
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.MEDIUM,
                    category="blocking_call",
                    title=desc,
                    file_path=str(file_path),
                    line_number=line_num,
                    code_snippet=line,
                    suggestion="Use async alternatives",
                ))
        return findings

    def _audit_n_plus_one(self) -> List[AuditFinding]:
        findings = []
        matches = self._grep_files(r"for\s+\w+\s+in\s+\w+:.*\n.*\.(query|execute|run|fetch)", "*.py")

        for file_path, line_num, line in matches[:10]:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.HIGH,
                category="n_plus_one",
                title="Potential N+1 query pattern",
                file_path=str(file_path),
                line_number=line_num,
                suggestion="Batch queries or use eager loading",
            ))
        return findings

    def _audit_missing_cache(self) -> List[AuditFinding]:
        findings = []
        expensive_patterns = [r"def (get_all|fetch_all|load_all|compute_|calculate_)"]

        for pattern in expensive_patterns:
            matches = self._grep_files(pattern, "*.py")
            for file_path, line_num, line in matches[:10]:
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.INFO,
                    category="cache_candidate",
                    title="Expensive operation - consider caching",
                    file_path=str(file_path),
                    line_number=line_num,
                    code_snippet=line,
                ))
        return findings

    def _generate_summary(self, findings: List[AuditFinding]) -> str:
        if not findings:
            return "No obvious performance issues."
        n_plus_one = sum(1 for f in findings if f.category == "n_plus_one")
        return f"Found {len(findings)} performance concerns, {n_plus_one} N+1 patterns."


# =============================================================================
# CASSANDRA - WARNING PROPHET
# =============================================================================


class CassandraAuditor(BaseArchetype):
    """Warning prophet - finds TODOs and deprecated code."""

    name = "CASSANDRA"
    description = "Warning Prophet - TODOs & Deprecated"
    domain = "warnings"
    icon = "🔮"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        findings.extend(self._audit_todos())
        findings.extend(self._audit_deprecated())
        findings.extend(self._audit_ignored_exceptions())

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=self._generate_summary(findings),
        )

    def _audit_todos(self) -> List[AuditFinding]:
        findings = []
        patterns = [
            (r"#\s*TODO:?\s*(.+)", "TODO", Severity.LOW),
            (r"#\s*FIXME:?\s*(.+)", "FIXME", Severity.MEDIUM),
            (r"#\s*HACK:?\s*(.+)", "HACK", Severity.MEDIUM),
            (r"#\s*BUG:?\s*(.+)", "BUG", Severity.HIGH),
        ]

        for pattern, marker, severity in patterns:
            matches = self._grep_files(pattern, "*.py")
            # Limit to 10 findings per marker type to avoid noise
            for file_path, line_num, line in matches[:10]:
                match = re.search(pattern, line, re.IGNORECASE)
                desc = match.group(1).strip() if match else line
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=severity,
                    category=f"todo_{marker.lower()}",
                    title=f"{marker} comment",
                    description=desc[:100],
                    file_path=str(file_path),
                    line_number=line_num,
                ))

            # If there are more, add a summary finding
            if len(matches) > 10:
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.INFO,
                    category=f"todo_{marker.lower()}_summary",
                    title=f"{len(matches) - 10} more {marker} comments",
                    description=f"Total {len(matches)} {marker} comments found",
                ))
        return findings

    def _audit_deprecated(self) -> List[AuditFinding]:
        findings = []
        patterns = [r"@deprecated", r"DEPRECATED", r"will be removed", r"do not use"]

        for pattern in patterns:
            matches = self._grep_files(pattern, "*.py")
            for file_path, line_num, line in matches[:20]:
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.MEDIUM,
                    category="deprecated",
                    title="Deprecated code marker",
                    file_path=str(file_path),
                    line_number=line_num,
                    code_snippet=line,
                ))
        return findings

    def _audit_ignored_exceptions(self) -> List[AuditFinding]:
        findings = []
        matches = self._grep_files(r"except\s*:", "*.py")

        for file_path, line_num, line in matches:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.MEDIUM,
                category="bare_except",
                title="Bare except clause",
                description="Catches all exceptions including KeyboardInterrupt",
                file_path=str(file_path),
                line_number=line_num,
                suggestion="Specify exception type: except Exception:",
            ))
        return findings

    def _generate_summary(self, findings: List[AuditFinding]) -> str:
        if not findings:
            return "No warnings found."
        todos = sum(1 for f in findings if "todo" in f.category)
        return f"Found {len(findings)} warnings: {todos} TODOs."


# =============================================================================
# SISYPHUS - DRY AUDITOR
# =============================================================================


class SisyphusAuditor(BaseArchetype):
    """DRY violations and repetition auditor."""

    name = "SISYPHUS"
    description = "Boulder Roller - DRY Violations"
    domain = "repetition"
    icon = "🪨"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        findings.extend(self._audit_duplicate_functions())
        findings.extend(self._audit_boilerplate())

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=self._generate_summary(findings),
        )

    def _audit_duplicate_functions(self) -> List[AuditFinding]:
        findings = []
        common_duplicates = [
            (r"def get_driver\(\)", "get_driver() factory"),
            (r"def get_session\(\)", "get_session() factory"),
            (r"def load_config\(\)", "load_config()"),
            (r"def setup_logging\(\)", "setup_logging()"),
        ]

        for pattern, desc in common_duplicates:
            matches = self._grep_files(pattern, "*.py")
            if len(matches) > 1:
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.MEDIUM,
                    category="duplicate_function",
                    title=f"Duplicate: {desc}",
                    description=f"Found {len(matches)} definitions",
                    file_path=str(matches[0][0]),
                    suggestion="Consolidate into single module",
                ))
        return findings

    def _audit_boilerplate(self) -> List[AuditFinding]:
        findings = []
        boilerplate = [
            (r"sys\.path\.insert\(0,", "sys.path manipulation"),
            (r"if __name__ == [\"']__main__[\"']:", "Main guard"),
        ]

        for pattern, desc in boilerplate:
            matches = self._grep_files(pattern, "*.py")
            if len(matches) > 5:
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.LOW,
                    category="boilerplate",
                    title=f"Repeated: {desc}",
                    description=f"Found {len(matches)} occurrences",
                    file_path="Multiple files",
                ))
        return findings

    def _generate_summary(self, findings: List[AuditFinding]) -> str:
        if not findings:
            return "Code follows DRY principles."
        return f"Found {len(findings)} repetition issues."


# =============================================================================
# ICARUS - COMPLEXITY AUDITOR
# =============================================================================


class IcarusAuditor(BaseArchetype):
    """Over-engineering and complexity auditor."""

    name = "ICARUS"
    description = "Sun Chaser - Over-Engineering"
    domain = "complexity"
    icon = "🌞"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        findings.extend(self._audit_god_classes())
        findings.extend(self._audit_pattern_overuse())
        findings.extend(self._audit_too_many_params())

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=self._generate_summary(findings),
        )

    def _audit_god_classes(self) -> List[AuditFinding]:
        findings = []

        for file_path in self._find_files("*.py"):
            # Skip test files and migrations
            if "test" in str(file_path).lower() or "migration" in str(file_path).lower():
                continue

            lines = self._count_lines(file_path)
            if lines > 1500:
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.HIGH,
                    category="god_object",
                    title=f"Large file: {lines} lines",
                    file_path=str(file_path),
                    suggestion="Split into smaller modules",
                ))
            elif lines > 1000:
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.MEDIUM,
                    category="large_file",
                    title=f"Growing file: {lines} lines",
                    file_path=str(file_path),
                ))
        return findings

    def _audit_pattern_overuse(self) -> List[AuditFinding]:
        findings = []
        patterns = [
            (r"class \w+Factory", "Factory"),
            (r"class \w+Builder", "Builder"),
            (r"class \w+Singleton", "Singleton"),
        ]

        total = 0
        for pattern, name in patterns:
            matches = self._grep_files(pattern, "*.py")
            total += len(matches)

        if total > 10:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.MEDIUM,
                category="pattern_overload",
                title=f"Heavy pattern usage: {total} classes",
                suggestion="KISS - patterns are tools, not requirements",
            ))
        return findings

    def _audit_too_many_params(self) -> List[AuditFinding]:
        findings = []
        matches = self._grep_files(r"def \w+\([^)]{100,}\)", "*.py")

        for file_path, line_num, line in matches[:10]:
            param_count = line.count(",") + 1
            if param_count > 7:
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.MEDIUM,
                    category="too_many_params",
                    title=f"Function with {param_count} parameters",
                    file_path=str(file_path),
                    line_number=line_num,
                    suggestion="Use config object or dataclass",
                ))
        return findings

    def _generate_summary(self, findings: List[AuditFinding]) -> str:
        if not findings:
            return "Appropriate complexity levels."
        god_objects = sum(1 for f in findings if "god" in f.category)
        return f"Found {len(findings)} complexity issues, {god_objects} god objects."


# =============================================================================
# DIONYSUS - CHAOS AUDITOR
# =============================================================================


class DionysusAuditor(BaseArchetype):
    """Error handling and edge case auditor."""

    name = "DIONYSUS"
    description = "God of Chaos - Error Handling"
    domain = "robustness"
    icon = "🍷"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        findings.extend(self._audit_injection_risks())
        findings.extend(self._audit_null_handling())
        findings.extend(self._audit_boundary_conditions())

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=self._generate_summary(findings),
        )

    def _audit_injection_risks(self) -> List[AuditFinding]:
        findings = []
        patterns = [
            # SQL injection - f-string with SELECT/INSERT/UPDATE/DELETE
            (r'f["\'].*SELECT\s+.*\{', "SQL injection risk"),
            (r'f["\'].*INSERT\s+.*\{', "SQL injection risk"),
            (r'f["\'].*UPDATE\s+.*\{', "SQL injection risk"),
            (r'f["\'].*DELETE\s+.*\{', "SQL injection risk"),
            # Cypher injection - f-string with MATCH clause (not word MATCH)
            (r'f["\'].*MATCH\s*\(.*\{', "Cypher injection risk"),
            # Format string injection
            (r'\.format\([^)]*\).*(?:SELECT|INSERT|UPDATE|DELETE)', "SQL injection via format()"),
            # Code execution (exclude torch.load which uses weights_only)
            (r'(?<!weights_only=True\s*)eval\([^)]*\)', "Code execution via eval()"),
        ]

        for pattern, desc in patterns:
            matches = self._grep_files(pattern, "*.py")
            for file_path, line_num, line in matches:
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.CRITICAL if "injection" in desc else Severity.HIGH,
                    category="injection_risk",
                    title=desc,
                    file_path=str(file_path),
                    line_number=line_num,
                    code_snippet=line[:100],
                    suggestion="Use parameterized queries",
                ))
        return findings

    def _audit_null_handling(self) -> List[AuditFinding]:
        findings = []
        patterns = [
            (r"\.get\([^,)]+\)\.", "dict.get() chained without default"),
            (r"re\.search\([^)]+\)\.", "regex result used directly"),
        ]

        for pattern, desc in patterns:
            matches = self._grep_files(pattern, "*.py")
            for file_path, line_num, line in matches[:10]:
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.MEDIUM,
                    category="null_risk",
                    title=desc,
                    file_path=str(file_path),
                    line_number=line_num,
                ))
        return findings

    def _audit_boundary_conditions(self) -> List[AuditFinding]:
        # Disabled - too noisy, low signal-to-noise ratio
        # These are common patterns that are usually safe
        return []

    def _generate_summary(self, findings: List[AuditFinding]) -> str:
        if not findings:
            return "Error handling appears comprehensive."
        critical = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        return f"Found {len(findings)} robustness issues, {critical} critical."


# =============================================================================
# HEPHAESTUS - BUILD AUDITOR
# =============================================================================


class HephaestusAuditor(BaseArchetype):
    """Build and dependencies auditor."""

    name = "HEPHAESTUS"
    description = "Divine Smith - Build & Dependencies"
    domain = "build"
    icon = "🔨"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        findings.extend(self._audit_python_deps())
        findings.extend(self._audit_node_deps())
        findings.extend(self._audit_docker())

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=self._generate_summary(findings),
        )

    def _audit_python_deps(self) -> List[AuditFinding]:
        findings = []

        for req_file in self.root_path.rglob("requirements*.txt"):
            try:
                content = req_file.read_text()
                for i, line in enumerate(content.split("\n"), 1):
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("-"):
                        if "==" not in line and ">=" not in line:
                            findings.append(AuditFinding(
                                archetype=self.name,
                                severity=Severity.MEDIUM,
                                category="unpinned_dep",
                                title=f"Unpinned: {line}",
                                file_path=str(req_file),
                                line_number=i,
                                suggestion="Pin version: package==x.y.z",
                            ))
            except Exception:
                pass
        return findings

    def _audit_node_deps(self) -> List[AuditFinding]:
        findings = []

        for pkg_file in self.root_path.rglob("package.json"):
            if "node_modules" in str(pkg_file):
                continue
            try:
                content = json.loads(pkg_file.read_text())
                deps = {**content.get("dependencies", {}), **content.get("devDependencies", {})}

                for dep, version in deps.items():
                    if version in ("*", "latest"):
                        findings.append(AuditFinding(
                            archetype=self.name,
                            severity=Severity.HIGH,
                            category="dangerous_version",
                            title=f"Dangerous: {dep}@{version}",
                            file_path=str(pkg_file),
                            suggestion="Pin to specific version",
                        ))
            except Exception:
                pass
        return findings

    def _audit_docker(self) -> List[AuditFinding]:
        findings = []

        for dockerfile in self.root_path.rglob("Dockerfile*"):
            try:
                content = dockerfile.read_text()
                for i, line in enumerate(content.split("\n"), 1):
                    if re.search(r"FROM\s+\w+:latest", line):
                        findings.append(AuditFinding(
                            archetype=self.name,
                            severity=Severity.MEDIUM,
                            category="docker_latest",
                            title="Using :latest tag",
                            file_path=str(dockerfile),
                            line_number=i,
                            suggestion="Pin to specific version",
                        ))
            except Exception:
                pass
        return findings

    def _generate_summary(self, findings: List[AuditFinding]) -> str:
        if not findings:
            return "Build configuration looks solid."
        deps = sum(1 for f in findings if "dep" in f.category or "version" in f.category)
        return f"Found {len(findings)} build issues, {deps} dependency concerns."


# =============================================================================
# PANDORA - SECURITY BOUNDARIES
# =============================================================================


class PandoraAuditor(BaseArchetype):
    """Security boundaries auditor - guards what should stay locked."""

    name = "PANDORA"
    description = "Box Guardian - Security Boundaries"
    domain = "security"
    icon = "📦"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        # Check for hardcoded secrets
        secret_patterns = [
            (r"password\s*=\s*[\"'][^\"']+[\"']", "Hardcoded password"),
            (r"api_key\s*=\s*[\"'][^\"']+[\"']", "Hardcoded API key"),
            (r"secret\s*=\s*[\"'][^\"']+[\"']", "Hardcoded secret"),
            (r"token\s*=\s*[\"'][A-Za-z0-9_-]{20,}[\"']", "Hardcoded token"),
        ]

        for pattern, desc in secret_patterns:
            matches = self._grep_files(pattern, "*.py")
            for fp, ln, line in matches[:5]:
                if "test" not in str(fp).lower() and "example" not in line.lower():
                    findings.append(AuditFinding(
                        archetype=self.name,
                        severity=Severity.CRITICAL,
                        category="hardcoded_secret",
                        title=desc,
                        file_path=str(fp),
                        line_number=ln,
                        suggestion="Use environment variables or secrets manager",
                    ))

        # Check for CORS issues
        cors_matches = self._grep_files(r"allow_origins\s*=\s*\[\s*[\"']\*[\"']", "*.py")
        for fp, ln, _ in cors_matches:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.HIGH,
                category="cors",
                title="Wildcard CORS origin",
                file_path=str(fp),
                line_number=ln,
                suggestion="Restrict to specific origins in production",
            ))

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=f"Found {len(findings)} security boundary issues." if findings else "Security boundaries intact.",
        )


# =============================================================================
# DELPHI - AI/LLM SAFETY
# =============================================================================


class DelphiAuditor(BaseArchetype):
    """AI/LLM safety auditor - oracle of safe AI patterns."""

    name = "DELPHI"
    description = "Oracle of AI - LLM Safety & Guardrails"
    domain = "ai_safety"
    icon = "🔮"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        # Check for prompt injection risks
        injection_patterns = [
            (r"f[\"'].*\{.*user.*\}.*prompt", "User input in prompt template"),
            (r"\.format\(.*user.*\).*(?:system|prompt)", "User input formatted into prompt"),
        ]

        for pattern, desc in injection_patterns:
            matches = self._grep_files(pattern, "*.py")
            for fp, ln, line in matches[:10]:
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.HIGH,
                    category="prompt_injection",
                    title=desc,
                    file_path=str(fp),
                    line_number=ln,
                    suggestion="Sanitize user input, use structured prompts",
                ))

        # Check for missing output validation
        llm_calls = self._grep_files(r"\.generate\(|\.complete\(|\.chat\(|openai\.", "*.py")
        validators = self._grep_files(r"validate.*response|response.*valid|parse.*json", "*.py")

        if len(llm_calls) > 5 and len(validators) < 2:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.MEDIUM,
                category="output_validation",
                title="LLM calls without output validation",
                description=f"{len(llm_calls)} LLM calls, {len(validators)} validators",
                suggestion="Validate LLM outputs before using in application",
            ))

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=f"Found {len(findings)} AI safety concerns." if findings else "AI patterns look safe.",
        )


# =============================================================================
# MIDAS - LLM COST OPTIMIZATION
# =============================================================================


class MidasAuditor(BaseArchetype):
    """LLM cost optimization auditor - turns tokens into gold."""

    name = "MIDAS"
    description = "Golden Touch - LLM Cost Optimization"
    domain = "cost"
    icon = "💰"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        # Check for caching patterns on LLM calls
        llm_patterns = self._grep_files(r"openai|anthropic|\.generate\(|\.complete\(", "*.py")
        cache_patterns = self._grep_files(r"@cache|@lru_cache|redis\.get|cache\.get", "*.py")

        if len(llm_patterns) > 10 and len(cache_patterns) < 3:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.MEDIUM,
                category="missing_cache",
                title="LLM calls without caching",
                description=f"Found {len(llm_patterns)} LLM patterns, {len(cache_patterns)} cache patterns",
                suggestion="Cache deterministic LLM responses to reduce costs",
            ))

        # Check for model selection
        expensive_models = self._grep_files(r"gpt-4|claude-3-opus|gemini-ultra", "*.py")
        for fp, ln, line in expensive_models[:5]:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.INFO,
                category="model_cost",
                title="Premium model usage",
                file_path=str(fp),
                line_number=ln,
                suggestion="Consider cheaper models for simple tasks",
            ))

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=f"Found {len(findings)} cost optimization opportunities." if findings else "Cost patterns look good.",
        )


# =============================================================================
# LETHE - DATA LEAKAGE
# =============================================================================


class LetheAuditor(BaseArchetype):
    """Data leakage auditor - ensures secrets stay forgotten."""

    name = "LETHE"
    description = "River of Forgetting - Data Leakage Prevention"
    domain = "data_safety"
    icon = "🌊"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        # Check for sensitive data in logs
        log_sensitive = [
            (r"log.*password|password.*log", "Password in logs"),
            (r"print\(.*password|print\(.*secret", "Sensitive data in print"),
            (r"logger\.\w+\(.*(?:api_key|secret|token|password)", "Sensitive data logged"),
        ]

        for pattern, desc in log_sensitive:
            matches = self._grep_files(pattern, "*.py")
            for fp, ln, _ in matches[:5]:
                if "test" not in str(fp).lower():
                    findings.append(AuditFinding(
                        archetype=self.name,
                        severity=Severity.HIGH,
                        category="data_leak",
                        title=desc,
                        file_path=str(fp),
                        line_number=ln,
                        suggestion="Redact sensitive data before logging",
                    ))

        # Check for debug mode in production code
        debug_matches = self._grep_files(r"DEBUG\s*=\s*True|debug\s*=\s*True", "*.py")
        for fp, ln, _ in debug_matches:
            if "test" not in str(fp).lower() and "setting" in str(fp).lower():
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.MEDIUM,
                    category="debug_mode",
                    title="Debug mode enabled",
                    file_path=str(fp),
                    line_number=ln,
                    suggestion="Use environment variable for debug setting",
                ))

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=f"Found {len(findings)} data leakage risks." if findings else "Data stays private.",
        )


# =============================================================================
# ANTAEUS - RESILIENCE
# =============================================================================


class AntaeusAuditor(BaseArchetype):
    """Resilience auditor - strength through fault tolerance."""

    name = "ANTAEUS"
    description = "Giant of Resilience - Fault Tolerance"
    domain = "resilience"
    icon = "🏔️"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        # Check for retry patterns
        external_calls = self._grep_files(r"requests\.|httpx\.|aiohttp\.", "*.py")
        retry_patterns = self._grep_files(r"@retry|tenacity|backoff|max_retries", "*.py")

        if len(external_calls) > 10 and len(retry_patterns) < 2:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.MEDIUM,
                category="missing_retry",
                title="HTTP calls without retry logic",
                description=f"{len(external_calls)} HTTP calls, {len(retry_patterns)} retry patterns",
                suggestion="Add retry with exponential backoff for external calls",
            ))

        # Check for timeout usage
        timeout_patterns = self._grep_files(r"timeout\s*=", "*.py")
        if len(external_calls) > 10 and len(timeout_patterns) < len(external_calls) // 2:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.MEDIUM,
                category="missing_timeout",
                title="External calls may lack timeouts",
                suggestion="Always set timeouts on external HTTP calls",
            ))

        # Check for circuit breaker
        circuit_breaker = self._grep_files(r"circuit.*breaker|CircuitBreaker|pybreaker", "*.py")
        if len(external_calls) > 20 and not circuit_breaker:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.LOW,
                category="circuit_breaker",
                title="No circuit breaker pattern",
                suggestion="Consider circuit breaker for cascading failure prevention",
            ))

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=f"Found {len(findings)} resilience gaps." if findings else "Good fault tolerance.",
        )


# =============================================================================
# TIRESIAS - TESTING
# =============================================================================


class TiresiasAuditor(BaseArchetype):
    """Testing blind spots auditor - sees what tests miss."""

    name = "TIRESIAS"
    description = "Blind Prophet - Testing Blind Spots"
    domain = "testing"
    icon = "👁️‍🗨️"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        # Count source files vs test files
        py_files = [f for f in self._find_files("*.py") if "test" not in str(f).lower()]
        test_files = [f for f in self._find_files("test_*.py")]
        test_files.extend(self._find_files("*_test.py"))

        ratio = len(test_files) / len(py_files) if py_files else 0

        if ratio < 0.1:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.HIGH,
                category="test_coverage",
                title=f"Low test file ratio: {ratio:.1%}",
                description=f"{len(test_files)} test files for {len(py_files)} source files",
                suggestion="Aim for at least 1 test file per module",
            ))
        elif ratio < 0.3:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.MEDIUM,
                category="test_coverage",
                title=f"Moderate test coverage: {ratio:.1%}",
                description=f"{len(test_files)} test files for {len(py_files)} source files",
            ))

        # Check for assertion usage in tests
        assertions = self._grep_files(r"assert\s|self\.assert|pytest\.raises", "test_*.py")
        if test_files and len(assertions) < len(test_files) * 2:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.LOW,
                category="weak_assertions",
                title="Tests may have weak assertions",
                suggestion="Ensure each test has meaningful assertions",
            ))

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=f"Found {len(findings)} testing gaps." if findings else "Good test coverage.",
        )


# =============================================================================
# MENTOR - DOCUMENTATION
# =============================================================================


class MentorAuditor(BaseArchetype):
    """Documentation quality auditor - teaches through examples."""

    name = "MENTOR"
    description = "Wise Teacher - Documentation Quality"
    domain = "documentation"
    icon = "📚"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        # Check for docstrings
        functions = self._grep_files(r"^\s*def \w+\(", "*.py")
        docstrings = self._grep_files(r'^\s*""".*"""$|^\s*"""', "*.py")

        if len(functions) > 50 and len(docstrings) < len(functions) * 0.3:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.MEDIUM,
                category="docstrings",
                title="Low docstring coverage",
                description=f"{len(docstrings)} docstrings for {len(functions)} functions",
                suggestion="Add docstrings to public functions and classes",
            ))

        # Check for type hints
        typed_funcs = self._grep_files(r"def \w+\([^)]*:.*\)\s*->", "*.py")
        if len(functions) > 50:
            ratio = len(typed_funcs) / len(functions)
            if ratio < 0.5:
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.LOW,
                    category="type_hints",
                    title=f"Type hint coverage: {ratio:.0%}",
                    suggestion="Add type hints for better documentation",
                ))

        # Check for README
        readme_files = list(self.root_path.glob("README*"))
        if not readme_files:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.LOW,
                category="readme",
                title="No README file found",
                suggestion="Add README.md with project overview",
            ))

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=f"Found {len(findings)} documentation issues." if findings else "Documentation looks good.",
        )


# =============================================================================
# PROTEUS - STATE MANAGEMENT
# =============================================================================


class ProteusAuditor(BaseArchetype):
    """State management auditor - tamer of the shape-shifter."""

    name = "PROTEUS"
    description = "Shape-Shifter - State Management"
    domain = "state"
    icon = "🌀"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        # Check for mutable default arguments
        mutable_defaults = self._grep_files(r"def \w+\([^)]*=\s*\[\]|def \w+\([^)]*=\s*\{\}", "*.py")
        for fp, ln, line in mutable_defaults[:5]:
            if "test" not in str(fp).lower():
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.MEDIUM,
                    category="mutable_default",
                    title="Mutable default argument",
                    file_path=str(fp),
                    line_number=ln,
                    suggestion="Use None and initialize in function body",
                ))

        # Check for global mutable state
        global_state = self._grep_files(r"^[A-Z_]+\s*=\s*\[\]|^[A-Z_]+\s*=\s*\{\}", "*.py")
        if len(global_state) > 10:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.MEDIUM,
                category="global_state",
                title=f"{len(global_state)} global mutable containers",
                suggestion="Consider using singletons with reset functions",
            ))

        # Check for thread safety
        threading_use = self._grep_files(r"threading\.|Thread\(", "*.py")
        lock_use = self._grep_files(r"Lock\(\)|RLock\(\)|asyncio\.Lock", "*.py")
        if len(threading_use) > 5 and len(lock_use) < 2:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.MEDIUM,
                category="thread_safety",
                title="Threading without locks",
                suggestion="Use locks for shared mutable state",
            ))

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=f"Found {len(findings)} state issues." if findings else "State management looks solid.",
        )


# =============================================================================
# MNEMOSYNE - CONTEXT MANAGEMENT
# =============================================================================


class MnemosyneAuditor(BaseArchetype):
    """Context management auditor - memory guardian."""

    name = "MNEMOSYNE"
    description = "Memory Titaness - Context Propagation"
    domain = "context"
    icon = "🧠"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        # Check for context propagation patterns
        context_patterns = self._grep_files(r"ContextVar\(|correlation_id|request_id|trace_id", "*.py")

        if not context_patterns:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.MEDIUM,
                category="context_missing",
                title="No context propagation patterns",
                suggestion="Add request/correlation IDs for tracing",
            ))

        # Check for logging with context
        logs = self._grep_files(r"logger\.\w+\(", "*.py")
        logs_with_extra = self._grep_files(r"logger\.\w+\(.*extra\s*=", "*.py")

        if len(logs) > 50 and len(logs_with_extra) < 5:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.LOW,
                category="logging_context",
                title="Logs lack context",
                description=f"{len(logs)} log calls, {len(logs_with_extra)} with extra",
                suggestion="Add request context to log messages",
            ))

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=f"Found {len(findings)} context issues." if findings else "Context management looks good.",
        )


# =============================================================================
# ARIADNE - DEPENDENCY MANAGEMENT
# =============================================================================


class AriadneAuditor(BaseArchetype):
    """Dependency management auditor - thread through the labyrinth."""

    name = "ARIADNE"
    description = "Labyrinth Navigator - Dependencies"
    domain = "dependencies"
    icon = "🧵"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        # Check requirements.txt for unpinned deps
        for req_file in self.root_path.rglob("requirements*.txt"):
            if "venv" in str(req_file):
                continue
            try:
                content = req_file.read_text()
                unpinned = 0
                for line in content.split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("-"):
                        if "==" not in line and ">=" not in line:
                            unpinned += 1
                if unpinned > 5:
                    findings.append(AuditFinding(
                        archetype=self.name,
                        severity=Severity.MEDIUM,
                        category="unpinned",
                        title=f"{unpinned} unpinned dependencies",
                        file_path=str(req_file),
                        suggestion="Pin versions for reproducible builds",
                    ))
            except Exception:
                pass

        # Check for circular import indicators
        type_checking = self._grep_files(r"if TYPE_CHECKING:", "*.py")
        if len(type_checking) > 10:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.INFO,
                category="circular_imports",
                title=f"{len(type_checking)} TYPE_CHECKING usages",
                suggestion="Review for potential circular import issues",
            ))

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=f"Found {len(findings)} dependency issues." if findings else "Dependencies look clean.",
        )


# =============================================================================
# JANUS - VERSIONING
# =============================================================================


class JanusAuditor(BaseArchetype):
    """Versioning auditor - guardian of transitions."""

    name = "JANUS"
    description = "Two-Faced Guardian - Versioning"
    domain = "versioning"
    icon = "🚪"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        # Check for API versioning
        api_versions = self._grep_files(r"/api/v\d+/|/v\d+/", "*.py")
        if api_versions:
            v1 = len(self._grep_files(r"/api/v1/", "*.py"))
            v2 = len(self._grep_files(r"/api/v2/", "*.py"))
            if v1 > 0 and v2 > 0:
                findings.append(AuditFinding(
                    archetype=self.name,
                    severity=Severity.INFO,
                    category="api_versions",
                    title=f"Multiple API versions: v1={v1}, v2={v2}",
                    suggestion="Document migration path between versions",
                ))

        # Check for deprecation markers
        deprecated = self._grep_files(r"@deprecated|DEPRECATED|will be removed", "*.py")
        if deprecated:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.INFO,
                category="deprecation",
                title=f"{len(deprecated)} deprecation markers",
                suggestion="Ensure deprecated items have sunset timeline",
            ))

        # Check for __version__
        version_def = self._grep_files(r"__version__\s*=", "*.py")
        if not version_def:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.LOW,
                category="version_constant",
                title="No __version__ defined",
                suggestion="Add __version__ to main __init__.py",
            ))

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=f"Found {len(findings)} versioning notes." if findings else "Versioning looks good.",
        )


# =============================================================================
# ARGUS - OBSERVABILITY
# =============================================================================


class ArgusAuditor(BaseArchetype):
    """Observability auditor - the all-seeing eye."""

    name = "ARGUS"
    description = "All-Seeing - Observability"
    domain = "observability"
    icon = "👁️"

    def audit(self) -> AuditReport:
        start_time = time.time()
        findings: List[AuditFinding] = []

        # Check for structured logging
        structlog = self._grep_files(r"structlog|JsonFormatter|json.*log", "*.py")
        if not structlog:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.MEDIUM,
                category="structured_logging",
                title="No structured logging detected",
                suggestion="Use structlog or JSON formatter for log aggregation",
            ))

        # Check for health endpoints
        health = self._grep_files(r"/health|/ready|/live|HealthCheck", "*.py")
        if not health:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.LOW,
                category="health_check",
                title="No health check endpoints",
                suggestion="Add /health endpoint for k8s probes",
            ))

        # Check for metrics
        metrics = self._grep_files(r"prometheus|Counter\(|Gauge\(|Histogram\(", "*.py")
        if not metrics:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.MEDIUM,
                category="metrics",
                title="No metrics instrumentation",
                suggestion="Add prometheus_client for /metrics endpoint",
            ))

        # Check for tracing
        tracing = self._grep_files(r"opentelemetry|langfuse|jaeger|trace_id", "*.py")
        if not tracing:
            findings.append(AuditFinding(
                archetype=self.name,
                severity=Severity.LOW,
                category="tracing",
                title="No distributed tracing",
                suggestion="Add OpenTelemetry for request tracing",
            ))

        return AuditReport(
            archetype=self.name,
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            findings=findings,
            summary=f"Found {len(findings)} observability gaps." if findings else "Good observability.",
        )


# =============================================================================
# ORCHESTRATOR
# =============================================================================


class AuditOrchestrator:
    """Orchestrates multi-archetype audits."""

    ARCHETYPES: Dict[str, Type[BaseArchetype]] = {
        # Core 7 (Greek Mythology)
        "hermes": HermesAuditor,
        "ra": RaAuditor,
        "cassandra": CassandraAuditor,
        "sisyphus": SisyphusAuditor,
        "icarus": IcarusAuditor,
        "dionysus": DionysusAuditor,
        "hephaestus": HephaestusAuditor,
        # Extended 12 (Security, AI, Resilience, Quality)
        "pandora": PandoraAuditor,
        "delphi": DelphiAuditor,
        "midas": MidasAuditor,
        "lethe": LetheAuditor,
        "antaeus": AntaeusAuditor,
        "tiresias": TiresiasAuditor,
        "mentor": MentorAuditor,
        "proteus": ProteusAuditor,
        "mnemosyne": MnemosyneAuditor,
        "ariadne": AriadneAuditor,
        "janus": JanusAuditor,
        "argus": ArgusAuditor,
    }

    def __init__(self, root_path: Optional[Path] = None):
        self.root_path = root_path or Path.cwd()

    def list_archetypes(self) -> List[Dict[str, str]]:
        """List all available archetypes."""
        result = []
        for name, cls in self.ARCHETYPES.items():
            auditor = cls(self.root_path)
            result.append({
                "name": auditor.name,
                "key": name,
                "description": auditor.description,
                "domain": auditor.domain,
                "icon": auditor.icon,
            })
        return result

    def run_audit(
        self,
        archetypes: Optional[List[str]] = None,
        severity_threshold: Severity = Severity.INFO,
    ) -> "UnifiedAuditReport":
        """Run audit with selected archetypes."""
        start_time = time.time()

        if archetypes is None:
            archetypes = list(self.ARCHETYPES.keys())

        reports: List[AuditReport] = []
        for key in archetypes:
            if key.lower() not in self.ARCHETYPES:
                continue
            auditor = self.ARCHETYPES[key.lower()](self.root_path)
            try:
                reports.append(auditor.audit())
            except Exception as e:
                reports.append(AuditReport(
                    archetype=auditor.name,
                    timestamp=datetime.now(),
                    findings=[],
                    summary=f"Failed: {e}",
                ))

        all_findings = []
        for report in reports:
            for finding in report.findings:
                if finding.severity.value >= severity_threshold.value:
                    all_findings.append(finding)

        all_findings.sort(key=lambda f: f.severity.value, reverse=True)

        return UnifiedAuditReport(
            timestamp=datetime.now(),
            duration_ms=(time.time() - start_time) * 1000,
            archetypes_run=[r.archetype for r in reports],
            individual_reports=reports,
            findings=all_findings,
        )

    def run_quick_audit(self) -> "UnifiedAuditReport":
        return self.run_audit(["hermes", "dionysus", "hephaestus"], Severity.MEDIUM)

    def run_full_audit(self) -> "UnifiedAuditReport":
        return self.run_audit(None, Severity.INFO)

    def run_security_audit(self) -> "UnifiedAuditReport":
        return self.run_audit(["dionysus", "hephaestus", "hermes"], Severity.LOW)

    def run_performance_audit(self) -> "UnifiedAuditReport":
        return self.run_audit(["ra", "icarus"], Severity.LOW)


@dataclass
class UnifiedAuditReport:
    """Unified report from multiple archetypes."""
    timestamp: datetime
    duration_ms: float
    archetypes_run: List[str]
    individual_reports: List[AuditReport]
    findings: List[AuditFinding]

    @property
    def summary(self) -> str:
        if not self.findings:
            return f"All {len(self.archetypes_run)} archetypes report healthy code."

        by_severity = {}
        for f in self.findings:
            by_severity[f.severity.name] = by_severity.get(f.severity.name, 0) + 1

        sev_str = ", ".join(f"{c} {n.lower()}" for n, c in by_severity.items())
        return f"Found {len(self.findings)} issues. Severity: {sev_str}."

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": round(self.duration_ms, 2),
            "archetypes_run": self.archetypes_run,
            "total_findings": len(self.findings),
            "summary": self.summary,
            "findings": [f.to_dict() for f in self.findings],
        }

    def to_markdown(self) -> str:
        lines = [
            "# Multi-Archetype Audit Report",
            "",
            f"**Date**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Duration**: {self.duration_ms:.0f}ms",
            f"**Archetypes**: {', '.join(self.archetypes_run)}",
            "",
            "## Summary",
            "",
            self.summary,
            "",
            "## Archetype Reports",
            "",
        ]

        for report in self.individual_reports:
            lines.append(f"### {report.archetype}")
            lines.append(f"- {report.summary}")
            lines.append(f"- Findings: {len(report.findings)}")
            lines.append("")

        critical_high = [f for f in self.findings if f.severity.value >= Severity.HIGH.value]
        if critical_high:
            lines.append("## Critical & High Severity Findings")
            lines.append("")
            for f in critical_high[:20]:
                lines.append(f"### [{f.severity.name}] {f.title}")
                lines.append(f"**Archetype**: {f.archetype} | **Category**: {f.category}")
                if f.file_path:
                    loc = f.file_path
                    if f.line_number:
                        loc += f":{f.line_number}"
                    lines.append(f"**Location**: `{loc}`")
                if f.description:
                    lines.append(f"\n{f.description}")
                if f.suggestion:
                    lines.append(f"\n💡 {f.suggestion}")
                lines.append("")

        return "\n".join(lines)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def run_full_audit(root_path: Optional[Path] = None) -> UnifiedAuditReport:
    """Run full audit with all archetypes."""
    return AuditOrchestrator(root_path).run_full_audit()


def run_quick_audit(root_path: Optional[Path] = None) -> UnifiedAuditReport:
    """Run quick audit with essential archetypes."""
    return AuditOrchestrator(root_path).run_quick_audit()


def run_security_audit(root_path: Optional[Path] = None) -> UnifiedAuditReport:
    """Run security-focused audit."""
    return AuditOrchestrator(root_path).run_security_audit()


def run_performance_audit(root_path: Optional[Path] = None) -> UnifiedAuditReport:
    """Run performance-focused audit."""
    return AuditOrchestrator(root_path).run_performance_audit()


# =============================================================================
# CLI
# =============================================================================


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Archetype Code Audit")
    parser.add_argument("path", nargs="?", default=".", help="Path to audit")
    parser.add_argument("--quick", action="store_true", help="Quick audit (3 archetypes)")
    parser.add_argument("--security", action="store_true", help="Security-focused audit")
    parser.add_argument("--performance", action="store_true", help="Performance-focused audit")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--archetypes", nargs="+", help="Specific archetypes to run")

    args = parser.parse_args()
    root = Path(args.path).resolve()

    orchestrator = AuditOrchestrator(root)

    if args.quick:
        report = orchestrator.run_quick_audit()
    elif args.security:
        report = orchestrator.run_security_audit()
    elif args.performance:
        report = orchestrator.run_performance_audit()
    elif args.archetypes:
        report = orchestrator.run_audit(args.archetypes)
    else:
        report = orchestrator.run_full_audit()

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.to_markdown())
