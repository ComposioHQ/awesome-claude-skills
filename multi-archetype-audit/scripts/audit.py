#!/usr/bin/env python3
"""
Multi-Archetype Code Audit System
=================================

A comprehensive code audit tool with 7 specialized archetypes,
each providing a unique perspective on code quality.

Usage:
    from audit import run_full_audit, run_quick_audit

    report = run_full_audit()
    print(report.to_markdown())

Author: Smash Coach AI Team
License: MIT
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
# ORCHESTRATOR
# =============================================================================


class AuditOrchestrator:
    """Orchestrates multi-archetype audits."""

    ARCHETYPES: Dict[str, Type[BaseArchetype]] = {
        "hermes": HermesAuditor,
        "ra": RaAuditor,
        "cassandra": CassandraAuditor,
        "sisyphus": SisyphusAuditor,
        "icarus": IcarusAuditor,
        "dionysus": DionysusAuditor,
        "hephaestus": HephaestusAuditor,
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
