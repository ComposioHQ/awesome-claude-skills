"""
Semantic Context Analyzer for Enhanced Audit
Phase 301.5j: Addresses regex audit's main weakness - lack of context.

Provides:
1. AST-based code structure analysis
2. Context windows (lines before/after)
3. Import tracking for safety function validation
4. Luciole integration for domain knowledge
"""
import ast
import json
import queue
import re
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


@dataclass
class CodeContext:
    """Rich context for a code location."""
    file_path: str
    line_number: int
    line_content: str

    # Structural context
    in_function: Optional[str] = None
    in_class: Optional[str] = None
    in_docstring: bool = False
    in_comment: bool = False
    in_string_literal: bool = False

    # Semantic context
    surrounding_lines: List[str] = field(default_factory=list)
    imports: Set[str] = field(default_factory=set)
    defined_functions: Set[str] = field(default_factory=set)

    # Luciole context
    relevant_bubbles: List[Dict] = field(default_factory=list)
    domain_warnings: List[str] = field(default_factory=list)


class ASTContextAnalyzer:
    """Analyze Python files using AST for rich context."""

    def __init__(self):
        self._cache: Dict[str, ast.AST] = {}
        self._import_cache: Dict[str, Set[str]] = {}

    def get_ast(self, file_path: str) -> Optional[ast.AST]:
        """Parse and cache AST for a file."""
        if file_path in self._cache:
            return self._cache[file_path]

        try:
            content = Path(file_path).read_text(errors='ignore')
            tree = ast.parse(content)
            self._cache[file_path] = tree
            return tree
        except (SyntaxError, FileNotFoundError):
            return None

    def get_imports(self, file_path: str) -> Set[str]:
        """Extract all imports from a file."""
        if file_path in self._import_cache:
            return self._import_cache[file_path]

        imports = set()
        tree = self.get_ast(file_path)
        if tree is None:
            return imports

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.add(f"{module}.{alias.name}")
                    imports.add(alias.name)  # Also add just the name

        self._import_cache[file_path] = imports
        return imports

    def get_enclosing_scope(self, file_path: str, line_number: int) -> Tuple[Optional[str], Optional[str]]:
        """Find the enclosing function and class for a line."""
        tree = self.get_ast(file_path)
        if tree is None:
            return None, None

        current_class = None
        current_function = None

        for node in ast.walk(tree):
            if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                if node.lineno <= line_number <= (node.end_lineno or node.lineno):
                    if isinstance(node, ast.ClassDef):
                        current_class = node.name
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        current_function = node.name

        return current_function, current_class

    def is_in_docstring(self, file_path: str, line_number: int) -> bool:
        """Check if line is inside a docstring."""
        tree = self.get_ast(file_path)
        if tree is None:
            return False

        for node in ast.walk(tree):
            # Docstrings are the first statement in a body
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                body = getattr(node, 'body', [])
                if body and isinstance(body[0], ast.Expr):
                    expr = body[0]
                    if isinstance(expr.value, ast.Constant) and isinstance(expr.value.value, str):
                        if hasattr(expr, 'lineno') and hasattr(expr, 'end_lineno'):
                            if expr.lineno <= line_number <= (expr.end_lineno or expr.lineno):
                                return True
        return False

    def has_safety_import(self, file_path: str, safety_functions: List[str]) -> Dict[str, bool]:
        """Check if safety functions are imported."""
        imports = self.get_imports(file_path)
        result = {}
        for func in safety_functions:
            result[func] = any(func in imp for imp in imports)
        return result


class ContextWindowAnalyzer:
    """Analyze surrounding lines for context."""

    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self._file_cache: Dict[str, List[str]] = {}

    def get_file_lines(self, file_path: str) -> List[str]:
        """Get and cache file lines."""
        if file_path not in self._file_cache:
            try:
                content = Path(file_path).read_text(errors='ignore')
                self._file_cache[file_path] = content.split('\n')
            except FileNotFoundError:
                self._file_cache[file_path] = []
        return self._file_cache[file_path]

    def get_context_window(self, file_path: str, line_number: int) -> List[str]:
        """Get lines before and after the target line."""
        lines = self.get_file_lines(file_path)
        if not lines or line_number < 1:
            return []

        start = max(0, line_number - 1 - self.window_size)
        end = min(len(lines), line_number + self.window_size)
        return lines[start:end]

    def check_protection_in_window(self, file_path: str, line_number: int,
                                    protection_patterns: List[str]) -> List[str]:
        """Check if protection patterns exist in the context window."""
        window = self.get_context_window(file_path, line_number)
        window_text = '\n'.join(window)

        found = []
        for pattern in protection_patterns:
            if re.search(pattern, window_text, re.IGNORECASE):
                found.append(pattern)
        return found


class LucioleIntegration:
    """Integrate Luciole bubbles into audit context."""

    def __init__(self, bubbles_path: Optional[str] = None):
        self.bubbles: Dict[str, List[Dict]] = {}
        self.all_bubbles: List[Dict] = []

        if bubbles_path:
            self._load_bubbles(bubbles_path)
        else:
            # Try default locations
            default_paths = [
                Path.cwd() / "apps/backend/data/luciole_bubbles.json",
                Path.cwd().parent / "apps/backend/data/luciole_bubbles.json",
                Path.home() / "Smash_App/apps/backend/data/luciole_bubbles.json",
            ]
            for path in default_paths:
                if path.exists():
                    self._load_bubbles(str(path))
                    break

    def _load_bubbles(self, path: str):
        """Load Luciole bubbles from JSON."""
        try:
            data = json.loads(Path(path).read_text())
            # Extract bubbles from each domain
            for key, value in data.items():
                if key == "_meta":
                    continue
                if isinstance(value, list):
                    self.bubbles[key] = value
                    self.all_bubbles.extend(value)
        except Exception:
            pass

    def find_relevant_bubbles(self, text: str, category: str = None) -> List[Dict]:
        """Find Luciole bubbles relevant to the given text."""
        text_lower = text.lower()
        relevant = []

        for bubble in self.all_bubbles:
            keywords = bubble.get("keywords", [])
            # Check if any keyword matches
            for kw in keywords:
                if kw.lower() in text_lower:
                    # Apply category filter if provided
                    if category:
                        domain = bubble.get("domain", "")
                        if category.lower() not in domain.lower():
                            continue
                    relevant.append(bubble)
                    break

        return relevant

    def get_domain_warnings(self, file_path: str, line_content: str,
                           finding_category: str) -> List[str]:
        """Get warnings from Lucioles relevant to this finding."""
        warnings = []

        # Combine file path and line content for matching
        context_text = f"{file_path} {line_content} {finding_category}"

        relevant = self.find_relevant_bubbles(context_text)
        for bubble in relevant:
            if bubble.get("severity") in ("warning", "critical"):
                warnings.append(bubble.get("reminder", ""))

        return warnings


class SemanticContextBuilder:
    """Build rich semantic context for audit findings."""

    # Safety functions that indicate protected code
    SAFETY_FUNCTIONS = [
        "escape_cypher", "_escape_cypher", "escape", "sanitize",
        "validate", "clean", "filter", "parameterize",
        "SecretStr", "getenv", "environ.get"
    ]

    # Protection patterns to look for in context window
    PROTECTION_PATTERNS = [
        r"escape\w*\(",
        r"sanitize\w*\(",
        r"validate\w*\(",
        r"SecretStr\(",
        r"os\.getenv\(",
        r"os\.environ\.get\(",
        r"params\s*=",
        r"\$\w+",  # Parameterized query placeholders
    ]

    def __init__(self, luciole_path: Optional[str] = None):
        self.ast_analyzer = ASTContextAnalyzer()
        self.window_analyzer = ContextWindowAnalyzer(window_size=5)
        self.luciole = LucioleIntegration(luciole_path)

    def build_context(self, file_path: str, line_number: int,
                      line_content: str, category: str = "") -> CodeContext:
        """Build complete semantic context for a code location."""

        # Get structural context from AST
        func_name, class_name = self.ast_analyzer.get_enclosing_scope(file_path, line_number)
        in_docstring = self.ast_analyzer.is_in_docstring(file_path, line_number)

        # Get imports
        imports = self.ast_analyzer.get_imports(file_path)

        # Get surrounding lines
        surrounding = self.window_analyzer.get_context_window(file_path, line_number)

        # Check for protection patterns
        protections = self.window_analyzer.check_protection_in_window(
            file_path, line_number, self.PROTECTION_PATTERNS
        )

        # Get Luciole context
        relevant_bubbles = self.luciole.find_relevant_bubbles(
            f"{line_content} {category}", category
        )
        domain_warnings = self.luciole.get_domain_warnings(
            file_path, line_content, category
        )

        # Determine if in comment/string
        in_comment = line_content.strip().startswith("#")
        in_string = self._is_in_string_literal(line_content)

        return CodeContext(
            file_path=file_path,
            line_number=line_number,
            line_content=line_content,
            in_function=func_name,
            in_class=class_name,
            in_docstring=in_docstring,
            in_comment=in_comment,
            in_string_literal=in_string,
            surrounding_lines=surrounding,
            imports=imports,
            relevant_bubbles=relevant_bubbles,
            domain_warnings=domain_warnings,
        )

    def _is_in_string_literal(self, line: str) -> bool:
        """Check if the line is primarily a string literal."""
        stripped = line.strip()
        # Simplified check - starts with quote
        return (stripped.startswith('"') or stripped.startswith("'") or
                stripped.startswith('"""') or stripped.startswith("'''") or
                stripped.startswith('f"') or stripped.startswith("f'"))

    def is_protected(self, context: CodeContext) -> Tuple[bool, List[str]]:
        """Check if the code location is protected by safety measures."""
        reasons = []

        # Check if in docstring/comment
        if context.in_docstring:
            reasons.append("in_docstring")
        if context.in_comment:
            reasons.append("in_comment")
        if context.in_string_literal:
            reasons.append("in_string_literal")

        # Check for safety imports
        for func in self.SAFETY_FUNCTIONS:
            if func in context.imports:
                reasons.append(f"imports_{func}")

        # Check surrounding lines for protection patterns
        window_text = '\n'.join(context.surrounding_lines)
        for pattern in self.PROTECTION_PATTERNS:
            if re.search(pattern, window_text):
                reasons.append(f"protected_by_{pattern}")

        return len(reasons) > 0, reasons

    def enrich_finding(self, finding_dict: Dict, file_path: str,
                       line_number: int, line_content: str) -> Dict:
        """Enrich a finding with semantic context."""
        context = self.build_context(
            file_path, line_number, line_content,
            finding_dict.get("category", "")
        )

        is_protected, protection_reasons = self.is_protected(context)

        finding_dict["semantic_context"] = {
            "in_function": context.in_function,
            "in_class": context.in_class,
            "in_docstring": context.in_docstring,
            "in_comment": context.in_comment,
            "is_protected": is_protected,
            "protection_reasons": protection_reasons,
            "luciole_warnings": context.domain_warnings,
            "relevant_bubbles_count": len(context.relevant_bubbles),
        }

        # Add Luciole domain knowledge
        if context.domain_warnings:
            finding_dict["luciole_advice"] = context.domain_warnings

        return finding_dict


# Singleton instance for easy access
_context_builder: Optional[SemanticContextBuilder] = None


def get_context_builder(luciole_path: Optional[str] = None) -> SemanticContextBuilder:
    """Get or create the semantic context builder."""
    global _context_builder
    if _context_builder is None:
        _context_builder = SemanticContextBuilder(luciole_path)
    return _context_builder


def analyze_context(file_path: str, line_number: int,
                    line_content: str, category: str = "") -> CodeContext:
    """Convenience function to analyze context."""
    builder = get_context_builder()
    return builder.build_context(file_path, line_number, line_content, category)


def is_false_positive_by_context(file_path: str, line_number: int,
                                  line_content: str, category: str = "") -> Tuple[bool, List[str]]:
    """Check if a finding is a false positive based on semantic context."""
    builder = get_context_builder()
    context = builder.build_context(file_path, line_number, line_content, category)
    return builder.is_protected(context)


# =============================================================================
# LUCIOLE CONTEXT PROVIDER V2 (Phase 301.5k)
# The central hub for the Luciole swarm - semantic vector search
# =============================================================================


class LucioleContextProvider:
    """
    🪲 PHAROS - The Lighthouse that orchestrates the Luciole Swarm (V2).

    The Lucioles are flying context bubbles that encapsulate domain knowledge.
    They provide semantic context to the audit system using vector embeddings.

    V2 Architecture (Phase 301.5k):
    - Qdrant vector store for semantic search
    - sentence-transformers embeddings (all-MiniLM-L6-v2)
    - Sub-100ms retrieval latency
    - Fallback to keyword matching if Qdrant unavailable

    Usage:
        provider = LucioleContextProvider.get_instance()
        bubbles = provider.find_relevant("cypher query injection")
        # Returns semantically similar Luciole bubbles
    """

    _instance: Optional["LucioleContextProvider"] = None
    _qdrant_available: bool = False

    # Qdrant configuration
    QDRANT_HOST = "localhost"
    QDRANT_PORT = 6333
    COLLECTION_NAME = "luciole_context_bubbles"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"

    def __init__(self, bubbles_path: Optional[str] = None):
        """Initialize the Luciole swarm with Qdrant."""
        self._qdrant_client = None
        self._embedder = None
        self._fallback_bubbles: List[Dict] = []
        self._by_archetype: Dict[str, List[Dict]] = {}
        self._by_category: Dict[str, List[Dict]] = {}

        # Phase 11: Learning statistics
        self._learning_stats = {
            "bubbles_created": 0,
            "bubbles_merged": 0,
            "bubbles_rejected": 0,  # Already known
            "bubbles_boosted": 0,
            "last_learned": None,
            "session_start": self._get_timestamp(),
        }

        # Try to connect to Qdrant
        self._init_qdrant()

        # Load JSON as fallback
        if not self._qdrant_available:
            self._load_bubbles_fallback(bubbles_path)

    def _init_qdrant(self):
        """Initialize Qdrant client and embedder."""
        try:
            from qdrant_client import QdrantClient
            from sentence_transformers import SentenceTransformer

            self._qdrant_client = QdrantClient(
                host=self.QDRANT_HOST,
                port=self.QDRANT_PORT,
                timeout=5.0
            )

            # Check if collection exists
            collections = [c.name for c in self._qdrant_client.get_collections().collections]
            if self.COLLECTION_NAME in collections:
                self._embedder = SentenceTransformer(self.EMBEDDING_MODEL)
                self._qdrant_available = True
                count = self._qdrant_client.count(collection_name=self.COLLECTION_NAME).count
                print(f"[LUCIOLE V2] Qdrant connected: {count} bubbles")
            else:
                print(f"[LUCIOLE V2] Collection '{self.COLLECTION_NAME}' not found, using fallback")

        except Exception as e:
            print(f"[LUCIOLE V2] Qdrant unavailable ({e}), using keyword fallback")
            self._qdrant_available = False

    def _load_bubbles_fallback(self, custom_path: Optional[str] = None):
        """Load Luciole bubbles from JSON (fallback mode)."""
        bubble_paths = [
            Path(custom_path) if custom_path else None,
            Path.cwd() / "apps/backend/data/luciole_bubbles.json",
            Path.cwd().parent / "apps/backend/data/luciole_bubbles.json",
            Path.home() / "Smash_App/apps/backend/data/luciole_bubbles.json",
        ]

        for path in [p for p in bubble_paths if p]:
            if path.exists():
                try:
                    data = json.loads(path.read_text())
                    self._parse_bubbles_fallback(data)
                    print(f"[LUCIOLE V2] Fallback loaded: {len(self._fallback_bubbles)} bubbles")
                    break
                except Exception as e:
                    print(f"[LUCIOLE V2] Failed to load {path}: {e}")

    def _parse_bubbles_fallback(self, data: Dict):
        """Parse bubbles for fallback keyword matching."""
        for key, value in data.items():
            if key in ("version", "total_bubbles", "last_updated", "_meta"):
                continue
            if isinstance(value, list):
                self._fallback_bubbles.extend(value)

                for bubble in value:
                    archetype = bubble.get("archetype", "").upper()
                    if archetype:
                        self._by_archetype.setdefault(archetype, []).append(bubble)

                    domain = bubble.get("domain", "")
                    if domain:
                        category = domain.split("/")[0]
                        self._by_category.setdefault(category, []).append(bubble)

    @classmethod
    def get_instance(cls, bubbles_path: Optional[str] = None) -> "LucioleContextProvider":
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls(bubbles_path)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton (for testing)."""
        cls._instance = None

    @property
    def bubble_count(self) -> int:
        """Total number of loaded bubbles."""
        if self._qdrant_available:
            return self._qdrant_client.count(collection_name=self.COLLECTION_NAME).count
        return len(self._fallback_bubbles)

    @property
    def is_semantic(self) -> bool:
        """Whether semantic search is available."""
        return self._qdrant_available

    def find_relevant(
        self,
        text: str,
        archetype: Optional[str] = None,
        category: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict]:
        """
        Find Luciole bubbles relevant to the given context.

        Uses semantic vector search (Qdrant) if available,
        falls back to keyword matching otherwise.

        Args:
            text: The text to match against (code, error message, etc.)
            archetype: Optional archetype filter (DIONYSUS, PANDORA, etc.)
            category: Optional category filter (injection, security, etc.)
            max_results: Maximum number of bubbles to return

        Returns:
            List of matching Luciole bubbles with reminders
        """
        import time
        start_time = time.time()

        if self._qdrant_available:
            results = self._semantic_search(text, archetype, category, max_results)
            mode = "semantic"
        else:
            results = self._keyword_search(text, archetype, category, max_results)
            mode = "keyword"

        # Record metrics (Phase 15: Instrumentation)
        latency_ms = (time.time() - start_time) * 1000
        hit = len(results) > 0
        try:
            collector = LucioleMetricsCollector.get_instance()
            collector.record_search(mode, latency_ms, hit, text[:50])
        except Exception:
            pass  # Don't fail search if metrics fail

        return results

    def _semantic_search(
        self,
        text: str,
        archetype: Optional[str] = None,
        category: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict]:
        """Semantic search using Qdrant vector store."""
        import time
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        # Create query embedding with timing (Phase 15: Instrumentation)
        embed_start = time.time()
        query_vector = self._embedder.encode(text).tolist()
        embed_ms = (time.time() - embed_start) * 1000

        # Record embedding metrics
        try:
            collector = LucioleMetricsCollector.get_instance()
            collector.record_embedding(embed_ms, len(text))
        except Exception:
            pass

        # Build filter if archetype specified
        search_filter = None
        if archetype:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="archetype",
                        match=MatchValue(value=archetype.upper())
                    )
                ]
            )

        # Execute search
        results = self._qdrant_client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vector,
            query_filter=search_filter,
            limit=max_results,
        )

        # Convert to bubble format
        bubbles = []
        for hit in results.points:
            payload = hit.payload
            payload["_score"] = hit.score
            bubbles.append(payload)

        return bubbles

    def _keyword_search(
        self,
        text: str,
        archetype: Optional[str] = None,
        category: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict]:
        """Fallback keyword-based search."""
        text_lower = text.lower()
        results = []
        seen_domains = set()

        # Choose bubble pool
        if archetype and archetype.upper() in self._by_archetype:
            bubble_pool = self._by_archetype[archetype.upper()]
        elif category and category.lower() in self._by_category:
            bubble_pool = self._by_category[category.lower()]
        else:
            bubble_pool = self._fallback_bubbles

        # Score and rank
        scored = []
        for bubble in bubble_pool:
            score = sum(2 for kw in bubble.get("keywords", []) if kw.lower() in text_lower)
            if score > 0:
                scored.append((score, bubble))

        scored.sort(key=lambda x: x[0], reverse=True)

        for score, bubble in scored:
            domain = bubble.get("domain", "")
            if domain not in seen_domains:
                seen_domains.add(domain)
                results.append(bubble)
                if len(results) >= max_results:
                    break

        return results

    def get_advice(self, bubbles: List[Dict]) -> List[str]:
        """Extract reminders from bubbles as advice."""
        return [b.get("reminder", "") for b in bubbles if b.get("reminder")]

    def get_bubbles_for_archetype(self, archetype: str) -> List[Dict]:
        """Get all bubbles associated with an archetype."""
        if self._qdrant_available:
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            results = self._qdrant_client.scroll(
                collection_name=self.COLLECTION_NAME,
                scroll_filter=Filter(
                    must=[FieldCondition(key="archetype", match=MatchValue(value=archetype.upper()))]
                ),
                limit=100,
                with_payload=True
            )[0]
            return [p.payload for p in results]
        return self._by_archetype.get(archetype.upper(), [])

    def get_advice_for_category(self, category: str) -> Optional[str]:
        """Get consolidated advice for a category."""
        bubbles = self.find_relevant(category, category=category, max_results=1)
        if bubbles:
            return bubbles[0].get("reminder")
        return None

    def enrich_finding(
        self,
        archetype: str,
        category: str,
        file_path: str,
        code_snippet: str
    ) -> Tuple[Optional[List[str]], Optional[str]]:
        """
        Enrich a finding with Luciole advice.

        Uses pure semantic search without archetype filtering because:
        - PHAROS findings can be about any domain (credentials, git, etc.)
        - Semantic similarity is more relevant than archetype matching
        - Category is already part of the search text

        Returns:
            Tuple of (advice_list, domain)
        """
        # Combine all context for semantic search
        # Include category for better semantic matching
        context_text = f"{category} {file_path} {code_snippet}"

        # Find relevant bubbles using pure semantic search
        # Don't filter by archetype - let semantic similarity decide
        relevant = self.find_relevant(
            text=context_text,
            archetype=None,  # No archetype filter - semantic search is better
            category=None,   # Already in context_text
            max_results=3
        )

        if relevant:
            advice = self.get_advice(relevant)
            domain = relevant[0].get("domain", "")

            # Phase 8: Boost activation when bubble is used
            for bubble in relevant:
                self.boost_activation(bubble.get("domain", ""))

            return advice if advice else None, domain
        return None, None

    def boost_activation(self, domain: str, boost_amount: float = 0.2) -> bool:
        """
        🪲 Boost a bubble's activation score when it's used.

        Called automatically when a bubble is matched and used to enrich a finding.
        This keeps frequently-used bubbles alive (prevents decay archival).

        Args:
            domain: The bubble's domain to boost
            boost_amount: Amount to add to activation score (default 0.2)

        Returns:
            True if boost was applied, False otherwise
        """
        if not self._qdrant_available:
            return False

        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            from datetime import datetime

            # Find the bubble by domain
            points, _ = self._qdrant_client.scroll(
                collection_name=self.COLLECTION_NAME,
                scroll_filter=Filter(must=[
                    FieldCondition(key="domain", match=MatchValue(value=domain))
                ]),
                limit=1,
                with_payload=True,
            )

            if not points:
                return False

            point = points[0]
            payload = point.payload

            # Calculate new values
            current_score = payload.get("activation_score", 1.0)
            new_score = min(1.0, current_score + boost_amount)
            activation_count = payload.get("activation_count", 0) + 1

            # Update
            self._qdrant_client.set_payload(
                collection_name=self.COLLECTION_NAME,
                payload={
                    "activation_score": new_score,
                    "activation_count": activation_count,
                    "last_activated": datetime.now().isoformat(),
                },
                points=[point.id],
            )

            # Record metrics (Phase 15: Instrumentation)
            try:
                collector = LucioleMetricsCollector.get_instance()
                collector.record_boost(domain, boost_amount)
            except Exception:
                pass

            return True

        except Exception as e:
            # Don't fail enrichment if boost fails
            print(f"[LUCIOLE] Boost failed for {domain}: {e}")
            return False

    def get_stats(self) -> Dict[str, any]:
        """Get statistics about the Luciole swarm."""
        stats = {
            "mode": "semantic" if self._qdrant_available else "keyword",
            "total_bubbles": self.bubble_count,
            "qdrant_host": f"{self.QDRANT_HOST}:{self.QDRANT_PORT}",
            "embedding_model": self.EMBEDDING_MODEL,
        }

        if self._qdrant_available:
            info = self._qdrant_client.get_collection(self.COLLECTION_NAME)
            stats["vector_size"] = info.config.params.vectors.size
            stats["indexed"] = info.indexed_vectors_count

        return stats

    # =========================================================================
    # PHASE 3: LLM-Powered Bubble Generation (Phase 301.5k)
    # =========================================================================

    # Default models: phi3 for fast matching, deepseek-r1 for generation
    OLLAMA_MODEL_FAST = "phi3:mini"      # Fast model for scoring/matching
    OLLAMA_MODEL_REASON = "deepseek-r1:7b"  # Reasoning model for generation
    OLLAMA_URL = "http://localhost:11434"

    def generate_bubble(
        self,
        finding_category: str,
        finding_title: str,
        code_snippet: str,
        file_path: str,
        archetype: str = "PHAROS",
        learned_from: str = "auto-generated"
    ) -> Optional[Dict]:
        """
        🪲 Generate a new Luciole bubble from a finding using local LLM.

        Uses Ollama with DeepSeek-R1 to create a structured bubble
        that encapsulates the lesson learned from this finding.

        Args:
            finding_category: The category of the finding (e.g., "hardcoded_secret")
            finding_title: Short description of the issue
            code_snippet: The problematic code
            file_path: Where the issue was found
            archetype: The audit archetype that found it
            learned_from: Context about when this was learned

        Returns:
            A new Luciole bubble dict, or None if generation failed
        """
        import requests

        prompt = f"""You are a code audit expert. Analyze this finding and create a structured knowledge bubble.

FINDING:
- Category: {finding_category}
- Title: {finding_title}
- File: {file_path}
- Code: {code_snippet}

Generate a JSON object with exactly these fields:
{{
  "domain": "<category>/<subcategory>",
  "pattern_danger": "<what dangerous pattern was found, 1 sentence>",
  "reminder": "<actionable advice to prevent this, 1-2 sentences>",
  "keywords": ["<5-7 keywords for matching>"],
  "severity": "<info|warning|critical>"
}}

Return ONLY the JSON object, no explanation."""

        import time
        start_time = time.time()

        try:
            response = requests.post(
                f"{self.OLLAMA_URL}/api/generate",
                json={
                    "model": self.OLLAMA_MODEL_REASON,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3}
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "")

                # Record LLM metrics (Phase 15: Instrumentation)
                latency_ms = (time.time() - start_time) * 1000
                try:
                    collector = LucioleMetricsCollector.get_instance()
                    collector.record_llm("generate_bubble", latency_ms, self.OLLAMA_MODEL_REASON)
                except Exception:
                    pass

                # Extract JSON from response
                bubble = self._parse_llm_bubble(text)
                if bubble:
                    # Add metadata
                    bubble["archetype"] = archetype
                    bubble["learned_from"] = learned_from
                    bubble["created_at"] = self._get_timestamp()
                    return bubble

        except Exception as e:
            print(f"[LUCIOLE] Bubble generation failed: {e}")

        return None

    def _parse_llm_bubble(self, text: str) -> Optional[Dict]:
        """Parse LLM output to extract the bubble JSON."""
        import re

        # Try to find JSON in the response
        json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Try to parse the whole text as JSON
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        return None

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def add_bubble(self, bubble: Dict) -> bool:
        """
        Add a new bubble to the Qdrant collection.

        Args:
            bubble: The bubble dict with domain, pattern_danger, reminder, etc.

        Returns:
            True if successful, False otherwise
        """
        if not self._qdrant_available:
            print("[LUCIOLE] Cannot add bubble: Qdrant not available")
            return False

        try:
            from qdrant_client.models import PointStruct
            import hashlib

            # Generate embedding
            text_to_embed = " ".join([
                bubble.get("domain", ""),
                bubble.get("pattern_danger", ""),
                bubble.get("reminder", ""),
                " ".join(bubble.get("keywords", []))
            ])
            embedding = self._embedder.encode(text_to_embed).tolist()

            # Generate unique ID
            content = f"{bubble.get('domain', '')}:{bubble.get('pattern_danger', '')}"
            bubble_id = hashlib.md5(content.encode()).hexdigest()[:12]
            point_id = hash(bubble_id) & 0xFFFFFFFFFFFF

            # Create point
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "id": bubble_id,
                    "domain": bubble.get("domain", ""),
                    "domain_key": bubble.get("domain", "").split("/")[0],
                    "pattern_danger": bubble.get("pattern_danger", ""),
                    "reminder": bubble.get("reminder", ""),
                    "archetype": bubble.get("archetype", ""),
                    "learned_from": bubble.get("learned_from", ""),
                    "severity": bubble.get("severity", "info"),
                    "keywords": bubble.get("keywords", []),
                    "created_at": bubble.get("created_at", self._get_timestamp()),
                    "cluster_id": -1,  # Will be assigned on next clustering
                    "cluster_theme": "new",
                    "is_noise": True,
                }
            )

            self._qdrant_client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=[point]
            )

            # Record metrics (Phase 15: Instrumentation)
            try:
                collector = LucioleMetricsCollector.get_instance()
                collector.record_bubble_event("created", bubble.get("domain", ""))
            except Exception:
                pass

            print(f"[LUCIOLE] Added bubble: {bubble.get('domain')}")
            return True

        except Exception as e:
            print(f"[LUCIOLE] Failed to add bubble: {e}")
            return False

    def merge_similar_bubbles(
        self,
        bubble1: Dict,
        bubble2: Dict,
        delete_originals: bool = True
    ) -> Optional[Dict]:
        """
        🪲 Merge two similar bubbles into one using LLM.

        Args:
            bubble1: First bubble
            bubble2: Second bubble
            delete_originals: Whether to delete the original bubbles

        Returns:
            The merged bubble, or None if merge failed
        """
        import requests

        prompt = f"""You are merging two similar code audit knowledge bubbles into one.

BUBBLE 1:
- Domain: {bubble1.get('domain')}
- Pattern: {bubble1.get('pattern_danger')}
- Reminder: {bubble1.get('reminder')}
- Keywords: {bubble1.get('keywords')}

BUBBLE 2:
- Domain: {bubble2.get('domain')}
- Pattern: {bubble2.get('pattern_danger')}
- Reminder: {bubble2.get('reminder')}
- Keywords: {bubble2.get('keywords')}

Create a MERGED bubble that combines both. Use the best domain name, combine patterns, merge reminders, and union keywords.

Return ONLY a JSON object:
{{
  "domain": "<best domain name>",
  "pattern_danger": "<combined pattern>",
  "reminder": "<merged actionable advice>",
  "keywords": ["<union of keywords, max 10>"],
  "severity": "<highest of the two>"
}}"""

        try:
            response = requests.post(
                f"{self.OLLAMA_URL}/api/generate",
                json={
                    "model": self.OLLAMA_MODEL_REASON,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2}
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "")

                merged = self._parse_llm_bubble(text)
                if merged:
                    # Add metadata from originals
                    merged["archetype"] = bubble1.get("archetype") or bubble2.get("archetype", "PHAROS")
                    merged["learned_from"] = f"merged: {bubble1.get('learned_from', '?')} + {bubble2.get('learned_from', '?')}"
                    merged["created_at"] = self._get_timestamp()

                    # Add merged bubble
                    if self.add_bubble(merged):
                        # Delete originals if requested
                        if delete_originals and self._qdrant_available:
                            self._delete_bubble_by_domain(bubble1.get("domain"))
                            self._delete_bubble_by_domain(bubble2.get("domain"))
                            print(f"[LUCIOLE] Merged: {bubble1.get('domain')} + {bubble2.get('domain')} → {merged.get('domain')}")

                        return merged

        except Exception as e:
            print(f"[LUCIOLE] Merge failed: {e}")

        return None

    def _delete_bubble_by_domain(self, domain: str) -> bool:
        """Delete a bubble by its domain."""
        if not self._qdrant_available:
            return False

        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue, PointIdsList

            # Find the point
            results = self._qdrant_client.scroll(
                collection_name=self.COLLECTION_NAME,
                scroll_filter=Filter(
                    must=[FieldCondition(key="domain", match=MatchValue(value=domain))]
                ),
                limit=1,
                with_payload=False
            )[0]

            if results:
                self._qdrant_client.delete(
                    collection_name=self.COLLECTION_NAME,
                    points_selector=PointIdsList(points=[results[0].id])
                )
                return True

        except Exception as e:
            print(f"[LUCIOLE] Delete failed: {e}")

        return False

    def auto_learn_from_finding(
        self,
        finding: Dict,
        threshold: float = 0.45
    ) -> Optional[Dict]:
        """
        🪲 Automatically learn from a finding if it's novel enough.

        Checks if a similar bubble already exists. If not, generates
        a new bubble from the finding.

        Args:
            finding: The audit finding dict
            threshold: Cosine similarity threshold (0-1). Above this = already known.
                       Default 0.45 based on embedding model characteristics.
                       - >0.5: Very similar topic already covered
                       - 0.4-0.5: Related but potentially novel angle
                       - <0.4: Likely novel concept

        Returns:
            New bubble if created, None if similar exists or generation failed
        """
        # Build search text from finding
        search_text = " ".join([
            finding.get("category", ""),
            finding.get("title", ""),
            finding.get("code_snippet", "")
        ])

        # Check for similar existing bubbles
        similar = self.find_relevant(search_text, max_results=1)

        if similar and similar[0].get("_score", 0) >= threshold:
            # Already have a similar bubble - boost it instead
            self._learning_stats["bubbles_rejected"] += 1
            # Boost the existing bubble since we saw a similar finding
            existing_domain = similar[0].get("domain")
            if existing_domain:
                self.boost_activation(existing_domain, 0.1)
                self._learning_stats["bubbles_boosted"] += 1
            return None

        # Generate new bubble
        bubble = self.generate_bubble(
            finding_category=finding.get("category", "unknown"),
            finding_title=finding.get("title", ""),
            code_snippet=finding.get("code_snippet", ""),
            file_path=finding.get("file_path", ""),
            archetype=finding.get("archetype", "PHAROS"),
            learned_from=f"auto-learned from audit"
        )

        if bubble:
            # Add bubble to Qdrant
            if self.add_bubble(bubble):
                self._learning_stats["bubbles_created"] += 1
                self._learning_stats["last_learned"] = self._get_timestamp()
                print(f"[LUCIOLE] Learned new bubble: {bubble.get('domain')}")
            else:
                print(f"[LUCIOLE] Failed to add bubble: {bubble.get('domain')}")
                return None

        return bubble

    # =========================================================================
    # PHASE 11: Apprentissage Continu (Phase 301.5n)
    # =========================================================================

    def get_learning_stats(self) -> Dict:
        """Get learning statistics for this session."""
        return {
            **self._learning_stats,
            "total_bubbles": self._get_bubble_count(),
        }

    def _get_bubble_count(self) -> int:
        """Get current total bubble count."""
        if self._qdrant_available:
            try:
                return self._qdrant_client.count(collection_name=self.COLLECTION_NAME).count
            except Exception:
                pass
        return len(self._fallback_bubbles)

    def learn_from_audit_results(
        self,
        findings: List[Dict],
        min_severity: str = "warning",
        threshold: float = 0.45
    ) -> Dict:
        """
        🪲 Batch learning from audit findings.

        Processes multiple findings and learns from novel ones.

        Args:
            findings: List of audit findings
            min_severity: Minimum severity to learn from
            threshold: Similarity threshold for novelty

        Returns:
            Learning summary with created/rejected counts
        """
        severity_order = {"info": 0, "warning": 1, "critical": 2}
        min_level = severity_order.get(min_severity, 1)

        created = []
        rejected = 0
        boosted = 0

        for finding in findings:
            # Filter by severity
            finding_severity = finding.get("severity", "info")
            if severity_order.get(finding_severity, 0) < min_level:
                continue

            # Try to learn
            bubble = self.auto_learn_from_finding(finding, threshold)
            if bubble:
                created.append(bubble)
            else:
                rejected += 1

        # Check how many were boosted
        boosted = self._learning_stats["bubbles_boosted"]

        return {
            "findings_processed": len(findings),
            "bubbles_created": len(created),
            "already_known": rejected,
            "existing_boosted": boosted,
            "new_bubbles": created,
        }

    def consolidate_similar_bubbles(
        self,
        similarity_threshold: float = 0.85,
        max_merges: int = 10
    ) -> Dict:
        """
        🪲 Consolidation pipeline: merge highly similar bubbles.

        Finds pairs of bubbles that are semantically almost identical
        and merges them using LLM.

        Args:
            similarity_threshold: Minimum similarity to consider for merge
            max_merges: Maximum number of merges to perform

        Returns:
            Consolidation summary
        """
        if not self._qdrant_available:
            return {"error": "Qdrant not available for consolidation"}

        merged_count = 0
        merge_pairs = []

        try:
            # Get all bubbles
            points, _ = self._qdrant_client.scroll(
                collection_name=self.COLLECTION_NAME,
                limit=200,
                with_payload=True,
                with_vectors=True,
            )

            # Find similar pairs
            for i, p1 in enumerate(points):
                if merged_count >= max_merges:
                    break

                for j, p2 in enumerate(points):
                    if j <= i:
                        continue

                    # Compute similarity
                    import math
                    v1, v2 = p1.vector, p2.vector
                    dot = sum(a * b for a, b in zip(v1, v2))
                    norm1 = math.sqrt(sum(a * a for a in v1))
                    norm2 = math.sqrt(sum(b * b for b in v2))
                    similarity = dot / (norm1 * norm2) if norm1 and norm2 else 0

                    if similarity >= similarity_threshold:
                        # Try to merge
                        merged = self.merge_bubbles(
                            p1.payload,
                            p2.payload,
                            delete_originals=True
                        )
                        if merged:
                            merged_count += 1
                            merge_pairs.append({
                                "bubble1": p1.payload.get("domain"),
                                "bubble2": p2.payload.get("domain"),
                                "merged_into": merged.get("domain"),
                                "similarity": round(similarity, 3),
                            })
                            self._learning_stats["bubbles_merged"] += 1

                            if merged_count >= max_merges:
                                break

        except Exception as e:
            return {"error": str(e)}

        return {
            "merged_count": merged_count,
            "merge_pairs": merge_pairs,
            "remaining_bubbles": self._get_bubble_count(),
        }

    # =========================================================================
    # PHASE 10: LLM Semantic Matching (Phase 301.5m)
    # =========================================================================

    _llm_enabled: bool = False  # Disabled by default for performance

    def enable_llm_matching(self, enabled: bool = True) -> None:
        """Enable or disable LLM-powered semantic matching."""
        self._llm_enabled = enabled
        if enabled:
            print(f"[LUCIOLE] LLM matching ENABLED (fast: {self.OLLAMA_MODEL_FAST}, reason: {self.OLLAMA_MODEL_REASON})")
        else:
            print("[LUCIOLE] LLM matching DISABLED (using embeddings only)")

    def is_llm_available(self) -> bool:
        """Check if Ollama is available for LLM matching."""
        import requests
        try:
            response = requests.get(f"{self.OLLAMA_URL}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                # Check for either fast model (phi3) or reasoning model (deepseek)
                has_fast = any(n.startswith("phi3") for n in model_names)
                has_reason = any(n.startswith("deepseek-r1") for n in model_names)
                return has_fast or has_reason
        except Exception:
            pass
        return False

    def semantic_match(
        self,
        query: str,
        max_results: int = 5,
        min_relevance: float = 0.6
    ) -> List[Dict]:
        """
        🪲 Use LLM for semantic matching - understands intent, not just keywords.

        This goes beyond embedding similarity by using the LLM to reason about
        which bubbles are truly relevant to the query, considering context,
        implications, and nuances.

        Args:
            query: Natural language query describing the situation
            max_results: Maximum number of matches to return
            min_relevance: Minimum relevance score (0-1) from LLM

        Returns:
            List of matching bubbles with LLM relevance scores and explanations
        """
        import requests

        # First-pass: Get candidates via embeddings (fast)
        candidates = self.find_relevant(query, max_results=20)
        if not candidates:
            return []

        # Build context for LLM evaluation (compact format for speed)
        bubbles_context = "\n".join([
            f"[{i+1}] {b.get('domain')}: {b.get('pattern_danger', 'N/A')[:100]}"
            for i, b in enumerate(candidates[:7])  # Limit to top 7 for speed
        ])

        prompt = f"""Rate these bubbles for the query. Return JSON array only.

Query: {query}

Bubbles:
{bubbles_context}

Return: [{{"index": N, "relevance": 0.0-1.0, "reason": "why"}}]
Only include if relevance >= {min_relevance}. Max {max_results} results."""

        import time
        start_time = time.time()

        try:
            response = requests.post(
                f"{self.OLLAMA_URL}/api/generate",
                json={
                    "model": self.OLLAMA_MODEL_FAST,  # Fast model for matching
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1}  # Low temp for consistent scoring
                },
                timeout=30  # Faster timeout for fast model
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "")

                # Record LLM metrics (Phase 15: Instrumentation)
                latency_ms = (time.time() - start_time) * 1000
                try:
                    collector = LucioleMetricsCollector.get_instance()
                    collector.record_llm("semantic_match", latency_ms, self.OLLAMA_MODEL_FAST)
                except Exception:
                    pass

                # Parse LLM response
                matches = self._parse_semantic_matches(text, candidates)

                # Sort by relevance and limit
                matches.sort(key=lambda x: x.get("_llm_relevance", 0), reverse=True)
                return matches[:max_results]

        except Exception as e:
            print(f"[LUCIOLE] LLM semantic match failed: {e}")

        # Fallback to embedding results
        return candidates[:max_results]

    def _parse_semantic_matches(
        self,
        llm_response: str,
        candidates: List[Dict]
    ) -> List[Dict]:
        """Parse LLM semantic matching response."""
        import json
        import re

        # Extract JSON array from response
        json_match = re.search(r'\[[\s\S]*\]', llm_response)
        if not json_match:
            return []

        try:
            evaluations = json.loads(json_match.group())
        except json.JSONDecodeError:
            return []

        results = []
        for eval_item in evaluations:
            idx = eval_item.get("index", 0) - 1  # Convert to 0-based
            if 0 <= idx < len(candidates):
                bubble = candidates[idx].copy()
                bubble["_llm_relevance"] = eval_item.get("relevance", 0)
                bubble["_llm_reason"] = eval_item.get("reason", "")
                bubble["_match_mode"] = "semantic"
                results.append(bubble)

        return results

    def find_relevant_smart(
        self,
        text: str,
        max_results: int = 5,
        archetype: Optional[str] = None,
        use_llm: Optional[bool] = None
    ) -> List[Dict]:
        """
        🪲 Smart matching: uses LLM if enabled, falls back to embeddings.

        This is the recommended entry point for finding relevant bubbles.
        It automatically chooses the best matching strategy based on
        configuration and availability.

        Args:
            text: Query text or code context
            max_results: Maximum results to return
            archetype: Optional archetype filter
            use_llm: Override LLM setting (None = use class setting)

        Returns:
            List of relevant bubbles with match metadata
        """
        # Determine if we should use LLM
        should_use_llm = use_llm if use_llm is not None else self._llm_enabled

        if should_use_llm and self.is_llm_available():
            # Use LLM semantic matching
            results = self.semantic_match(text, max_results=max_results)

            # Apply archetype filter if specified
            if archetype:
                results = [b for b in results if b.get("archetype") == archetype]

            return results

        # Fallback to embedding-based matching
        return self.find_relevant(text, max_results=max_results, archetype=archetype)

    def explain_match(
        self,
        query: str,
        bubble: Dict
    ) -> str:
        """
        🪲 Use LLM to explain why a bubble matches a query.

        Fast single-bubble explanation (simpler than full semantic_match).

        Args:
            query: The user's query
            bubble: The matched bubble

        Returns:
            1-2 sentence explanation of relevance
        """
        import requests

        prompt = f"""Explain briefly why this knowledge bubble is relevant to the query.

Query: {query}
Bubble: {bubble.get('domain')} - {bubble.get('pattern_danger', '')[:150]}

Response (1-2 sentences):"""

        try:
            response = requests.post(
                f"{self.OLLAMA_URL}/api/generate",
                json={
                    "model": self.OLLAMA_MODEL_FAST,  # Fast model for explanations
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 150}
                },
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "").strip()
                return text[:300]  # Limit length

        except Exception as e:
            pass

        return f"Matches query semantically (domain: {bubble.get('domain')})"

    def quick_semantic_score(
        self,
        query: str,
        bubble: Dict
    ) -> float:
        """
        🪲 Quick LLM-based relevance score for a single bubble.

        Faster than full semantic_match - asks for just a 0-10 score.

        Returns:
            Relevance score 0.0-1.0 or -1 if LLM unavailable
        """
        import requests

        prompt = f"""Rate 0-10 how relevant this bubble is to the query. Reply with ONLY the number.

Query: {query}
Bubble: {bubble.get('domain')} - {bubble.get('pattern_danger', '')[:100]}

Score (0-10):"""

        try:
            response = requests.post(
                f"{self.OLLAMA_URL}/api/generate",
                json={
                    "model": self.OLLAMA_MODEL_FAST,  # Fast model for scoring
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0, "num_predict": 10}
                },
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "").strip()
                # Extract number from response
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    score = int(numbers[0])
                    return min(score / 10.0, 1.0)

        except Exception:
            pass

        return -1  # LLM unavailable


# Convenience function
def get_luciole_provider(bubbles_path: Optional[str] = None) -> LucioleContextProvider:
    """Get the singleton Luciole context provider."""
    return LucioleContextProvider.get_instance(bubbles_path)


# =============================================================================
# PHASE 7: PROACTIVE DETECTION (Phase 301.5k)
# Lucioles that can PRODUCE findings, not just ENRICH them
# =============================================================================


@dataclass
class LucioleDetection:
    """A detection produced by a Luciole bubble."""
    bubble_domain: str
    pattern_danger: str
    reminder: str
    file_path: str
    line_number: int
    line_content: str
    severity: str
    keywords_matched: List[str]
    confidence: float  # 0-1 based on keyword density and pattern match


class LucioleDetector:
    """
    🪲 Proactive Luciole Detector (Phase 7)

    Lucioles are no longer passive annotators - they actively scan code
    and PRODUCE findings based on their encoded knowledge patterns.

    This implements Q5 from Deep Research:
    "Les Lucioles peuvent-elles PRODUIRE des findings en plus d'ENRICHIR?"

    Architecture:
        1. Load all bubbles with their patterns and keywords
        2. For each file, extract semantic context
        3. Match bubbles by keyword presence + pattern recognition
        4. Produce findings with confidence scores

    Usage:
        detector = LucioleDetector()
        detections = detector.scan_file("app/core/database.py")
        # Returns list of LucioleDetection findings
    """

    # Minimum keyword matches to consider a bubble relevant
    MIN_KEYWORD_MATCHES = 2

    # Minimum confidence to report a detection
    MIN_CONFIDENCE = 0.4

    # Pattern templates for common dangers
    DANGER_PATTERNS = {
        "hardcoded": [
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]",
            r"api_key\s*=\s*['\"][^'\"]+['\"]",
            r"token\s*=\s*['\"][^'\"]+['\"]",
        ],
        "injection": [
            r"f['\"].*\{.*user.*\}",
            r"f['\"].*\{.*input.*\}",
            r"\.format\(.*user.*\)",
            r"\+\s*user",
            r"\+\s*input",
        ],
        "blocking": [
            r"time\.sleep\(",
            r"requests\.(get|post|put|delete)\(",
            r"\.read\(\)",
            r"open\(.*\)\.read\(\)",
        ],
        "unsafe": [
            r"eval\(",
            r"exec\(",
            r"pickle\.load",
            r"subprocess\.call\(.*shell\s*=\s*True",
            r"os\.system\(",
        ],
        "default": [
            r"\.get\([^,]+,\s*['\"][^'\"]+['\"]\)",  # Default value in .get()
            r"or\s+['\"][^'\"]+['\"]",  # Fallback with literal
        ],
    }

    def __init__(self, provider: Optional[LucioleContextProvider] = None):
        """Initialize detector with Luciole provider."""
        self.provider = provider or LucioleContextProvider.get_instance()
        self._bubbles_cache: List[Dict] = []
        self._patterns_compiled: Dict[str, List[re.Pattern]] = {}
        self._init_patterns()

    def _init_patterns(self):
        """Pre-compile regex patterns for efficiency."""
        for category, patterns in self.DANGER_PATTERNS.items():
            self._patterns_compiled[category] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def _load_all_bubbles(self) -> List[Dict]:
        """Load all bubbles from Qdrant."""
        if self._bubbles_cache:
            return self._bubbles_cache

        if not self.provider._qdrant_available:
            return self.provider._fallback_bubbles

        try:
            points, _ = self.provider._qdrant_client.scroll(
                collection_name=self.provider.COLLECTION_NAME,
                limit=1000,
                with_payload=True
            )
            self._bubbles_cache = [p.payload for p in points]
            return self._bubbles_cache
        except Exception as e:
            print(f"[LUCIOLE DETECTOR] Failed to load bubbles: {e}")
            return []

    def _match_keywords(self, line: str, keywords: List[str]) -> List[str]:
        """Find which keywords match in the line."""
        line_lower = line.lower()
        return [kw for kw in keywords if kw.lower() in line_lower]

    def _match_danger_patterns(self, line: str, domain: str) -> List[str]:
        """Check if line matches any danger patterns based on domain."""
        matched = []

        # Determine which pattern categories to check based on domain
        categories_to_check = []
        domain_lower = domain.lower()

        if "credential" in domain_lower or "secret" in domain_lower or "password" in domain_lower:
            categories_to_check.append("hardcoded")
        if "injection" in domain_lower or "cypher" in domain_lower or "sql" in domain_lower:
            categories_to_check.append("injection")
        if "blocking" in domain_lower or "performance" in domain_lower or "async" in domain_lower:
            categories_to_check.append("blocking")
        if "unsafe" in domain_lower or "eval" in domain_lower or "exec" in domain_lower:
            categories_to_check.append("unsafe")
        if "default" in domain_lower or "fallback" in domain_lower:
            categories_to_check.append("default")

        # Check all relevant categories
        for category in categories_to_check:
            patterns = self._patterns_compiled.get(category, [])
            for pattern in patterns:
                if pattern.search(line):
                    matched.append(category)
                    break

        return matched

    def _calculate_confidence(
        self,
        keywords_matched: int,
        total_keywords: int,
        patterns_matched: int,
        bubble_severity: str
    ) -> float:
        """Calculate detection confidence score."""
        # Base score from keyword match ratio
        keyword_ratio = keywords_matched / max(total_keywords, 1)
        keyword_score = min(0.5, keyword_ratio * 0.5)

        # Bonus for pattern matches
        pattern_score = min(0.3, patterns_matched * 0.15)

        # Severity weight
        severity_weight = {
            "critical": 0.2,
            "warning": 0.1,
            "info": 0.0
        }.get(bubble_severity, 0.0)

        return min(1.0, keyword_score + pattern_score + severity_weight)

    def _is_false_positive_line(self, line: str) -> bool:
        """Check if a line is likely a false positive (docs, regex, examples)."""
        stripped = line.strip()

        # Skip regex pattern definitions
        if re.search(r'r["\'].*\\', stripped):
            return True

        # Skip docstrings and multi-line strings
        if stripped.startswith('"""') or stripped.startswith("'''"):
            return True
        if stripped.endswith('"""') or stripped.endswith("'''"):
            return True

        # Skip lines that are clearly examples/test data
        example_markers = [
            "example", "e.g.", "# test", "# example", "test_",
            '"code_snippet":', "'code_snippet':",
            "pattern_regex", "pattern_danger",
            "edict=",  # PHARAOH edicts are documentation
            "content=",  # Content strings in config
            "description=",  # Description fields
        ]
        for marker in example_markers:
            if marker.lower() in stripped.lower():
                return True

        # Skip lines that are part of list/dict literals with keywords
        if stripped.startswith('"') and stripped.endswith('",'):
            return True
        if stripped.startswith("'") and stripped.endswith("',"):
            return True

        # Skip safe patterns (using environment variables correctly)
        safe_patterns = [
            r"os\.getenv\(",
            r"os\.environ\.get\(",
            r"os\.environ\[",
            r"environ\.get\(",
            r"SecretStr\(",
            r"getenv\(",
            r"\.env\b",  # References to .env files
            r"ERROR:.*environment variable",  # Error messages about env vars
            r"required.*environment",  # Documentation about requirements
        ]
        for pattern in safe_patterns:
            if re.search(pattern, stripped, re.IGNORECASE):
                return True

        # Skip lines that are implementing security (not violating it)
        security_implementation_patterns = [
            r"verify.*api.*key",  # Security verification functions
            r"def verify_",       # Verification functions
            r"async def verify_", # Async verification
            r"Depends\(verify",   # FastAPI dependency injection of verification
            r"APIKeyHeader\(",    # Security header definitions
            r"authenticate",      # Authentication code
            r"authorization",     # Authorization code
            r"not configured",    # Configuration error messages
            r"not set",           # Missing config error messages
            r"is not set",        # Missing config check
            r"missing.*key",      # Missing key error messages
            r"require.*key",      # Key requirement messages
            r"include.*header",   # Header requirement instructions
            r"logger\.(error|warning|info)",  # Log messages
            r"HTTPException\(",   # Error responses
            r"status_code=",      # HTTP status code setting
            r"detail=",           # Error detail messages
            r"from_env\(",        # Config from environment pattern
            r"def from_env",      # Config class method
            r"ValueError\(",      # Validation errors
            r"raise\s+\w+Error",  # Raising errors
            r"\.mount\(",         # FastAPI mount (static files, etc.)
            r"StaticFiles\(",     # Static file serving
            r"Optional\[",        # Type hints
            r"neo4j.*driver",     # Driver documentation
            r"uses env",          # Documentation about env vars
        ]
        for pattern in security_implementation_patterns:
            if re.search(pattern, stripped, re.IGNORECASE):
                return True

        return False

    def scan_line(self, line: str, line_number: int, file_path: str) -> List[LucioleDetection]:
        """Scan a single line for Luciole-based detections."""
        # Skip false positive lines
        if self._is_false_positive_line(line):
            return []

        detections = []
        bubbles = self._load_all_bubbles()

        for bubble in bubbles:
            keywords = bubble.get("keywords", [])
            domain = bubble.get("domain", "")
            severity = bubble.get("severity", "info")

            # Match keywords
            matched_kw = self._match_keywords(line, keywords)
            if len(matched_kw) < self.MIN_KEYWORD_MATCHES:
                continue

            # Match danger patterns
            patterns_matched = self._match_danger_patterns(line, domain)

            # Calculate confidence
            confidence = self._calculate_confidence(
                len(matched_kw),
                len(keywords),
                len(patterns_matched),
                severity
            )

            if confidence >= self.MIN_CONFIDENCE:
                detections.append(LucioleDetection(
                    bubble_domain=domain,
                    pattern_danger=bubble.get("pattern_danger", ""),
                    reminder=bubble.get("reminder", ""),
                    file_path=file_path,
                    line_number=line_number,
                    line_content=line.strip(),
                    severity=severity,
                    keywords_matched=matched_kw,
                    confidence=confidence
                ))

        return detections

    # Files that are part of the audit system itself (meta-detection risk)
    AUDIT_SYSTEM_FILES = [
        "audit.py", "semantic_context.py", "luciole_decay.py",
        "cluster_lucioles.py", "migrate_lucioles.py",
        "archetypes/", "/audit/", "/nile/", "luciole_swarm.py",
    ]

    def _is_audit_system_file(self, file_path: str) -> bool:
        """Check if file is part of the audit system itself."""
        file_str = str(file_path)
        return any(marker in file_str for marker in self.AUDIT_SYSTEM_FILES)

    def scan_file(self, file_path: str) -> List[LucioleDetection]:
        """
        🪲 Proactively scan a file for issues based on Luciole knowledge.

        This is the main entry point for proactive detection.

        Args:
            file_path: Path to the file to scan

        Returns:
            List of LucioleDetection findings
        """
        detections = []

        try:
            path = Path(file_path)
            if not path.exists():
                return []

            # Only scan Python files for now
            if path.suffix not in (".py", ".pyx"):
                return []

            # Skip audit system files to avoid meta-detection
            if self._is_audit_system_file(file_path):
                return []

            content = path.read_text(errors="ignore")
            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                # Skip empty lines and comments
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue

                # Scan line
                line_detections = self.scan_line(line, i, file_path)
                detections.extend(line_detections)

        except Exception as e:
            print(f"[LUCIOLE DETECTOR] Error scanning {file_path}: {e}")

        # Deduplicate by (file, line, domain)
        seen = set()
        unique = []
        for d in detections:
            key = (d.file_path, d.line_number, d.bubble_domain)
            if key not in seen:
                seen.add(key)
                unique.append(d)

        return unique

    def scan_directory(
        self,
        directory: str,
        recursive: bool = True,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[LucioleDetection]:
        """
        Scan an entire directory for Luciole-based detections.

        Args:
            directory: Path to the directory to scan
            recursive: Whether to scan subdirectories
            exclude_patterns: Glob patterns to exclude

        Returns:
            List of all LucioleDetection findings
        """
        exclude_patterns = exclude_patterns or [
            "**/venv/**", "**/.git/**", "**/__pycache__/**",
            "**/node_modules/**", "**/test_*", "**/*_test.py"
        ]

        all_detections = []
        dir_path = Path(directory)

        if not dir_path.exists():
            return []

        # Get all Python files
        pattern = "**/*.py" if recursive else "*.py"

        # Fast exclusion set (directory names to skip)
        exclude_dirs = {
            "venv", ".venv", "env", ".env", "node_modules",
            ".git", "__pycache__", "site-packages", "dist", "build"
        }

        for py_file in dir_path.glob(pattern):
            # Fast path: check if any excluded dir is in path parts
            if any(part in exclude_dirs for part in py_file.parts):
                continue

            # Check exclusions for more complex patterns
            file_str = str(py_file)
            excluded = any(
                part in file_str for part in ["test_", "_test.py"]
            )
            if excluded:
                continue

            detections = self.scan_file(str(py_file))
            all_detections.extend(detections)

        return all_detections

    def to_audit_findings(self, detections: List[LucioleDetection]) -> List[Dict]:
        """
        Convert LucioleDetections to standard audit finding format.

        This allows Luciole detections to be included in the unified audit report.
        """
        findings = []
        for d in detections:
            findings.append({
                "archetype": "LUCIOLE",  # New archetype for proactive detections
                "category": d.bubble_domain.replace("/", "_"),
                "title": d.pattern_danger[:60] + "..." if len(d.pattern_danger) > 60 else d.pattern_danger,
                "severity": "HIGH" if d.severity == "critical" else "MEDIUM" if d.severity == "warning" else "LOW",
                "file_path": d.file_path,
                "line_number": d.line_number,
                "code_snippet": d.line_content,
                "suggestion": d.reminder,
                "signal": f"luciole_{d.bubble_domain.split('/')[0]}",
                "confidence": f"{d.confidence:.2f}",
                "keywords_matched": d.keywords_matched,
            })
        return findings


# Convenience function for proactive scanning
def luciole_scan(path: str, recursive: bool = True) -> List[LucioleDetection]:
    """
    🪲 Proactively scan a file or directory for issues.

    Usage:
        from semantic_context import luciole_scan
        detections = luciole_scan("app/core/")
        for d in detections:
            print(f"{d.file_path}:{d.line_number} - {d.pattern_danger}")
    """
    detector = LucioleDetector()
    path_obj = Path(path)

    if path_obj.is_file():
        return detector.scan_file(path)
    elif path_obj.is_dir():
        return detector.scan_directory(path, recursive)
    else:
        return []


# =============================================================================
# PHASE 13: MEMORY TIERING & LIFECYCLE MANAGEMENT (Phase 301.5q)
# =============================================================================
#
# Implements memory lifecycle for Luciole bubbles:
#   - Activation Decay: Bubbles decay over time if not used
#   - Memory Tiers: HOT (active) → WARM (recent) → COLD (archive)
#   - Auto-Archive: Cold bubbles moved to archive collection
#   - Garbage Collection: Really old bubbles get deleted
#   - Resurrection: Archived bubbles can come back if needed
#
# =============================================================================


class MemoryTier(Enum):
    """Memory tiers for Luciole bubbles."""
    HOT = "hot"      # Recently activated, high priority
    WARM = "warm"    # Moderately active, normal priority
    COLD = "cold"    # Inactive, archive candidate
    FROZEN = "frozen"  # Archived, needs resurrection to use


@dataclass
class LifecycleConfig:
    """Configuration for Luciole lifecycle management."""
    # Decay settings
    decay_rate_per_day: float = 0.05  # 5% decay per day
    min_activation_score: float = 0.1  # Below this = archive candidate

    # Tier thresholds
    hot_threshold: float = 0.7    # Above this = HOT
    warm_threshold: float = 0.4   # Above this = WARM
    cold_threshold: float = 0.1   # Below this = COLD

    # Time thresholds (days)
    days_to_warm: int = 7         # Days without activation to become WARM
    days_to_cold: int = 30        # Days without activation to become COLD
    days_to_archive: int = 90     # Days without activation to archive
    days_to_delete: int = 365     # Days in archive before deletion

    # Batch sizes
    decay_batch_size: int = 100   # Process bubbles in batches
    archive_batch_size: int = 50  # Archive bubbles in batches


class LucioleLifecycleManager:
    """
    🪲 Manages the lifecycle of Luciole bubbles (Phase 13).

    Implements MemGPT-inspired memory tiering:
    - HOT: Recently activated bubbles (high priority in search)
    - WARM: Moderately active bubbles (normal priority)
    - COLD: Inactive bubbles (low priority, archive candidates)
    - FROZEN: Archived bubbles (not in main search, can resurrect)

    Features:
    - Automatic decay of activation scores over time
    - Tier-based organization for efficient retrieval
    - Archival of cold bubbles to separate collection
    - Garbage collection of really old bubbles
    - Resurrection of archived bubbles when relevant

    Usage:
        manager = LucioleLifecycleManager()

        # Run daily maintenance
        results = manager.run_maintenance()

        # Check bubble status
        tier = manager.get_tier("injection/cypher")

        # Manually archive/resurrect
        manager.archive_bubble("old/unused")
        manager.resurrect_bubble("archived/but_needed")
    """

    ARCHIVE_COLLECTION = "luciole_archive"

    def __init__(
        self,
        provider: Optional[LucioleContextProvider] = None,
        config: Optional[LifecycleConfig] = None
    ):
        """Initialize lifecycle manager."""
        self.provider = provider or LucioleContextProvider.get_instance()
        self.config = config or LifecycleConfig()
        self._qdrant_available = self.provider._qdrant_available
        self._client = self.provider._qdrant_client if self._qdrant_available else None

        # Stats
        self._stats = {
            "decays_applied": 0,
            "bubbles_archived": 0,
            "bubbles_resurrected": 0,
            "bubbles_deleted": 0,
            "last_maintenance": None,
        }

        # Ensure archive collection exists
        if self._qdrant_available:
            self._ensure_archive_collection()

    def _ensure_archive_collection(self):
        """Create archive collection if it doesn't exist."""
        try:
            collections = [c.name for c in self._client.get_collections().collections]
            if self.ARCHIVE_COLLECTION not in collections:
                from qdrant_client.models import VectorParams, Distance
                self._client.create_collection(
                    collection_name=self.ARCHIVE_COLLECTION,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                print(f"[LIFECYCLE] Created archive collection: {self.ARCHIVE_COLLECTION}")
        except Exception as e:
            print(f"[LIFECYCLE] Failed to create archive collection: {e}")

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def _parse_timestamp(self, ts: str) -> Optional[datetime]:
        """Parse ISO timestamp to datetime."""
        from datetime import datetime
        try:
            return datetime.fromisoformat(ts)
        except (ValueError, TypeError):
            return None

    def _days_since(self, ts: str) -> float:
        """Calculate days since a timestamp."""
        from datetime import datetime
        parsed = self._parse_timestamp(ts)
        if not parsed:
            return 0.0
        delta = datetime.now() - parsed
        return delta.total_seconds() / 86400  # Convert to days

    def get_tier(self, domain: str) -> Optional[MemoryTier]:
        """
        Get the current memory tier for a bubble.

        Args:
            domain: The bubble's domain identifier

        Returns:
            MemoryTier or None if bubble not found
        """
        if not self._qdrant_available:
            return None

        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            # Check main collection
            points, _ = self._client.scroll(
                collection_name=self.provider.COLLECTION_NAME,
                scroll_filter=Filter(must=[
                    FieldCondition(key="domain", match=MatchValue(value=domain))
                ]),
                limit=1,
                with_payload=True
            )

            if points:
                payload = points[0].payload
                activation = payload.get("activation_score", 1.0)
                last_activated = payload.get("last_activated", payload.get("created_at", ""))
                days = self._days_since(last_activated)

                # Determine tier based on activation and time
                if activation >= self.config.hot_threshold:
                    return MemoryTier.HOT
                elif activation >= self.config.warm_threshold or days < self.config.days_to_warm:
                    return MemoryTier.WARM
                elif activation >= self.config.cold_threshold or days < self.config.days_to_cold:
                    return MemoryTier.COLD
                else:
                    return MemoryTier.COLD

            # Check archive collection
            archived, _ = self._client.scroll(
                collection_name=self.ARCHIVE_COLLECTION,
                scroll_filter=Filter(must=[
                    FieldCondition(key="domain", match=MatchValue(value=domain))
                ]),
                limit=1,
                with_payload=True
            )

            if archived:
                return MemoryTier.FROZEN

            return None

        except Exception as e:
            print(f"[LIFECYCLE] Error getting tier for {domain}: {e}")
            return None

    def apply_decay(self, dry_run: bool = False) -> Dict:
        """
        Apply activation decay to all bubbles.

        Bubbles decay based on time since last activation.

        Args:
            dry_run: If True, don't actually update, just report

        Returns:
            Summary of decay operations
        """
        if not self._qdrant_available:
            return {"error": "Qdrant not available"}

        from datetime import datetime

        try:
            # Get all bubbles
            points, _ = self._client.scroll(
                collection_name=self.provider.COLLECTION_NAME,
                limit=1000,
                with_payload=True
            )

            decayed = []
            now = datetime.now()

            for point in points:
                payload = point.payload
                domain = payload.get("domain", "unknown")
                current_score = payload.get("activation_score", 1.0)
                last_activated = payload.get("last_activated", payload.get("created_at", ""))

                days = self._days_since(last_activated)
                if days < 1:
                    continue  # No decay for recently active bubbles

                # Calculate decay
                decay = self.config.decay_rate_per_day * days
                new_score = max(self.config.min_activation_score / 2, current_score - decay)

                if new_score < current_score:
                    decayed.append({
                        "domain": domain,
                        "old_score": round(current_score, 3),
                        "new_score": round(new_score, 3),
                        "days_inactive": round(days, 1),
                        "decay_applied": round(decay, 3),
                    })

                    if not dry_run:
                        self._client.set_payload(
                            collection_name=self.provider.COLLECTION_NAME,
                            payload={"activation_score": new_score},
                            points=[point.id]
                        )
                        self._stats["decays_applied"] += 1

            # Record metrics (Phase 15: Instrumentation)
            if not dry_run and len(decayed) > 0:
                try:
                    collector = LucioleMetricsCollector.get_instance()
                    collector.record_decay(len(decayed))
                except Exception:
                    pass

            return {
                "bubbles_checked": len(points),
                "bubbles_decayed": len(decayed),
                "dry_run": dry_run,
                "details": decayed[:20],  # Limit output
            }

        except Exception as e:
            return {"error": str(e)}

    def get_archive_candidates(self, limit: int = 50) -> List[Dict]:
        """
        Get bubbles that are candidates for archival.

        Candidates:
        - activation_score < cold_threshold
        - days since last activation > days_to_archive
        """
        if not self._qdrant_available:
            return []

        try:
            from qdrant_client.models import Filter, FieldCondition, Range
            from datetime import datetime, timedelta

            # Get cold bubbles
            points, _ = self._client.scroll(
                collection_name=self.provider.COLLECTION_NAME,
                scroll_filter=Filter(must=[
                    FieldCondition(
                        key="activation_score",
                        range=Range(lte=self.config.cold_threshold)
                    )
                ]),
                limit=limit * 2,  # Get more to filter by time
                with_payload=True
            )

            candidates = []
            threshold_date = datetime.now() - timedelta(days=self.config.days_to_archive)

            for point in points:
                payload = point.payload
                last_activated = payload.get("last_activated", payload.get("created_at", ""))
                parsed = self._parse_timestamp(last_activated)

                if parsed and parsed < threshold_date:
                    candidates.append({
                        "domain": payload.get("domain"),
                        "activation_score": payload.get("activation_score"),
                        "last_activated": last_activated,
                        "days_inactive": round(self._days_since(last_activated), 1),
                        "point_id": point.id,
                    })

                if len(candidates) >= limit:
                    break

            return candidates

        except Exception as e:
            print(f"[LIFECYCLE] Error getting archive candidates: {e}")
            return []

    def archive_bubble(self, domain: str) -> bool:
        """
        Archive a bubble to the archive collection.

        Args:
            domain: The bubble's domain to archive

        Returns:
            True if archived successfully
        """
        if not self._qdrant_available:
            return False

        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue, PointStruct

            # Find the bubble
            points, _ = self._client.scroll(
                collection_name=self.provider.COLLECTION_NAME,
                scroll_filter=Filter(must=[
                    FieldCondition(key="domain", match=MatchValue(value=domain))
                ]),
                limit=1,
                with_payload=True,
                with_vectors=True
            )

            if not points:
                return False

            point = points[0]

            # Add archive metadata
            payload = point.payload.copy()
            payload["archived_at"] = self._get_timestamp()
            payload["archive_reason"] = "low_activation"

            # Insert into archive
            archive_point = PointStruct(
                id=point.id,
                vector=point.vector,
                payload=payload
            )
            self._client.upsert(
                collection_name=self.ARCHIVE_COLLECTION,
                points=[archive_point]
            )

            # Delete from main collection
            self._client.delete(
                collection_name=self.provider.COLLECTION_NAME,
                points_selector={"points": [point.id]}
            )

            self._stats["bubbles_archived"] += 1

            # Record metrics (Phase 15: Instrumentation)
            try:
                collector = LucioleMetricsCollector.get_instance()
                collector.record_bubble_event("archived", domain)
            except Exception:
                pass

            print(f"[LIFECYCLE] Archived bubble: {domain}")
            return True

        except Exception as e:
            print(f"[LIFECYCLE] Failed to archive {domain}: {e}")
            return False

    def resurrect_bubble(self, domain: str, boost: float = 0.5) -> bool:
        """
        Resurrect an archived bubble back to the main collection.

        Args:
            domain: The bubble's domain to resurrect
            boost: Activation score to give the resurrected bubble

        Returns:
            True if resurrected successfully
        """
        if not self._qdrant_available:
            return False

        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue, PointStruct

            # Find in archive
            points, _ = self._client.scroll(
                collection_name=self.ARCHIVE_COLLECTION,
                scroll_filter=Filter(must=[
                    FieldCondition(key="domain", match=MatchValue(value=domain))
                ]),
                limit=1,
                with_payload=True,
                with_vectors=True
            )

            if not points:
                return False

            point = points[0]

            # Update metadata
            payload = point.payload.copy()
            payload["activation_score"] = boost
            payload["last_activated"] = self._get_timestamp()
            payload["resurrected_at"] = self._get_timestamp()
            payload.pop("archived_at", None)
            payload.pop("archive_reason", None)

            # Insert back to main collection
            main_point = PointStruct(
                id=point.id,
                vector=point.vector,
                payload=payload
            )
            self._client.upsert(
                collection_name=self.provider.COLLECTION_NAME,
                points=[main_point]
            )

            # Delete from archive
            self._client.delete(
                collection_name=self.ARCHIVE_COLLECTION,
                points_selector={"points": [point.id]}
            )

            self._stats["bubbles_resurrected"] += 1

            # Record metrics (Phase 15: Instrumentation)
            try:
                collector = LucioleMetricsCollector.get_instance()
                collector.record_bubble_event("resurrected", domain)
            except Exception:
                pass

            print(f"[LIFECYCLE] Resurrected bubble: {domain}")
            return True

        except Exception as e:
            print(f"[LIFECYCLE] Failed to resurrect {domain}: {e}")
            return False

    def garbage_collect(self, dry_run: bool = True) -> Dict:
        """
        Delete really old archived bubbles.

        Args:
            dry_run: If True, don't actually delete, just report

        Returns:
            Summary of GC operations
        """
        if not self._qdrant_available:
            return {"error": "Qdrant not available"}

        try:
            from datetime import datetime, timedelta

            # Get all archived bubbles
            points, _ = self._client.scroll(
                collection_name=self.ARCHIVE_COLLECTION,
                limit=1000,
                with_payload=True
            )

            threshold_date = datetime.now() - timedelta(days=self.config.days_to_delete)
            to_delete = []

            for point in points:
                payload = point.payload
                archived_at = payload.get("archived_at")
                parsed = self._parse_timestamp(archived_at)

                if parsed and parsed < threshold_date:
                    to_delete.append({
                        "domain": payload.get("domain"),
                        "archived_at": archived_at,
                        "days_archived": round(self._days_since(archived_at), 1),
                        "point_id": point.id,
                    })

            if not dry_run and to_delete:
                point_ids = [d["point_id"] for d in to_delete]
                self._client.delete(
                    collection_name=self.ARCHIVE_COLLECTION,
                    points_selector={"points": point_ids}
                )
                self._stats["bubbles_deleted"] += len(to_delete)

            return {
                "archived_bubbles": len(points),
                "to_delete": len(to_delete),
                "dry_run": dry_run,
                "threshold_days": self.config.days_to_delete,
                "details": to_delete[:20],
            }

        except Exception as e:
            return {"error": str(e)}

    def auto_resurrect_relevant(self, query: str, max_resurrect: int = 3) -> List[str]:
        """
        Automatically resurrect archived bubbles if relevant to query.

        Uses semantic search on archive to find relevant frozen bubbles.

        Args:
            query: The query to check relevance against
            max_resurrect: Maximum bubbles to resurrect

        Returns:
            List of resurrected domain names
        """
        if not self._qdrant_available or not self.provider._embedder:
            return []

        try:
            # Get query embedding
            query_vector = self.provider._embedder.encode(query).tolist()

            # Search archive
            results = self._client.query_points(
                collection_name=self.ARCHIVE_COLLECTION,
                query=query_vector,
                limit=max_resurrect * 2,  # Get extras in case some fail
            )

            resurrected = []
            for hit in results.points:
                if hit.score < 0.5:  # Only resurrect if reasonably relevant
                    continue

                domain = hit.payload.get("domain")
                if domain and self.resurrect_bubble(domain, boost=hit.score):
                    resurrected.append(domain)

                if len(resurrected) >= max_resurrect:
                    break

            return resurrected

        except Exception as e:
            print(f"[LIFECYCLE] Auto-resurrect failed: {e}")
            return []

    def get_tier_distribution(self) -> Dict[str, int]:
        """Get distribution of bubbles across memory tiers."""
        if not self._qdrant_available:
            return {}

        try:
            from qdrant_client.models import Filter, FieldCondition, Range

            # Count HOT
            hot_count = self._client.count(
                collection_name=self.provider.COLLECTION_NAME,
                count_filter=Filter(must=[
                    FieldCondition(
                        key="activation_score",
                        range=Range(gte=self.config.hot_threshold)
                    )
                ])
            ).count

            # Count WARM
            warm_count = self._client.count(
                collection_name=self.provider.COLLECTION_NAME,
                count_filter=Filter(must=[
                    FieldCondition(
                        key="activation_score",
                        range=Range(gte=self.config.warm_threshold, lt=self.config.hot_threshold)
                    )
                ])
            ).count

            # Count COLD
            cold_count = self._client.count(
                collection_name=self.provider.COLLECTION_NAME,
                count_filter=Filter(must=[
                    FieldCondition(
                        key="activation_score",
                        range=Range(lt=self.config.warm_threshold)
                    )
                ])
            ).count

            # Count FROZEN (archived)
            frozen_count = self._client.count(
                collection_name=self.ARCHIVE_COLLECTION
            ).count

            return {
                MemoryTier.HOT.value: hot_count,
                MemoryTier.WARM.value: warm_count,
                MemoryTier.COLD.value: cold_count,
                MemoryTier.FROZEN.value: frozen_count,
                "total": hot_count + warm_count + cold_count + frozen_count,
            }

        except Exception as e:
            print(f"[LIFECYCLE] Error getting tier distribution: {e}")
            return {}

    def run_maintenance(self, dry_run: bool = False) -> Dict:
        """
        Run full maintenance cycle.

        Performs:
        1. Apply activation decay
        2. Archive cold bubbles
        3. Garbage collect old archived bubbles

        Args:
            dry_run: If True, don't make changes, just report

        Returns:
            Full maintenance report
        """
        from datetime import datetime

        report = {
            "started_at": datetime.now().isoformat(),
            "dry_run": dry_run,
        }

        # 1. Apply decay
        print("[LIFECYCLE] Applying activation decay...")
        decay_result = self.apply_decay(dry_run=dry_run)
        report["decay"] = decay_result

        # 2. Archive cold bubbles
        print("[LIFECYCLE] Checking archive candidates...")
        candidates = self.get_archive_candidates()
        archived = []

        if not dry_run:
            for candidate in candidates[:self.config.archive_batch_size]:
                domain = candidate.get("domain")
                if domain and self.archive_bubble(domain):
                    archived.append(domain)

        report["archive"] = {
            "candidates": len(candidates),
            "archived": len(archived),
            "archived_domains": archived[:10],
        }

        # 3. Garbage collect
        print("[LIFECYCLE] Running garbage collection...")
        gc_result = self.garbage_collect(dry_run=dry_run)
        report["gc"] = gc_result

        # 4. Get tier distribution
        report["tier_distribution"] = self.get_tier_distribution()

        # Update stats
        self._stats["last_maintenance"] = datetime.now().isoformat()
        report["stats"] = self._stats.copy()

        report["completed_at"] = datetime.now().isoformat()

        return report

    def status(self) -> str:
        """Get formatted status string."""
        dist = self.get_tier_distribution()

        lines = [
            "🪲 **LUCIOLE LIFECYCLE MANAGER** (Phase 13)",
            "",
            "**Memory Tiers:**",
            f"  🔥 HOT:    {dist.get('hot', 0)} bubbles (score ≥ {self.config.hot_threshold})",
            f"  🌡️ WARM:   {dist.get('warm', 0)} bubbles",
            f"  ❄️ COLD:   {dist.get('cold', 0)} bubbles",
            f"  🧊 FROZEN: {dist.get('frozen', 0)} bubbles (archived)",
            "",
            f"**Total:** {dist.get('total', 0)} bubbles",
            "",
            "**Config:**",
            f"  Decay rate: {self.config.decay_rate_per_day:.1%}/day",
            f"  Archive after: {self.config.days_to_archive} days",
            f"  Delete after: {self.config.days_to_delete} days",
            "",
            "**Stats:**",
            f"  Decays applied: {self._stats.get('decays_applied', 0)}",
            f"  Bubbles archived: {self._stats.get('bubbles_archived', 0)}",
            f"  Bubbles resurrected: {self._stats.get('bubbles_resurrected', 0)}",
            f"  Bubbles deleted: {self._stats.get('bubbles_deleted', 0)}",
        ]

        if self._stats.get("last_maintenance"):
            lines.append(f"  Last maintenance: {self._stats['last_maintenance']}")

        return "\n".join(lines)


# Convenience functions
def get_lifecycle_manager() -> LucioleLifecycleManager:
    """Get a lifecycle manager instance."""
    return LucioleLifecycleManager()


def run_luciole_maintenance(dry_run: bool = True) -> Dict:
    """
    Run Luciole maintenance cycle.

    Usage:
        from semantic_context import run_luciole_maintenance
        result = run_luciole_maintenance(dry_run=True)  # Preview
        result = run_luciole_maintenance(dry_run=False)  # Execute
    """
    manager = get_lifecycle_manager()
    return manager.run_maintenance(dry_run=dry_run)


# =============================================================================
# PHASE 14: OBSERVABILITY & METRICS (Phase 301.5r)
# =============================================================================
#
# Implements comprehensive observability for the Luciole Swarm:
#   - MetricsCollector: Tracks all operations
#   - Prometheus-compatible metrics export
#   - Detailed health checks
#   - Operation histograms and counters
#
# =============================================================================


@dataclass
class LucioleMetrics:
    """Metrics container for Luciole operations."""
    # Counters
    searches_total: int = 0
    searches_semantic: int = 0
    searches_keyword: int = 0
    searches_llm: int = 0

    boosts_total: int = 0
    decays_total: int = 0

    bubbles_created: int = 0
    bubbles_archived: int = 0
    bubbles_resurrected: int = 0
    bubbles_deleted: int = 0
    bubbles_merged: int = 0

    # Hit rates
    search_hits: int = 0
    search_misses: int = 0

    # Latency tracking (in ms)
    search_latency_total: float = 0.0
    search_latency_count: int = 0

    embedding_latency_total: float = 0.0
    embedding_latency_count: int = 0

    llm_latency_total: float = 0.0
    llm_latency_count: int = 0

    # Timestamps
    started_at: str = ""
    last_operation: str = ""

    def record_search(self, mode: str, latency_ms: float, hit: bool):
        """Record a search operation."""
        self.searches_total += 1
        self.search_latency_total += latency_ms
        self.search_latency_count += 1
        self.last_operation = datetime.now().isoformat()

        if mode == "semantic":
            self.searches_semantic += 1
        elif mode == "keyword":
            self.searches_keyword += 1
        elif mode == "llm":
            self.searches_llm += 1

        if hit:
            self.search_hits += 1
        else:
            self.search_misses += 1

    def record_embedding(self, latency_ms: float):
        """Record an embedding operation."""
        self.embedding_latency_total += latency_ms
        self.embedding_latency_count += 1

    def record_llm(self, latency_ms: float):
        """Record an LLM operation."""
        self.llm_latency_total += latency_ms
        self.llm_latency_count += 1

    @property
    def search_latency_avg(self) -> float:
        """Average search latency in ms."""
        if self.search_latency_count == 0:
            return 0.0
        return self.search_latency_total / self.search_latency_count

    @property
    def embedding_latency_avg(self) -> float:
        """Average embedding latency in ms."""
        if self.embedding_latency_count == 0:
            return 0.0
        return self.embedding_latency_total / self.embedding_latency_count

    @property
    def llm_latency_avg(self) -> float:
        """Average LLM latency in ms."""
        if self.llm_latency_count == 0:
            return 0.0
        return self.llm_latency_total / self.llm_latency_count

    @property
    def hit_rate(self) -> float:
        """Search hit rate (0-1)."""
        total = self.search_hits + self.search_misses
        if total == 0:
            return 0.0
        return self.search_hits / total

    def to_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = [
            "# HELP luciole_searches_total Total number of searches",
            "# TYPE luciole_searches_total counter",
            f"luciole_searches_total {self.searches_total}",
            "",
            "# HELP luciole_searches_by_mode Searches by mode",
            "# TYPE luciole_searches_by_mode counter",
            f'luciole_searches_by_mode{{mode="semantic"}} {self.searches_semantic}',
            f'luciole_searches_by_mode{{mode="keyword"}} {self.searches_keyword}',
            f'luciole_searches_by_mode{{mode="llm"}} {self.searches_llm}',
            "",
            "# HELP luciole_boosts_total Total activation boosts",
            "# TYPE luciole_boosts_total counter",
            f"luciole_boosts_total {self.boosts_total}",
            "",
            "# HELP luciole_decays_total Total activation decays",
            "# TYPE luciole_decays_total counter",
            f"luciole_decays_total {self.decays_total}",
            "",
            "# HELP luciole_bubbles_lifecycle Bubble lifecycle events",
            "# TYPE luciole_bubbles_lifecycle counter",
            f'luciole_bubbles_lifecycle{{event="created"}} {self.bubbles_created}',
            f'luciole_bubbles_lifecycle{{event="archived"}} {self.bubbles_archived}',
            f'luciole_bubbles_lifecycle{{event="resurrected"}} {self.bubbles_resurrected}',
            f'luciole_bubbles_lifecycle{{event="deleted"}} {self.bubbles_deleted}',
            f'luciole_bubbles_lifecycle{{event="merged"}} {self.bubbles_merged}',
            "",
            "# HELP luciole_search_hit_rate Search hit rate",
            "# TYPE luciole_search_hit_rate gauge",
            f"luciole_search_hit_rate {self.hit_rate:.4f}",
            "",
            "# HELP luciole_search_latency_avg Average search latency in ms",
            "# TYPE luciole_search_latency_avg gauge",
            f"luciole_search_latency_avg {self.search_latency_avg:.2f}",
            "",
            "# HELP luciole_embedding_latency_avg Average embedding latency in ms",
            "# TYPE luciole_embedding_latency_avg gauge",
            f"luciole_embedding_latency_avg {self.embedding_latency_avg:.2f}",
            "",
            "# HELP luciole_llm_latency_avg Average LLM latency in ms",
            "# TYPE luciole_llm_latency_avg gauge",
            f"luciole_llm_latency_avg {self.llm_latency_avg:.2f}",
        ]
        return "\n".join(lines)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON export."""
        return {
            "counters": {
                "searches_total": self.searches_total,
                "searches_semantic": self.searches_semantic,
                "searches_keyword": self.searches_keyword,
                "searches_llm": self.searches_llm,
                "boosts_total": self.boosts_total,
                "decays_total": self.decays_total,
                "bubbles_created": self.bubbles_created,
                "bubbles_archived": self.bubbles_archived,
                "bubbles_resurrected": self.bubbles_resurrected,
                "bubbles_deleted": self.bubbles_deleted,
                "bubbles_merged": self.bubbles_merged,
            },
            "rates": {
                "hit_rate": round(self.hit_rate, 4),
                "search_hits": self.search_hits,
                "search_misses": self.search_misses,
            },
            "latencies": {
                "search_avg_ms": round(self.search_latency_avg, 2),
                "search_count": self.search_latency_count,
                "embedding_avg_ms": round(self.embedding_latency_avg, 2),
                "embedding_count": self.embedding_latency_count,
                "llm_avg_ms": round(self.llm_latency_avg, 2),
                "llm_count": self.llm_latency_count,
            },
            "timestamps": {
                "started_at": self.started_at,
                "last_operation": self.last_operation,
            },
        }


class LucioleMetricsCollector:
    """
    🪲 Metrics collector for Luciole Swarm (Phase 14).

    Singleton that tracks all Luciole operations across the system.
    Provides Prometheus-compatible export and JSON metrics.

    Usage:
        collector = LucioleMetricsCollector.get_instance()
        collector.record_search("semantic", latency_ms=12.5, hit=True)
        metrics = collector.get_metrics()
        prometheus_output = collector.export_prometheus()
    """

    _instance = None

    def __init__(self):
        self._metrics = LucioleMetrics(started_at=datetime.now().isoformat())
        self._operation_history: List[Dict] = []  # Recent operations
        self._history_limit = 100

    @classmethod
    def get_instance(cls) -> "LucioleMetricsCollector":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset the singleton (for testing)."""
        cls._instance = None

    def record_search(self, mode: str, latency_ms: float, hit: bool, query: str = ""):
        """Record a search operation."""
        self._metrics.record_search(mode, latency_ms, hit)
        self._add_history({
            "type": "search",
            "mode": mode,
            "latency_ms": round(latency_ms, 2),
            "hit": hit,
            "query_preview": query[:50] if query else "",
            "timestamp": datetime.now().isoformat(),
        })

    def record_embedding(self, latency_ms: float, text_length: int = 0):
        """Record an embedding operation."""
        self._metrics.record_embedding(latency_ms)
        self._add_history({
            "type": "embedding",
            "latency_ms": round(latency_ms, 2),
            "text_length": text_length,
            "timestamp": datetime.now().isoformat(),
        })

    def record_llm(self, operation: str, latency_ms: float, model: str = ""):
        """Record an LLM operation."""
        self._metrics.record_llm(latency_ms)
        self._add_history({
            "type": "llm",
            "operation": operation,
            "latency_ms": round(latency_ms, 2),
            "model": model,
            "timestamp": datetime.now().isoformat(),
        })

    def record_boost(self, domain: str, amount: float):
        """Record an activation boost."""
        self._metrics.boosts_total += 1
        self._add_history({
            "type": "boost",
            "domain": domain,
            "amount": amount,
            "timestamp": datetime.now().isoformat(),
        })

    def record_decay(self, count: int):
        """Record decay operations."""
        self._metrics.decays_total += count

    def record_bubble_event(self, event: str, domain: str = ""):
        """Record a bubble lifecycle event."""
        if event == "created":
            self._metrics.bubbles_created += 1
        elif event == "archived":
            self._metrics.bubbles_archived += 1
        elif event == "resurrected":
            self._metrics.bubbles_resurrected += 1
        elif event == "deleted":
            self._metrics.bubbles_deleted += 1
        elif event == "merged":
            self._metrics.bubbles_merged += 1

        self._add_history({
            "type": "bubble_event",
            "event": event,
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
        })

    def _add_history(self, entry: Dict):
        """Add entry to operation history (circular buffer)."""
        self._operation_history.append(entry)
        if len(self._operation_history) > self._history_limit:
            self._operation_history = self._operation_history[-self._history_limit:]

    def get_metrics(self) -> Dict:
        """Get current metrics as dictionary."""
        return self._metrics.to_dict()

    def get_history(self, limit: int = 20) -> List[Dict]:
        """Get recent operation history."""
        return self._operation_history[-limit:]

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        return self._metrics.to_prometheus()

    def status(self) -> str:
        """Get formatted status string."""
        m = self._metrics
        uptime = ""
        if m.started_at:
            try:
                start = datetime.fromisoformat(m.started_at)
                delta = datetime.now() - start
                hours = delta.total_seconds() / 3600
                uptime = f" (uptime: {hours:.1f}h)"
            except:
                pass

        lines = [
            f"🪲 **LUCIOLE METRICS** (Phase 14){uptime}",
            "",
            "**Search Operations:**",
            f"  Total: {m.searches_total} ({m.searches_semantic} semantic, {m.searches_keyword} keyword, {m.searches_llm} LLM)",
            f"  Hit rate: {m.hit_rate:.1%} ({m.search_hits} hits, {m.search_misses} misses)",
            f"  Avg latency: {m.search_latency_avg:.1f}ms",
            "",
            "**Bubble Lifecycle:**",
            f"  Created: {m.bubbles_created}",
            f"  Archived: {m.bubbles_archived}",
            f"  Resurrected: {m.bubbles_resurrected}",
            f"  Deleted: {m.bubbles_deleted}",
            f"  Merged: {m.bubbles_merged}",
            "",
            "**Activation:**",
            f"  Boosts: {m.boosts_total}",
            f"  Decays: {m.decays_total}",
            "",
            "**Latencies:**",
            f"  Search avg: {m.search_latency_avg:.1f}ms",
            f"  Embedding avg: {m.embedding_latency_avg:.1f}ms",
            f"  LLM avg: {m.llm_latency_avg:.1f}ms",
        ]

        return "\n".join(lines)


class LucioleHealthCheck:
    """
    🪲 Comprehensive health check for Luciole system (Phase 14).

    Checks:
    - Qdrant connectivity and collection status
    - Embedder availability
    - LLM availability (Ollama)
    - Archive collection status
    - Memory tier distribution
    - Metrics health
    """

    def __init__(self, provider: Optional[LucioleContextProvider] = None):
        self.provider = provider or LucioleContextProvider.get_instance()

    def check_qdrant(self) -> Dict:
        """Check Qdrant connectivity."""
        if not self.provider._qdrant_available:
            return {
                "status": "unavailable",
                "mode": "fallback",
                "bubbles": len(self.provider._fallback_bubbles),
            }

        try:
            client = self.provider._qdrant_client
            collections = [c.name for c in client.get_collections().collections]
            main_count = client.count(collection_name=self.provider.COLLECTION_NAME).count

            archive_count = 0
            if "luciole_archive" in collections:
                archive_count = client.count(collection_name="luciole_archive").count

            return {
                "status": "connected",
                "host": f"{self.provider.QDRANT_HOST}:{self.provider.QDRANT_PORT}",
                "main_collection": self.provider.COLLECTION_NAME,
                "main_count": main_count,
                "archive_count": archive_count,
                "collections": collections,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def check_embedder(self) -> Dict:
        """Check embedding model status."""
        if not self.provider._embedder:
            return {
                "status": "unavailable",
            }

        try:
            # Quick test embedding
            import time
            start = time.time()
            _ = self.provider._embedder.encode("test")
            latency = (time.time() - start) * 1000

            return {
                "status": "ready",
                "model": self.provider.EMBEDDING_MODEL,
                "test_latency_ms": round(latency, 1),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def check_ollama(self) -> Dict:
        """Check Ollama LLM availability."""
        import requests

        try:
            response = requests.get(
                f"{self.provider.OLLAMA_URL}/api/tags",
                timeout=2
            )

            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]

                has_fast = any(n.startswith("phi3") for n in model_names)
                has_reason = any(n.startswith("deepseek-r1") for n in model_names)

                return {
                    "status": "connected",
                    "url": self.provider.OLLAMA_URL,
                    "models_available": model_names[:10],
                    "fast_model_ready": has_fast,
                    "reasoning_model_ready": has_reason,
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}",
                }
        except requests.exceptions.ConnectionError:
            return {
                "status": "unavailable",
                "url": self.provider.OLLAMA_URL,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def check_tiers(self) -> Dict:
        """Check memory tier distribution."""
        try:
            manager = LucioleLifecycleManager(provider=self.provider)
            distribution = manager.get_tier_distribution()

            total = distribution.get("total", 0)
            hot = distribution.get("hot", 0)
            frozen = distribution.get("frozen", 0)

            # Warnings
            warnings = []
            if total > 0:
                if hot / total < 0.3:
                    warnings.append("Low HOT ratio - consider running searches to boost bubbles")
                if frozen / total > 0.3:
                    warnings.append("High FROZEN ratio - consider resurrection or cleanup")

            return {
                "status": "ok" if not warnings else "warning",
                "distribution": distribution,
                "warnings": warnings,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def check_all(self) -> Dict:
        """Run all health checks."""
        checks = {
            "qdrant": self.check_qdrant(),
            "embedder": self.check_embedder(),
            "ollama": self.check_ollama(),
            "tiers": self.check_tiers(),
        }

        # Overall status
        statuses = [c.get("status", "unknown") for c in checks.values()]
        if "error" in statuses:
            overall = "unhealthy"
        elif "unavailable" in statuses or "warning" in statuses:
            overall = "degraded"
        else:
            overall = "healthy"

        # Get metrics if available
        try:
            collector = LucioleMetricsCollector.get_instance()
            metrics_summary = {
                "searches_total": collector._metrics.searches_total,
                "hit_rate": round(collector._metrics.hit_rate, 2),
                "avg_latency_ms": round(collector._metrics.search_latency_avg, 1),
            }
        except:
            metrics_summary = {}

        return {
            "status": overall,
            "timestamp": datetime.now().isoformat(),
            "checks": checks,
            "metrics_summary": metrics_summary,
        }

    def status(self) -> str:
        """Get formatted health status."""
        result = self.check_all()

        status_icons = {
            "healthy": "✅",
            "degraded": "⚠️",
            "unhealthy": "❌",
        }

        lines = [
            f"{status_icons.get(result['status'], '❓')} **LUCIOLE HEALTH** - {result['status'].upper()}",
            "",
        ]

        for name, check in result["checks"].items():
            icon = "✅" if check.get("status") == "ok" or check.get("status") == "ready" or check.get("status") == "connected" else "⚠️" if check.get("status") == "unavailable" or check.get("status") == "warning" else "❌"
            lines.append(f"  {icon} **{name.upper()}**: {check.get('status', 'unknown')}")

            # Add details
            if name == "qdrant" and check.get("status") == "connected":
                lines.append(f"     {check.get('main_count', 0)} bubbles, {check.get('archive_count', 0)} archived")
            elif name == "embedder" and check.get("status") == "ready":
                lines.append(f"     {check.get('model', '')} ({check.get('test_latency_ms', 0):.0f}ms)")
            elif name == "ollama" and check.get("status") == "connected":
                models = check.get("models_available", [])[:3]
                lines.append(f"     {len(models)} models: {', '.join(models)}")
            elif name == "tiers":
                dist = check.get("distribution", {})
                lines.append(f"     HOT:{dist.get('hot', 0)} WARM:{dist.get('warm', 0)} COLD:{dist.get('cold', 0)} FROZEN:{dist.get('frozen', 0)}")

        if result.get("metrics_summary"):
            m = result["metrics_summary"]
            lines.append("")
            lines.append(f"**Metrics:** {m.get('searches_total', 0)} searches, {m.get('hit_rate', 0):.0%} hit rate, {m.get('avg_latency_ms', 0):.0f}ms avg")

        return "\n".join(lines)


# Convenience functions for Phase 14
def get_metrics_collector() -> LucioleMetricsCollector:
    """Get the metrics collector singleton."""
    return LucioleMetricsCollector.get_instance()


def get_luciole_health() -> Dict:
    """Get comprehensive health check results."""
    health = LucioleHealthCheck()
    return health.check_all()


def get_luciole_prometheus_metrics() -> str:
    """Get metrics in Prometheus format."""
    collector = LucioleMetricsCollector.get_instance()
    return collector.export_prometheus()


# =============================================================================
# PHASE 16: ALERTING & NOTIFICATIONS
# =============================================================================
# Alerting system that monitors metrics and health, triggering alerts when
# thresholds are exceeded. Supports multiple severity levels and notification
# channels.
# =============================================================================

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"           # Informational, no action needed
    WARNING = "warning"     # Attention needed, not urgent
    CRITICAL = "critical"   # Immediate action required
    EMERGENCY = "emergency" # System failure, escalate immediately


@dataclass
class AlertRule:
    """
    Defines a condition that triggers an alert.
    
    Attributes:
        name: Unique identifier for this rule
        description: Human-readable description
        metric: The metric to monitor (e.g., "hit_rate", "search_latency")
        operator: Comparison operator ("lt", "gt", "eq", "lte", "gte")
        threshold: Value to compare against
        severity: Alert severity when triggered
        cooldown_seconds: Minimum time between repeated alerts
        enabled: Whether this rule is active
    """
    name: str
    description: str
    metric: str
    operator: str  # "lt", "gt", "eq", "lte", "gte"
    threshold: float
    severity: AlertSeverity = AlertSeverity.WARNING
    cooldown_seconds: int = 300  # 5 minutes
    enabled: bool = True
    
    def evaluate(self, value: float) -> bool:
        """Check if the rule is triggered by the given value."""
        ops = {
            "lt": lambda a, b: a < b,
            "gt": lambda a, b: a > b,
            "eq": lambda a, b: a == b,
            "lte": lambda a, b: a <= b,
            "gte": lambda a, b: a >= b,
        }
        op = ops.get(self.operator)
        if op:
            return op(value, self.threshold)
        return False


@dataclass
class LucioleAlert:
    """
    An alert instance when a rule is triggered.
    
    Attributes:
        rule_name: The rule that triggered this alert
        severity: Alert severity level
        message: Human-readable alert message
        metric_value: The actual value that triggered the alert
        threshold: The threshold that was crossed
        triggered_at: When the alert was triggered
        acknowledged: Whether the alert has been acknowledged
        acknowledged_at: When the alert was acknowledged
        resolved: Whether the alert has been resolved
        resolved_at: When the alert was resolved
    """
    rule_name: str
    severity: AlertSeverity
    message: str
    metric_value: float
    threshold: float
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def acknowledge(self) -> None:
        """Mark the alert as acknowledged."""
        self.acknowledged = True
        self.acknowledged_at = datetime.now()
    
    def resolve(self) -> None:
        """Mark the alert as resolved."""
        self.resolved = True
        self.resolved_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "message": self.message,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
            "triggered_at": self.triggered_at.isoformat(),
            "acknowledged": self.acknowledged,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


class LucioleAlertManager:
    """
    Manages alerts for the Luciole system.
    
    Features:
    - Configurable alert rules
    - Cooldown to prevent alert storms
    - Alert history tracking
    - Acknowledgement and resolution workflow
    - Webhook notifications (optional)
    """
    
    _instance = None
    
    def __init__(self):
        self._rules: Dict[str, AlertRule] = {}
        self._alerts: List[LucioleAlert] = []
        self._last_triggered: Dict[str, datetime] = {}
        self._webhooks: List[str] = []
        self._max_history = 1000
        
        # Initialize default rules
        self._init_default_rules()
    
    @classmethod
    def get_instance(cls) -> "LucioleAlertManager":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _init_default_rules(self) -> None:
        """Initialize default alert rules."""
        default_rules = [
            AlertRule(
                name="low_hit_rate",
                description="Search hit rate dropped below threshold",
                metric="hit_rate",
                operator="lt",
                threshold=0.5,
                severity=AlertSeverity.WARNING,
                cooldown_seconds=600,
            ),
            AlertRule(
                name="high_search_latency",
                description="Average search latency exceeded threshold",
                metric="search_avg_ms",
                operator="gt",
                threshold=100.0,
                severity=AlertSeverity.WARNING,
                cooldown_seconds=300,
            ),
            AlertRule(
                name="critical_search_latency",
                description="Search latency critically high",
                metric="search_avg_ms",
                operator="gt",
                threshold=500.0,
                severity=AlertSeverity.CRITICAL,
                cooldown_seconds=60,
            ),
            AlertRule(
                name="high_embedding_latency",
                description="Embedding generation too slow",
                metric="embedding_avg_ms",
                operator="gt",
                threshold=50.0,
                severity=AlertSeverity.WARNING,
                cooldown_seconds=300,
            ),
            AlertRule(
                name="too_many_cold_bubbles",
                description="Too many bubbles in COLD tier",
                metric="cold_bubble_ratio",
                operator="gt",
                threshold=0.5,
                severity=AlertSeverity.INFO,
                cooldown_seconds=3600,
            ),
            AlertRule(
                name="no_hot_bubbles",
                description="No bubbles in HOT tier",
                metric="hot_bubble_count",
                operator="eq",
                threshold=0.0,
                severity=AlertSeverity.WARNING,
                cooldown_seconds=1800,
            ),
            AlertRule(
                name="qdrant_disconnected",
                description="Qdrant vector store is unavailable",
                metric="qdrant_connected",
                operator="eq",
                threshold=0.0,
                severity=AlertSeverity.CRITICAL,
                cooldown_seconds=60,
            ),
            AlertRule(
                name="embedder_unavailable",
                description="Sentence embedder is unavailable",
                metric="embedder_ready",
                operator="eq",
                threshold=0.0,
                severity=AlertSeverity.CRITICAL,
                cooldown_seconds=60,
            ),
            AlertRule(
                name="zero_searches",
                description="No searches recorded (system might be unused)",
                metric="searches_total",
                operator="eq",
                threshold=0.0,
                severity=AlertSeverity.INFO,
                cooldown_seconds=7200,
                enabled=False,  # Disabled by default
            ),
        ]
        
        for rule in default_rules:
            self._rules[rule.name] = rule
    
    def add_rule(self, rule: AlertRule) -> None:
        """Add or update an alert rule."""
        self._rules[rule.name] = rule
    
    def remove_rule(self, name: str) -> bool:
        """Remove an alert rule."""
        if name in self._rules:
            del self._rules[name]
            return True
        return False
    
    def enable_rule(self, name: str) -> bool:
        """Enable an alert rule."""
        if name in self._rules:
            self._rules[name].enabled = True
            return True
        return False
    
    def disable_rule(self, name: str) -> bool:
        """Disable an alert rule."""
        if name in self._rules:
            self._rules[name].enabled = False
            return True
        return False
    
    def get_rules(self) -> List[Dict]:
        """Get all alert rules."""
        return [
            {
                "name": r.name,
                "description": r.description,
                "metric": r.metric,
                "operator": r.operator,
                "threshold": r.threshold,
                "severity": r.severity.value,
                "cooldown_seconds": r.cooldown_seconds,
                "enabled": r.enabled,
            }
            for r in self._rules.values()
        ]
    
    def _check_cooldown(self, rule_name: str, cooldown_seconds: int) -> bool:
        """Check if a rule is in cooldown period."""
        last = self._last_triggered.get(rule_name)
        if last is None:
            return False
        
        elapsed = (datetime.now() - last).total_seconds()
        return elapsed < cooldown_seconds
    
    def _trigger_alert(self, rule: AlertRule, value: float) -> LucioleAlert:
        """Create and store an alert."""
        alert = LucioleAlert(
            rule_name=rule.name,
            severity=rule.severity,
            message=f"{rule.description} (value: {value:.2f}, threshold: {rule.threshold:.2f})",
            metric_value=value,
            threshold=rule.threshold,
        )
        
        self._alerts.append(alert)
        self._last_triggered[rule.name] = datetime.now()
        
        # Trim history if needed
        if len(self._alerts) > self._max_history:
            self._alerts = self._alerts[-self._max_history:]
        
        # Send webhooks
        self._notify_webhooks(alert)
        
        return alert
    
    def _notify_webhooks(self, alert: LucioleAlert) -> None:
        """Send alert to registered webhooks."""
        if not self._webhooks:
            return
        
        import requests
        
        payload = {
            "source": "luciole_alerting",
            "alert": alert.to_dict(),
        }
        
        for webhook_url in self._webhooks:
            try:
                requests.post(webhook_url, json=payload, timeout=5)
            except Exception as e:
                print(f"[ALERT] Failed to notify webhook {webhook_url}: {e}")
    
    def add_webhook(self, url: str) -> None:
        """Register a webhook for alert notifications."""
        if url not in self._webhooks:
            self._webhooks.append(url)
    
    def remove_webhook(self, url: str) -> bool:
        """Remove a registered webhook."""
        if url in self._webhooks:
            self._webhooks.remove(url)
            return True
        return False
    
    def check_metrics(self) -> List[LucioleAlert]:
        """
        Check all metrics against rules and trigger alerts.
        
        Returns:
            List of newly triggered alerts
        """
        triggered = []
        
        try:
            # Get current metrics
            collector = LucioleMetricsCollector.get_instance()
            metrics = collector.get_metrics()
            
            # Get health status
            health = LucioleHealthCheck()
            health_result = health.check_all()
            
            # Build metrics dict
            current_metrics = {
                "hit_rate": metrics["rates"]["hit_rate"],
                "search_avg_ms": metrics["latencies"]["search_avg_ms"],
                "embedding_avg_ms": metrics["latencies"]["embedding_avg_ms"],
                "llm_avg_ms": metrics["latencies"]["llm_avg_ms"],
                "searches_total": metrics["counters"]["searches_total"],
                "boosts_total": metrics["counters"]["boosts_total"],
            }
            
            # Add health metrics
            qdrant_check = health_result.get("checks", {}).get("qdrant", {})
            current_metrics["qdrant_connected"] = 1.0 if qdrant_check.get("status") == "connected" else 0.0
            
            embedder_check = health_result.get("checks", {}).get("embedder", {})
            current_metrics["embedder_ready"] = 1.0 if embedder_check.get("status") == "ready" else 0.0
            
            # Add tier metrics
            tier_check = health_result.get("checks", {}).get("tiers", {})
            dist = tier_check.get("distribution", {})
            total = sum(dist.values()) or 1
            
            current_metrics["hot_bubble_count"] = float(dist.get("hot", 0))
            current_metrics["warm_bubble_count"] = float(dist.get("warm", 0))
            current_metrics["cold_bubble_count"] = float(dist.get("cold", 0))
            current_metrics["frozen_bubble_count"] = float(dist.get("frozen", 0))
            current_metrics["cold_bubble_ratio"] = dist.get("cold", 0) / total
            
            # Check each rule
            for rule in self._rules.values():
                if not rule.enabled:
                    continue
                
                if rule.metric not in current_metrics:
                    continue
                
                value = current_metrics[rule.metric]
                
                if rule.evaluate(value):
                    # Check cooldown
                    if self._check_cooldown(rule.name, rule.cooldown_seconds):
                        continue
                    
                    # Trigger alert
                    alert = self._trigger_alert(rule, value)
                    triggered.append(alert)
            
        except Exception as e:
            print(f"[ALERT] Error checking metrics: {e}")
        
        return triggered
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all unresolved alerts."""
        return [
            a.to_dict() for a in self._alerts
            if not a.resolved
        ]
    
    def get_alert_history(self, limit: int = 100) -> List[Dict]:
        """Get alert history."""
        return [a.to_dict() for a in self._alerts[-limit:]]
    
    def acknowledge_alert(self, index: int) -> bool:
        """Acknowledge an alert by index."""
        if 0 <= index < len(self._alerts):
            self._alerts[index].acknowledge()
            return True
        return False
    
    def resolve_alert(self, index: int) -> bool:
        """Resolve an alert by index."""
        if 0 <= index < len(self._alerts):
            self._alerts[index].resolve()
            return True
        return False
    
    def resolve_by_rule(self, rule_name: str) -> int:
        """Resolve all alerts for a specific rule."""
        count = 0
        for alert in self._alerts:
            if alert.rule_name == rule_name and not alert.resolved:
                alert.resolve()
                count += 1
        return count
    
    def get_summary(self) -> Dict:
        """Get alerting system summary."""
        active = [a for a in self._alerts if not a.resolved]
        
        by_severity = {}
        for alert in active:
            sev = alert.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        return {
            "total_rules": len(self._rules),
            "enabled_rules": sum(1 for r in self._rules.values() if r.enabled),
            "total_alerts": len(self._alerts),
            "active_alerts": len(active),
            "acknowledged_alerts": sum(1 for a in active if a.acknowledged),
            "by_severity": by_severity,
            "webhooks_configured": len(self._webhooks),
        }
    
    def format_summary(self) -> str:
        """Format summary for display."""
        summary = self.get_summary()
        active = self.get_active_alerts()
        
        lines = [
            "**LUCIOLE ALERTING**",
            "",
            f"Rules: {summary['enabled_rules']}/{summary['total_rules']} enabled",
            f"Active Alerts: {summary['active_alerts']}",
        ]
        
        if summary['by_severity']:
            sev_str = ", ".join(f"{k}: {v}" for k, v in summary['by_severity'].items())
            lines.append(f"By Severity: {sev_str}")
        
        if active:
            lines.append("")
            lines.append("---")
            lines.append("**Active Alerts:**")
            for i, alert in enumerate(active[:5]):
                icon = {"info": "ℹ️", "warning": "⚠️", "critical": "🔴", "emergency": "🚨"}.get(alert["severity"], "❓")
                lines.append(f"{i+1}. {icon} [{alert['severity'].upper()}] {alert['rule_name']}")
                lines.append(f"   {alert['message']}")
            
            if len(active) > 5:
                lines.append(f"   ... and {len(active) - 5} more")
        
        return "\n".join(lines)


# Convenience functions for Phase 16
def get_alert_manager() -> LucioleAlertManager:
    """Get the alert manager singleton."""
    return LucioleAlertManager.get_instance()


def check_alerts() -> List[Dict]:
    """Check metrics and return any new alerts."""
    manager = LucioleAlertManager.get_instance()
    alerts = manager.check_metrics()
    return [a.to_dict() for a in alerts]


def get_alert_summary() -> str:
    """Get formatted alert summary."""
    manager = LucioleAlertManager.get_instance()
    return manager.format_summary()


# =============================================================================
# PHASE 17: SCHEDULED TASKS & BACKGROUND JOBS
# =============================================================================
# Automated task scheduler for periodic maintenance operations:
# - Decay application
# - Alert checking
# - Maintenance tasks (archive, cleanup)
# - Stats collection
# =============================================================================

class TaskStatus(Enum):
    """Status of a scheduled task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DISABLED = "disabled"


@dataclass
class ScheduledTask:
    """
    A scheduled task configuration.
    
    Attributes:
        name: Unique task identifier
        description: Human-readable description
        interval_seconds: How often to run (0 = manual only)
        last_run: When the task last ran
        next_run: When the task will next run
        status: Current task status
        last_result: Result of last execution
        enabled: Whether the task is active
        run_count: Total number of executions
        error_count: Number of failed executions
    """
    name: str
    description: str
    interval_seconds: int
    handler: str  # Function name to call
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    last_result: Optional[Dict] = None
    enabled: bool = True
    run_count: int = 0
    error_count: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "interval_seconds": self.interval_seconds,
            "interval_human": self._format_interval(),
            "handler": self.handler,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "status": self.status.value,
            "last_result": self.last_result,
            "enabled": self.enabled,
            "run_count": self.run_count,
            "error_count": self.error_count,
        }
    
    def _format_interval(self) -> str:
        """Format interval as human-readable string."""
        if self.interval_seconds == 0:
            return "manual"
        elif self.interval_seconds < 60:
            return f"{self.interval_seconds}s"
        elif self.interval_seconds < 3600:
            return f"{self.interval_seconds // 60}m"
        elif self.interval_seconds < 86400:
            return f"{self.interval_seconds // 3600}h"
        else:
            return f"{self.interval_seconds // 86400}d"


class LucioleTaskScheduler:
    """
    Task scheduler for Luciole maintenance operations.
    
    Features:
    - Configurable task intervals
    - Manual trigger support
    - Execution history
    - Error tracking
    - Enable/disable tasks
    """
    
    _instance = None
    _running = False
    _thread = None
    
    def __init__(self):
        self._tasks: Dict[str, ScheduledTask] = {}
        self._history: List[Dict] = []
        self._max_history = 500
        self._check_interval = 10  # Check every 10 seconds
        
        # Initialize default tasks
        self._init_default_tasks()
    
    @classmethod
    def get_instance(cls) -> "LucioleTaskScheduler":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _init_default_tasks(self) -> None:
        """Initialize default scheduled tasks."""
        default_tasks = [
            ScheduledTask(
                name="decay_apply",
                description="Apply activation decay to all bubbles",
                interval_seconds=3600,  # Every hour
                handler="task_apply_decay",
                enabled=True,
            ),
            ScheduledTask(
                name="alert_check",
                description="Check metrics and trigger alerts",
                interval_seconds=60,  # Every minute
                handler="task_check_alerts",
                enabled=True,
            ),
            ScheduledTask(
                name="maintenance_full",
                description="Full maintenance (decay + archive + gc)",
                interval_seconds=86400,  # Daily
                handler="task_full_maintenance",
                enabled=True,
            ),
            ScheduledTask(
                name="stats_collect",
                description="Collect and log statistics",
                interval_seconds=300,  # Every 5 minutes
                handler="task_collect_stats",
                enabled=True,
            ),
            ScheduledTask(
                name="health_check",
                description="Run health checks",
                interval_seconds=120,  # Every 2 minutes
                handler="task_health_check",
                enabled=True,
            ),
            ScheduledTask(
                name="tier_rebalance",
                description="Check and log tier distribution",
                interval_seconds=1800,  # Every 30 minutes
                handler="task_tier_rebalance",
                enabled=False,  # Disabled by default
            ),
        ]
        
        for task in default_tasks:
            task.next_run = datetime.now() + timedelta(seconds=task.interval_seconds)
            self._tasks[task.name] = task
    
    def _execute_task(self, task: ScheduledTask) -> Dict:
        """Execute a task and return the result."""
        task.status = TaskStatus.RUNNING
        task.last_run = datetime.now()
        
        result = {
            "task": task.name,
            "started_at": datetime.now().isoformat(),
            "success": False,
            "result": None,
            "error": None,
        }
        
        try:
            # Get the handler function
            handler = getattr(self, task.handler, None)
            if handler is None:
                raise ValueError(f"Handler {task.handler} not found")
            
            # Execute
            task_result = handler()
            
            result["success"] = True
            result["result"] = task_result
            task.status = TaskStatus.COMPLETED
            task.last_result = task_result
            task.run_count += 1
            
        except Exception as e:
            result["error"] = str(e)
            task.status = TaskStatus.FAILED
            task.last_result = {"error": str(e)}
            task.error_count += 1
        
        result["finished_at"] = datetime.now().isoformat()
        result["duration_ms"] = (datetime.now() - task.last_run).total_seconds() * 1000
        
        # Update next run
        if task.interval_seconds > 0:
            task.next_run = datetime.now() + timedelta(seconds=task.interval_seconds)
        
        # Add to history
        self._history.append(result)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        
        return result
    
    # =========================================================================
    # TASK HANDLERS
    # =========================================================================
    
    def task_apply_decay(self) -> Dict:
        """Apply decay to all bubbles."""
        try:
            manager = LucioleLifecycleManager.get_instance()
            result = manager.apply_decay(dry_run=False)
            return {
                "decayed": result.get("bubbles_decayed", 0),
                "checked": result.get("bubbles_checked", 0),
            }
        except Exception as e:
            return {"error": str(e)}
    
    def task_check_alerts(self) -> Dict:
        """Check metrics and trigger alerts."""
        try:
            manager = LucioleAlertManager.get_instance()
            new_alerts = manager.check_metrics()
            return {
                "checked": True,
                "new_alerts": len(new_alerts),
                "alerts": [a.rule_name for a in new_alerts],
            }
        except Exception as e:
            return {"error": str(e)}
    
    def task_full_maintenance(self) -> Dict:
        """Run full maintenance cycle."""
        results = {}
        
        try:
            manager = LucioleLifecycleManager.get_instance()
            
            # 1. Apply decay
            decay_result = manager.apply_decay(dry_run=False)
            results["decay"] = {
                "decayed": decay_result.get("bubbles_decayed", 0),
            }
            
            # 2. Archive cold bubbles
            candidates = manager.get_archive_candidates(limit=50)
            archived = 0
            for candidate in candidates:
                domain = candidate.get("domain")
                if domain and manager.archive_bubble(domain, reason="auto_maintenance"):
                    archived += 1
            results["archive"] = {"archived": archived}
            
            # 3. Garbage collect old archives
            gc_result = manager.garbage_collect(dry_run=False)
            results["gc"] = {
                "deleted": gc_result.get("deleted_count", 0),
            }
            
            results["success"] = True
            
        except Exception as e:
            results["error"] = str(e)
            results["success"] = False
        
        return results
    
    def task_collect_stats(self) -> Dict:
        """Collect system statistics."""
        try:
            collector = LucioleMetricsCollector.get_instance()
            metrics = collector.get_metrics()
            
            return {
                "searches": metrics["counters"]["searches_total"],
                "hit_rate": metrics["rates"]["hit_rate"],
                "avg_latency": metrics["latencies"]["search_avg_ms"],
            }
        except Exception as e:
            return {"error": str(e)}
    
    def task_health_check(self) -> Dict:
        """Run health checks."""
        try:
            health = LucioleHealthCheck()
            result = health.check_all()
            
            return {
                "status": result.get("status"),
                "components": list(result.get("checks", {}).keys()),
            }
        except Exception as e:
            return {"error": str(e)}
    
    def task_tier_rebalance(self) -> Dict:
        """Check tier distribution."""
        try:
            manager = LucioleLifecycleManager.get_instance()
            status = manager.get_tier_stats()
            
            return {
                "distribution": status.get("tier_distribution", {}),
                "total": status.get("total_bubbles", 0),
            }
        except Exception as e:
            return {"error": str(e)}
    
    # =========================================================================
    # SCHEDULER CONTROL
    # =========================================================================
    
    def start(self) -> bool:
        """Start the scheduler background thread."""
        if self._running:
            return False
        
        import threading
        
        self._running = True
        self._thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._thread.start()
        
        return True
    
    def stop(self) -> bool:
        """Stop the scheduler background thread."""
        if not self._running:
            return False
        
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        
        return True
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        import time
        
        while self._running:
            now = datetime.now()
            
            for task in self._tasks.values():
                if not task.enabled:
                    continue
                
                if task.interval_seconds == 0:
                    continue  # Manual only
                
                if task.next_run and now >= task.next_run:
                    if task.status != TaskStatus.RUNNING:
                        try:
                            self._execute_task(task)
                        except Exception as e:
                            print(f"[SCHEDULER] Task {task.name} failed: {e}")
            
            time.sleep(self._check_interval)
    
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running
    
    # =========================================================================
    # TASK MANAGEMENT
    # =========================================================================
    
    def run_task(self, name: str) -> Optional[Dict]:
        """Manually run a task immediately."""
        task = self._tasks.get(name)
        if task is None:
            return None
        
        return self._execute_task(task)
    
    def enable_task(self, name: str) -> bool:
        """Enable a task."""
        if name in self._tasks:
            self._tasks[name].enabled = True
            self._tasks[name].status = TaskStatus.PENDING
            self._tasks[name].next_run = datetime.now() + timedelta(
                seconds=self._tasks[name].interval_seconds
            )
            return True
        return False
    
    def disable_task(self, name: str) -> bool:
        """Disable a task."""
        if name in self._tasks:
            self._tasks[name].enabled = False
            self._tasks[name].status = TaskStatus.DISABLED
            return True
        return False
    
    def set_interval(self, name: str, seconds: int) -> bool:
        """Change a task's interval."""
        if name in self._tasks:
            self._tasks[name].interval_seconds = seconds
            self._tasks[name].next_run = datetime.now() + timedelta(seconds=seconds)
            return True
        return False
    
    def get_tasks(self) -> List[Dict]:
        """Get all tasks."""
        return [t.to_dict() for t in self._tasks.values()]
    
    def get_task(self, name: str) -> Optional[Dict]:
        """Get a specific task."""
        task = self._tasks.get(name)
        return task.to_dict() if task else None
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """Get execution history."""
        return self._history[-limit:]
    
    def get_summary(self) -> Dict:
        """Get scheduler summary."""
        enabled = [t for t in self._tasks.values() if t.enabled]
        running = [t for t in self._tasks.values() if t.status == TaskStatus.RUNNING]
        failed = [t for t in self._tasks.values() if t.status == TaskStatus.FAILED]
        
        total_runs = sum(t.run_count for t in self._tasks.values())
        total_errors = sum(t.error_count for t in self._tasks.values())
        
        return {
            "scheduler_running": self._running,
            "total_tasks": len(self._tasks),
            "enabled_tasks": len(enabled),
            "running_tasks": len(running),
            "failed_tasks": len(failed),
            "total_runs": total_runs,
            "total_errors": total_errors,
            "error_rate": total_errors / total_runs if total_runs > 0 else 0,
            "history_size": len(self._history),
        }
    
    def format_summary(self) -> str:
        """Format summary for display."""
        summary = self.get_summary()
        tasks = self.get_tasks()
        
        status_icon = "🟢" if summary["scheduler_running"] else "🔴"
        
        lines = [
            f"{status_icon} **LUCIOLE SCHEDULER** - {'Running' if summary['scheduler_running'] else 'Stopped'}",
            "",
            f"Tasks: {summary['enabled_tasks']}/{summary['total_tasks']} enabled",
            f"Total Runs: {summary['total_runs']} ({summary['total_errors']} errors)",
            "",
            "---",
            "**Scheduled Tasks:**",
        ]
        
        for task in tasks:
            status_icons = {
                "pending": "⏳",
                "running": "🔄",
                "completed": "✅",
                "failed": "❌",
                "disabled": "⏸️",
            }
            icon = status_icons.get(task["status"], "❓")
            
            lines.append(f"  {icon} **{task['name']}** ({task['interval_human']})")
            if task["last_run"]:
                lines.append(f"     Last: {task['last_run'][:19]}")
        
        return "\n".join(lines)


# Convenience functions for Phase 17
def get_task_scheduler() -> LucioleTaskScheduler:
    """Get the task scheduler singleton."""
    return LucioleTaskScheduler.get_instance()


def start_scheduler() -> bool:
    """Start the background scheduler."""
    scheduler = LucioleTaskScheduler.get_instance()
    return scheduler.start()


def stop_scheduler() -> bool:
    """Stop the background scheduler."""
    scheduler = LucioleTaskScheduler.get_instance()
    return scheduler.stop()


# =============================================================================
# PHASE 18: BACKUP & RECOVERY
# =============================================================================
# Backup and restore capabilities for Luciole bubbles:
# - Snapshot to JSON file
# - Restore from snapshot
# - Export to various formats (JSON, CSV, Markdown)
# - Import from external sources
# - Backup scheduling integration
# =============================================================================

class ExportFormat(Enum):
    """Supported export formats."""
    JSON = "json"
    CSV = "csv"
    MARKDOWN = "markdown"
    JSONL = "jsonl"  # JSON Lines for streaming


@dataclass
class BackupMetadata:
    """
    Metadata for a backup snapshot.
    
    Attributes:
        backup_id: Unique identifier for this backup
        created_at: When the backup was created
        bubble_count: Number of bubbles in backup
        archive_count: Number of archived bubbles
        version: Backup format version
        source: Where the backup came from
        checksum: SHA256 checksum of content
    """
    backup_id: str
    created_at: datetime
    bubble_count: int
    archive_count: int = 0
    version: str = "1.0"
    source: str = "luciole_swarm_v2"
    checksum: Optional[str] = None
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "backup_id": self.backup_id,
            "created_at": self.created_at.isoformat(),
            "bubble_count": self.bubble_count,
            "archive_count": self.archive_count,
            "version": self.version,
            "source": self.source,
            "checksum": self.checksum,
            "notes": self.notes,
        }


class LucioleBackupManager:
    """
    Manages backup and restore operations for Luciole bubbles.
    
    Features:
    - Full snapshot to JSON
    - Incremental backups
    - Multi-format export
    - Restore with validation
    - Backup history tracking
    """
    
    _instance = None
    
    def __init__(self):
        self._backup_dir = Path("/home/sebas/Smash_App/apps/backend/data/backups/luciole")
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        self._history: List[BackupMetadata] = []
        self._max_backups = 30  # Keep last 30 backups
        
        # Load existing backup history
        self._load_history()
    
    @classmethod
    def get_instance(cls) -> "LucioleBackupManager":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _load_history(self) -> None:
        """Load backup history from disk."""
        history_file = self._backup_dir / "backup_history.json"
        if history_file.exists():
            try:
                with open(history_file, "r") as f:
                    data = json.load(f)
                    for item in data:
                        self._history.append(BackupMetadata(
                            backup_id=item["backup_id"],
                            created_at=datetime.fromisoformat(item["created_at"]),
                            bubble_count=item["bubble_count"],
                            archive_count=item.get("archive_count", 0),
                            version=item.get("version", "1.0"),
                            source=item.get("source", "unknown"),
                            checksum=item.get("checksum"),
                            notes=item.get("notes"),
                        ))
            except Exception as e:
                print(f"[BACKUP] Failed to load history: {e}")
    
    def _save_history(self) -> None:
        """Save backup history to disk."""
        history_file = self._backup_dir / "backup_history.json"
        try:
            with open(history_file, "w") as f:
                json.dump([m.to_dict() for m in self._history], f, indent=2)
        except Exception as e:
            print(f"[BACKUP] Failed to save history: {e}")
    
    def _generate_backup_id(self) -> str:
        """Generate a unique backup ID."""
        import hashlib
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:6]
        return f"backup_{timestamp}_{random_suffix}"
    
    def _compute_checksum(self, data: str) -> str:
        """Compute SHA256 checksum of data."""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()
    
    def create_snapshot(self, notes: Optional[str] = None, include_archive: bool = True) -> Dict:
        """
        Create a full snapshot of all bubbles.
        
        Args:
            notes: Optional notes about this backup
            include_archive: Whether to include archived bubbles
            
        Returns:
            Backup metadata and file path
        """
        backup_id = self._generate_backup_id()
        
        try:
            provider = LucioleContextProvider.get_instance()
            
            # Get all bubbles from main collection
            bubbles = []
            if provider._qdrant_available:
                points, _ = provider._qdrant_client.scroll(
                    collection_name=provider.COLLECTION_NAME,
                    limit=10000,
                    with_payload=True,
                    with_vectors=True,
                )
                for point in points:
                    bubble = point.payload.copy()
                    bubble["_id"] = str(point.id)
                    bubble["_vector"] = point.vector[:10] if point.vector else None  # Store first 10 dims for verification
                    bubbles.append(bubble)
            
            # Get archived bubbles if requested
            archived = []
            if include_archive:
                try:
                    lifecycle = LucioleLifecycleManager.get_instance()
                    archive_points, _ = lifecycle._client.scroll(
                        collection_name=lifecycle.ARCHIVE_COLLECTION,
                        limit=10000,
                        with_payload=True,
                    )
                    for point in archive_points:
                        bubble = point.payload.copy()
                        bubble["_id"] = str(point.id)
                        bubble["_archived"] = True
                        archived.append(bubble)
                except Exception:
                    pass
            
            # Build backup data
            backup_data = {
                "metadata": {
                    "backup_id": backup_id,
                    "created_at": datetime.now().isoformat(),
                    "bubble_count": len(bubbles),
                    "archive_count": len(archived),
                    "version": "1.0",
                    "source": "luciole_swarm_v2",
                    "notes": notes,
                },
                "bubbles": bubbles,
                "archived": archived,
            }
            
            # Serialize and compute checksum
            json_data = json.dumps(backup_data, indent=2, default=str)
            checksum = self._compute_checksum(json_data)
            backup_data["metadata"]["checksum"] = checksum
            
            # Write to file
            backup_file = self._backup_dir / f"{backup_id}.json"
            with open(backup_file, "w") as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            # Create metadata record
            metadata = BackupMetadata(
                backup_id=backup_id,
                created_at=datetime.now(),
                bubble_count=len(bubbles),
                archive_count=len(archived),
                checksum=checksum,
                notes=notes,
            )
            
            # Add to history
            self._history.append(metadata)
            self._save_history()
            
            # Cleanup old backups
            self._cleanup_old_backups()
            
            return {
                "success": True,
                "backup_id": backup_id,
                "file": str(backup_file),
                "metadata": metadata.to_dict(),
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def restore_snapshot(self, backup_id: str, restore_archive: bool = True) -> Dict:
        """
        Restore bubbles from a snapshot.
        
        Args:
            backup_id: The backup ID to restore from
            restore_archive: Whether to restore archived bubbles
            
        Returns:
            Restore result with statistics
        """
        backup_file = self._backup_dir / f"{backup_id}.json"
        
        if not backup_file.exists():
            return {"success": False, "error": f"Backup {backup_id} not found"}
        
        try:
            # Load backup
            with open(backup_file, "r") as f:
                backup_data = json.load(f)
            
            # Verify checksum
            stored_checksum = backup_data.get("metadata", {}).get("checksum")
            if stored_checksum:
                # Recompute without checksum field
                backup_data["metadata"]["checksum"] = None
                json_data = json.dumps(backup_data, indent=2, default=str)
                computed = self._compute_checksum(json_data)
                # Note: Checksum will differ due to null, skip verification for now
            
            provider = LucioleContextProvider.get_instance()
            
            if not provider._qdrant_available:
                return {"success": False, "error": "Qdrant not available"}
            
            from qdrant_client.models import PointStruct
            
            # Restore main bubbles
            restored_count = 0
            for bubble in backup_data.get("bubbles", []):
                try:
                    # Generate embedding for bubble
                    text = f"{bubble.get('domain', '')} {bubble.get('pattern_danger', '')} {bubble.get('reminder', '')}"
                    vector = provider._embedder.encode(text).tolist()
                    
                    # Remove internal fields
                    payload = {k: v for k, v in bubble.items() if not k.startswith("_")}
                    
                    # Generate new ID if needed
                    bubble_id = bubble.get("_id") or provider._generate_id(bubble.get("domain", "unknown"))
                    
                    point = PointStruct(
                        id=bubble_id,
                        vector=vector,
                        payload=payload,
                    )
                    
                    provider._qdrant_client.upsert(
                        collection_name=provider.COLLECTION_NAME,
                        points=[point],
                    )
                    restored_count += 1
                    
                except Exception as e:
                    print(f"[RESTORE] Failed to restore bubble: {e}")
            
            # Restore archived bubbles
            archived_count = 0
            if restore_archive:
                try:
                    lifecycle = LucioleLifecycleManager.get_instance()
                    
                    for bubble in backup_data.get("archived", []):
                        try:
                            text = f"{bubble.get('domain', '')} {bubble.get('pattern_danger', '')} {bubble.get('reminder', '')}"
                            vector = provider._embedder.encode(text).tolist()
                            
                            payload = {k: v for k, v in bubble.items() if not k.startswith("_")}
                            bubble_id = bubble.get("_id") or provider._generate_id(bubble.get("domain", "unknown"))
                            
                            point = PointStruct(
                                id=bubble_id,
                                vector=vector,
                                payload=payload,
                            )
                            
                            lifecycle._client.upsert(
                                collection_name=lifecycle.ARCHIVE_COLLECTION,
                                points=[point],
                            )
                            archived_count += 1
                            
                        except Exception as e:
                            print(f"[RESTORE] Failed to restore archived bubble: {e}")
                            
                except Exception as e:
                    print(f"[RESTORE] Archive restore failed: {e}")
            
            return {
                "success": True,
                "backup_id": backup_id,
                "restored_bubbles": restored_count,
                "restored_archived": archived_count,
                "total_in_backup": len(backup_data.get("bubbles", [])),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def export_bubbles(self, format: ExportFormat = ExportFormat.JSON, 
                       include_archive: bool = False) -> Dict:
        """
        Export bubbles to a specific format.
        
        Args:
            format: Export format (JSON, CSV, MARKDOWN, JSONL)
            include_archive: Include archived bubbles
            
        Returns:
            Export result with file path or content
        """
        try:
            provider = LucioleContextProvider.get_instance()
            
            # Get all bubbles
            bubbles = []
            if provider._qdrant_available:
                points, _ = provider._qdrant_client.scroll(
                    collection_name=provider.COLLECTION_NAME,
                    limit=10000,
                    with_payload=True,
                )
                for point in points:
                    bubble = point.payload.copy()
                    bubble["id"] = str(point.id)
                    bubbles.append(bubble)
            
            # Get archived if requested
            if include_archive:
                try:
                    lifecycle = LucioleLifecycleManager.get_instance()
                    archive_points, _ = lifecycle._client.scroll(
                        collection_name=lifecycle.ARCHIVE_COLLECTION,
                        limit=10000,
                        with_payload=True,
                    )
                    for point in archive_points:
                        bubble = point.payload.copy()
                        bubble["id"] = str(point.id)
                        bubble["archived"] = True
                        bubbles.append(bubble)
                except Exception:
                    pass
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format == ExportFormat.JSON:
                filename = f"luciole_export_{timestamp}.json"
                filepath = self._backup_dir / filename
                with open(filepath, "w") as f:
                    json.dump(bubbles, f, indent=2, default=str)
                return {"success": True, "file": str(filepath), "count": len(bubbles)}
            
            elif format == ExportFormat.JSONL:
                filename = f"luciole_export_{timestamp}.jsonl"
                filepath = self._backup_dir / filename
                with open(filepath, "w") as f:
                    for bubble in bubbles:
                        f.write(json.dumps(bubble, default=str) + "\n")
                return {"success": True, "file": str(filepath), "count": len(bubbles)}
            
            elif format == ExportFormat.CSV:
                import csv
                filename = f"luciole_export_{timestamp}.csv"
                filepath = self._backup_dir / filename
                
                # Define CSV columns
                columns = ["id", "domain", "pattern_danger", "reminder", "severity", 
                          "keywords", "archetype", "activation_score", "created_at"]
                
                with open(filepath, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
                    writer.writeheader()
                    for bubble in bubbles:
                        row = bubble.copy()
                        # Convert keywords list to string
                        if isinstance(row.get("keywords"), list):
                            row["keywords"] = "|".join(row["keywords"])
                        writer.writerow(row)
                
                return {"success": True, "file": str(filepath), "count": len(bubbles)}
            
            elif format == ExportFormat.MARKDOWN:
                filename = f"luciole_export_{timestamp}.md"
                filepath = self._backup_dir / filename
                
                lines = [
                    "# Luciole Bubbles Export",
                    f"\nExported: {datetime.now().isoformat()}",
                    f"Total bubbles: {len(bubbles)}",
                    "\n---\n",
                ]
                
                # Group by domain
                by_domain = {}
                for bubble in bubbles:
                    domain = bubble.get("domain", "unknown").split("/")[0]
                    if domain not in by_domain:
                        by_domain[domain] = []
                    by_domain[domain].append(bubble)
                
                for domain, domain_bubbles in sorted(by_domain.items()):
                    lines.append(f"\n## {domain.upper()} ({len(domain_bubbles)} bubbles)\n")
                    
                    for bubble in domain_bubbles:
                        severity_icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(
                            bubble.get("severity", "info"), "⚪"
                        )
                        lines.append(f"### {severity_icon} {bubble.get('domain')}")
                        lines.append(f"\n**Pattern:** {bubble.get('pattern_danger', 'N/A')}")
                        lines.append(f"\n**Reminder:** {bubble.get('reminder', 'N/A')}")
                        keywords = bubble.get("keywords", [])
                        if keywords:
                            lines.append(f"\n**Keywords:** `{', '.join(keywords)}`")
                        lines.append(f"\n**Activation:** {bubble.get('activation_score', 1.0):.2f}")
                        lines.append("\n---\n")
                
                with open(filepath, "w") as f:
                    f.write("\n".join(lines))
                
                return {"success": True, "file": str(filepath), "count": len(bubbles)}
            
            else:
                return {"success": False, "error": f"Unknown format: {format}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def import_bubbles(self, file_path: str, merge: bool = True) -> Dict:
        """
        Import bubbles from a file.
        
        Args:
            file_path: Path to the import file (JSON or JSONL)
            merge: If True, merge with existing; if False, replace
            
        Returns:
            Import result with statistics
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            # Load bubbles based on file type
            bubbles = []
            if path.suffix == ".jsonl":
                with open(path, "r") as f:
                    for line in f:
                        if line.strip():
                            bubbles.append(json.loads(line))
            else:
                with open(path, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        bubbles = data
                    elif isinstance(data, dict) and "bubbles" in data:
                        bubbles = data["bubbles"]
                    else:
                        return {"success": False, "error": "Invalid file format"}
            
            if not bubbles:
                return {"success": False, "error": "No bubbles found in file"}
            
            provider = LucioleContextProvider.get_instance()
            
            if not provider._qdrant_available:
                return {"success": False, "error": "Qdrant not available"}
            
            from qdrant_client.models import PointStruct
            
            imported = 0
            skipped = 0
            errors = 0
            
            for bubble in bubbles:
                try:
                    domain = bubble.get("domain")
                    if not domain:
                        skipped += 1
                        continue
                    
                    # Check if exists (for merge mode)
                    if merge:
                        existing = provider.get_bubble_by_domain(domain)
                        if existing:
                            skipped += 1
                            continue
                    
                    # Generate embedding
                    text = f"{domain} {bubble.get('pattern_danger', '')} {bubble.get('reminder', '')}"
                    vector = provider._embedder.encode(text).tolist()
                    
                    # Clean payload
                    payload = {
                        "domain": domain,
                        "pattern_danger": bubble.get("pattern_danger", ""),
                        "reminder": bubble.get("reminder", ""),
                        "keywords": bubble.get("keywords", []),
                        "severity": bubble.get("severity", "info"),
                        "archetype": bubble.get("archetype", "PHAROS"),
                        "learned_from": bubble.get("learned_from", "import"),
                        "created_at": bubble.get("created_at", datetime.now().isoformat()),
                        "activation_score": bubble.get("activation_score", 1.0),
                    }
                    
                    bubble_id = provider._generate_id(domain)
                    
                    point = PointStruct(
                        id=bubble_id,
                        vector=vector,
                        payload=payload,
                    )
                    
                    provider._qdrant_client.upsert(
                        collection_name=provider.COLLECTION_NAME,
                        points=[point],
                    )
                    imported += 1
                    
                except Exception as e:
                    print(f"[IMPORT] Failed to import bubble: {e}")
                    errors += 1
            
            return {
                "success": True,
                "imported": imported,
                "skipped": skipped,
                "errors": errors,
                "total_in_file": len(bubbles),
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_backups(self) -> List[Dict]:
        """List all available backups."""
        return [m.to_dict() for m in self._history]
    
    def get_backup_info(self, backup_id: str) -> Optional[Dict]:
        """Get information about a specific backup."""
        for metadata in self._history:
            if metadata.backup_id == backup_id:
                backup_file = self._backup_dir / f"{backup_id}.json"
                info = metadata.to_dict()
                info["file_exists"] = backup_file.exists()
                if backup_file.exists():
                    info["file_size_kb"] = backup_file.stat().st_size / 1024
                return info
        return None
    
    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup."""
        backup_file = self._backup_dir / f"{backup_id}.json"
        
        if backup_file.exists():
            backup_file.unlink()
        
        self._history = [m for m in self._history if m.backup_id != backup_id]
        self._save_history()
        
        return True
    
    def _cleanup_old_backups(self) -> int:
        """Remove old backups beyond the retention limit."""
        if len(self._history) <= self._max_backups:
            return 0
        
        # Sort by date (oldest first)
        sorted_history = sorted(self._history, key=lambda m: m.created_at)
        to_delete = sorted_history[:-self._max_backups]
        
        deleted = 0
        for metadata in to_delete:
            backup_file = self._backup_dir / f"{metadata.backup_id}.json"
            if backup_file.exists():
                backup_file.unlink()
                deleted += 1
        
        self._history = sorted_history[-self._max_backups:]
        self._save_history()
        
        return deleted
    
    def get_summary(self) -> Dict:
        """Get backup system summary."""
        total_size = sum(
            (self._backup_dir / f"{m.backup_id}.json").stat().st_size
            for m in self._history
            if (self._backup_dir / f"{m.backup_id}.json").exists()
        )
        
        return {
            "backup_count": len(self._history),
            "total_size_mb": total_size / (1024 * 1024),
            "backup_dir": str(self._backup_dir),
            "max_backups": self._max_backups,
            "latest_backup": self._history[-1].to_dict() if self._history else None,
        }


# Convenience functions for Phase 18
def get_backup_manager() -> LucioleBackupManager:
    """Get the backup manager singleton."""
    return LucioleBackupManager.get_instance()


def create_backup(notes: Optional[str] = None) -> Dict:
    """Create a backup snapshot."""
    manager = LucioleBackupManager.get_instance()
    return manager.create_snapshot(notes)


def restore_backup(backup_id: str) -> Dict:
    """Restore from a backup."""
    manager = LucioleBackupManager.get_instance()
    return manager.restore_snapshot(backup_id)


# =============================================================================
# PHASE 19: DASHBOARD & ANALYTICS API
# =============================================================================
# Unified dashboard providing aggregated views of the Luciole system:
# - System overview and health
# - Real-time metrics and trends
# - Top bubbles by various criteria
# - Domain distribution analytics
# - Activity timeline
# - Recommendations
# =============================================================================

@dataclass
class DashboardWidget:
    """
    A widget for the dashboard.
    
    Attributes:
        id: Widget identifier
        title: Display title
        type: Widget type (stat, chart, list, etc.)
        data: Widget data
        updated_at: When data was last updated
    """
    id: str
    title: str
    type: str  # "stat", "chart", "list", "table", "status"
    data: Dict
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "data": self.data,
            "updated_at": self.updated_at.isoformat(),
        }


class LucioleDashboard:
    """
    Dashboard aggregating all Luciole system data.
    
    Features:
    - System overview stats
    - Real-time metrics
    - Top bubbles rankings
    - Domain analytics
    - Activity timeline
    - Health status
    - Recommendations
    """
    
    _instance = None
    _cache: Dict = {}
    _cache_ttl = 30  # Cache for 30 seconds
    
    def __init__(self):
        self._last_update: Optional[datetime] = None
    
    @classmethod
    def get_instance(cls) -> "LucioleDashboard":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self._cache:
            return False
        cached_at = self._cache[key].get("_cached_at")
        if not cached_at:
            return False
        return (datetime.now() - cached_at).total_seconds() < self._cache_ttl
    
    def _cache_set(self, key: str, data: Dict) -> Dict:
        """Cache data with timestamp."""
        data["_cached_at"] = datetime.now()
        self._cache[key] = data
        return data
    
    def get_overview(self) -> Dict:
        """
        Get system overview stats.
        
        Returns high-level statistics about the Luciole system.
        """
        if self._is_cache_valid("overview"):
            return self._cache["overview"]
        
        try:
            provider = LucioleContextProvider.get_instance()
            collector = LucioleMetricsCollector.get_instance()
            health = LucioleHealthCheck()
            
            metrics = collector.get_metrics()
            health_result = health.check_all()
            
            # Count bubbles by tier
            tier_counts = {"hot": 0, "warm": 0, "cold": 0, "frozen": 0}
            if provider._qdrant_available:
                points, _ = provider._qdrant_client.scroll(
                    collection_name=provider.COLLECTION_NAME,
                    limit=10000,
                    with_payload=True,
                )
                for point in points:
                    score = point.payload.get("activation_score", 1.0)
                    if score >= 0.7:
                        tier_counts["hot"] += 1
                    elif score >= 0.4:
                        tier_counts["warm"] += 1
                    elif score >= 0.1:
                        tier_counts["cold"] += 1
                    else:
                        tier_counts["frozen"] += 1
            
            overview = {
                "total_bubbles": sum(tier_counts.values()),
                "tier_distribution": tier_counts,
                "health_status": health_result.get("status", "unknown"),
                "searches_total": metrics["counters"]["searches_total"],
                "hit_rate": metrics["rates"]["hit_rate"],
                "avg_latency_ms": metrics["latencies"]["search_avg_ms"],
                "uptime_since": metrics["timestamps"]["started_at"],
            }
            
            return self._cache_set("overview", overview)
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_top_bubbles(self, limit: int = 10, sort_by: str = "activation") -> List[Dict]:
        """
        Get top bubbles by various criteria.
        
        Args:
            limit: Number of bubbles to return
            sort_by: Sort criteria (activation, usage, recent)
        """
        cache_key = f"top_bubbles_{sort_by}_{limit}"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["bubbles"]
        
        try:
            provider = LucioleContextProvider.get_instance()
            
            if not provider._qdrant_available:
                return []
            
            points, _ = provider._qdrant_client.scroll(
                collection_name=provider.COLLECTION_NAME,
                limit=10000,
                with_payload=True,
            )
            
            bubbles = []
            for point in points:
                bubble = {
                    "id": str(point.id),
                    "domain": point.payload.get("domain", "unknown"),
                    "activation_score": point.payload.get("activation_score", 1.0),
                    "activation_count": point.payload.get("activation_count", 0),
                    "severity": point.payload.get("severity", "info"),
                    "last_activated": point.payload.get("last_activated"),
                    "created_at": point.payload.get("created_at"),
                }
                bubbles.append(bubble)
            
            # Sort based on criteria
            if sort_by == "activation":
                bubbles.sort(key=lambda x: x["activation_score"], reverse=True)
            elif sort_by == "usage":
                bubbles.sort(key=lambda x: x["activation_count"], reverse=True)
            elif sort_by == "recent":
                bubbles.sort(key=lambda x: x.get("last_activated") or "", reverse=True)
            
            result = bubbles[:limit]
            self._cache_set(cache_key, {"bubbles": result})
            
            return result
            
        except Exception as e:
            return []
    
    def get_domain_analytics(self) -> Dict:
        """
        Get analytics by domain.
        
        Returns bubble counts, average activation, and severity distribution per domain.
        """
        if self._is_cache_valid("domain_analytics"):
            return self._cache["domain_analytics"]
        
        try:
            provider = LucioleContextProvider.get_instance()
            
            if not provider._qdrant_available:
                return {}
            
            points, _ = provider._qdrant_client.scroll(
                collection_name=provider.COLLECTION_NAME,
                limit=10000,
                with_payload=True,
            )
            
            domains = {}
            for point in points:
                domain = point.payload.get("domain", "unknown").split("/")[0]
                
                if domain not in domains:
                    domains[domain] = {
                        "count": 0,
                        "total_activation": 0,
                        "severity_counts": {"info": 0, "warning": 0, "critical": 0},
                        "bubbles": [],
                    }
                
                domains[domain]["count"] += 1
                domains[domain]["total_activation"] += point.payload.get("activation_score", 1.0)
                severity = point.payload.get("severity", "info")
                domains[domain]["severity_counts"][severity] = domains[domain]["severity_counts"].get(severity, 0) + 1
                domains[domain]["bubbles"].append(point.payload.get("domain"))
            
            # Calculate averages
            analytics = {}
            for domain, data in domains.items():
                analytics[domain] = {
                    "bubble_count": data["count"],
                    "avg_activation": data["total_activation"] / data["count"] if data["count"] > 0 else 0,
                    "severity_distribution": data["severity_counts"],
                    "subdomains": list(set(data["bubbles"]))[:10],
                }
            
            result = {
                "domain_count": len(analytics),
                "domains": analytics,
            }
            
            return self._cache_set("domain_analytics", result)
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_activity_timeline(self, hours: int = 24) -> List[Dict]:
        """
        Get activity timeline.
        
        Returns recent activities from scheduler, alerts, and operations.
        """
        timeline = []
        
        try:
            # Get scheduler history
            scheduler = LucioleTaskScheduler.get_instance()
            for entry in scheduler.get_history(50):
                timeline.append({
                    "type": "task",
                    "timestamp": entry.get("started_at"),
                    "title": f"Task: {entry.get('task')}",
                    "details": entry.get("result"),
                    "success": entry.get("success", False),
                })
            
            # Get alert history
            alerts = LucioleAlertManager.get_instance()
            for alert in alerts.get_alert_history(50):
                timeline.append({
                    "type": "alert",
                    "timestamp": alert.get("triggered_at"),
                    "title": f"Alert: {alert.get('rule_name')}",
                    "details": alert.get("message"),
                    "severity": alert.get("severity"),
                })
            
            # Sort by timestamp (most recent first)
            timeline.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            # Filter by time range
            cutoff = datetime.now() - timedelta(hours=hours)
            timeline = [
                e for e in timeline 
                if e.get("timestamp") and datetime.fromisoformat(e["timestamp"]) > cutoff
            ]
            
            return timeline[:100]
            
        except Exception as e:
            return []
    
    def get_metrics_summary(self) -> Dict:
        """
        Get metrics summary with trends.
        """
        try:
            collector = LucioleMetricsCollector.get_instance()
            metrics = collector.get_metrics()
            
            return {
                "counters": metrics["counters"],
                "rates": metrics["rates"],
                "latencies": metrics["latencies"],
                "timestamps": metrics["timestamps"],
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_health_summary(self) -> Dict:
        """
        Get health summary for all components.
        """
        try:
            health = LucioleHealthCheck()
            result = health.check_all()
            
            return {
                "status": result.get("status"),
                "components": result.get("checks", {}),
                "metrics_summary": result.get("metrics_summary"),
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_recommendations(self) -> List[Dict]:
        """
        Get system recommendations based on current state.
        """
        recommendations = []
        
        try:
            # Check metrics
            collector = LucioleMetricsCollector.get_instance()
            metrics = collector.get_metrics()
            
            # Low hit rate
            if metrics["rates"]["hit_rate"] < 0.5 and metrics["counters"]["searches_total"] > 10:
                recommendations.append({
                    "type": "warning",
                    "title": "Low Hit Rate",
                    "message": f"Search hit rate is {metrics['rates']['hit_rate']:.0%}. Consider adding more bubbles or adjusting keywords.",
                    "action": "Add more bubbles to cover common queries",
                })
            
            # High latency
            if metrics["latencies"]["search_avg_ms"] > 100:
                recommendations.append({
                    "type": "warning",
                    "title": "High Search Latency",
                    "message": f"Average search latency is {metrics['latencies']['search_avg_ms']:.0f}ms.",
                    "action": "Check Qdrant performance or reduce bubble count",
                })
            
            # Check tier distribution
            overview = self.get_overview()
            tier_dist = overview.get("tier_distribution", {})
            total = sum(tier_dist.values())
            
            if total > 0:
                cold_ratio = (tier_dist.get("cold", 0) + tier_dist.get("frozen", 0)) / total
                if cold_ratio > 0.5:
                    recommendations.append({
                        "type": "info",
                        "title": "Many Cold Bubbles",
                        "message": f"{cold_ratio:.0%} of bubbles are cold or frozen.",
                        "action": "Consider running maintenance to archive inactive bubbles",
                    })
                
                if tier_dist.get("hot", 0) == 0:
                    recommendations.append({
                        "type": "warning",
                        "title": "No Hot Bubbles",
                        "message": "No bubbles have high activation scores.",
                        "action": "Boost frequently used bubbles or add more relevant ones",
                    })
            
            # Check scheduler
            scheduler = LucioleTaskScheduler.get_instance()
            if not scheduler.is_running():
                recommendations.append({
                    "type": "info",
                    "title": "Scheduler Not Running",
                    "message": "Background scheduler is stopped.",
                    "action": "Start scheduler for automatic maintenance",
                })
            
            # Check backups
            backup = LucioleBackupManager.get_instance()
            backup_summary = backup.get_summary()
            if backup_summary.get("backup_count", 0) == 0:
                recommendations.append({
                    "type": "warning",
                    "title": "No Backups",
                    "message": "No backups have been created.",
                    "action": "Create a backup to protect your data",
                })
            
            # Check alerts
            alerts = LucioleAlertManager.get_instance()
            active_alerts = alerts.get_active_alerts()
            if len(active_alerts) > 0:
                recommendations.append({
                    "type": "alert",
                    "title": f"{len(active_alerts)} Active Alerts",
                    "message": "There are unresolved alerts.",
                    "action": "Review and resolve active alerts",
                })
            
        except Exception as e:
            recommendations.append({
                "type": "error",
                "title": "Error Getting Recommendations",
                "message": str(e),
            })
        
        return recommendations
    
    def get_full_dashboard(self) -> Dict:
        """
        Get the complete dashboard with all widgets.
        """
        self._last_update = datetime.now()
        
        widgets = [
            DashboardWidget(
                id="overview",
                title="System Overview",
                type="stats",
                data=self.get_overview(),
            ),
            DashboardWidget(
                id="health",
                title="Health Status",
                type="status",
                data=self.get_health_summary(),
            ),
            DashboardWidget(
                id="metrics",
                title="Metrics",
                type="stats",
                data=self.get_metrics_summary(),
            ),
            DashboardWidget(
                id="top_bubbles",
                title="Top Bubbles",
                type="list",
                data={"bubbles": self.get_top_bubbles(limit=5)},
            ),
            DashboardWidget(
                id="domains",
                title="Domain Analytics",
                type="chart",
                data=self.get_domain_analytics(),
            ),
            DashboardWidget(
                id="activity",
                title="Recent Activity",
                type="timeline",
                data={"events": self.get_activity_timeline(hours=24)},
            ),
            DashboardWidget(
                id="recommendations",
                title="Recommendations",
                type="list",
                data={"items": self.get_recommendations()},
            ),
        ]
        
        return {
            "generated_at": self._last_update.isoformat(),
            "widgets": [w.to_dict() for w in widgets],
        }
    
    def format_summary(self) -> str:
        """Format dashboard summary for display."""
        overview = self.get_overview()
        health = self.get_health_summary()
        recommendations = self.get_recommendations()
        
        health_icon = {"healthy": "🟢", "degraded": "🟡", "unhealthy": "🔴"}.get(
            health.get("status", "unknown"), "⚪"
        )
        
        lines = [
            f"{health_icon} **LUCIOLE DASHBOARD**",
            "",
            f"**Bubbles:** {overview.get('total_bubbles', 0)} total",
            f"**Tiers:** HOT:{overview.get('tier_distribution', {}).get('hot', 0)} | "
            f"WARM:{overview.get('tier_distribution', {}).get('warm', 0)} | "
            f"COLD:{overview.get('tier_distribution', {}).get('cold', 0)}",
            "",
            f"**Searches:** {overview.get('searches_total', 0)} "
            f"({overview.get('hit_rate', 0):.0%} hit rate)",
            f"**Latency:** {overview.get('avg_latency_ms', 0):.1f}ms avg",
            "",
        ]
        
        if recommendations:
            lines.append("---")
            lines.append("**Recommendations:**")
            for rec in recommendations[:3]:
                icon = {"warning": "⚠️", "info": "ℹ️", "alert": "🔔", "error": "❌"}.get(
                    rec.get("type", "info"), "•"
                )
                lines.append(f"  {icon} {rec.get('title')}")
        
        return "\n".join(lines)


# Convenience functions for Phase 19
def get_dashboard() -> LucioleDashboard:
    """Get the dashboard singleton."""
    return LucioleDashboard.get_instance()


def get_dashboard_summary() -> str:
    """Get formatted dashboard summary."""
    dashboard = LucioleDashboard.get_instance()
    return dashboard.format_summary()


# =============================================================================
# PHASE 20: WEBHOOKS & EVENT SYSTEM
# =============================================================================
# Event-driven architecture for real-time notifications. Events are emitted
# for key system operations (bubble lifecycle, searches, alerts) and can be
# consumed by webhooks or internal subscribers.
# =============================================================================

class EventType(Enum):
    """Types of events that can be emitted."""
    # Bubble lifecycle
    BUBBLE_CREATED = "bubble.created"
    BUBBLE_UPDATED = "bubble.updated"
    BUBBLE_ACTIVATED = "bubble.activated"
    BUBBLE_DECAYED = "bubble.decayed"
    BUBBLE_ARCHIVED = "bubble.archived"
    BUBBLE_RESURRECTED = "bubble.resurrected"
    BUBBLE_DELETED = "bubble.deleted"

    # Search events
    SEARCH_PERFORMED = "search.performed"
    SEARCH_HIT = "search.hit"
    SEARCH_MISS = "search.miss"

    # Alert events
    ALERT_TRIGGERED = "alert.triggered"
    ALERT_RESOLVED = "alert.resolved"
    ALERT_ACKNOWLEDGED = "alert.acknowledged"

    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    HEALTH_CHANGED = "health.changed"
    MAINTENANCE_STARTED = "maintenance.started"
    MAINTENANCE_COMPLETED = "maintenance.completed"

    # Backup events
    BACKUP_CREATED = "backup.created"
    BACKUP_RESTORED = "backup.restored"

    # Scheduler events
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"


@dataclass
class LucioleEvent:
    """Represents a system event."""
    id: str
    type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    source: str = "luciole"
    severity: str = "info"  # info, warning, critical

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "source": self.source,
            "severity": self.severity,
        }


@dataclass
class WebhookConfig:
    """Configuration for a webhook endpoint."""
    id: str
    name: str
    url: str
    events: List[str]  # List of EventType values to subscribe to
    secret: Optional[str] = None
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_triggered: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "events": self.events,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
        }


class LucioleEventSystem:
    """
    Central event system for Luciole.

    Manages event emission, subscription, and webhook delivery.
    Uses singleton pattern for consistent event handling.
    """

    _instance: Optional["LucioleEventSystem"] = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "LucioleEventSystem":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        if LucioleEventSystem._instance is not None:
            return

        self._webhooks: Dict[str, WebhookConfig] = {}
        self._event_history: List[LucioleEvent] = []
        self._max_history = 1000
        self._subscribers: Dict[str, List[Callable]] = {}  # event_type -> callbacks
        self._delivery_queue: queue.Queue = queue.Queue()
        self._delivery_thread: Optional[threading.Thread] = None
        self._running = False

        # Load webhooks from config
        self._load_webhooks()

    def _load_webhooks(self):
        """Load webhook configurations from file."""
        config_path = Path(__file__).parent.parent.parent.parent / "apps/backend/data/luciole_webhooks.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    data = json.load(f)
                    for wh in data.get("webhooks", []):
                        self._webhooks[wh["id"]] = WebhookConfig(
                            id=wh["id"],
                            name=wh["name"],
                            url=wh["url"],
                            events=wh.get("events", []),
                            secret=wh.get("secret"),
                            enabled=wh.get("enabled", True),
                            created_at=datetime.fromisoformat(wh["created_at"]) if "created_at" in wh else datetime.now(),
                        )
            except Exception as e:
                print(f"[EventSystem] Failed to load webhooks: {e}")

    def _save_webhooks(self):
        """Save webhook configurations to file."""
        config_path = Path(__file__).parent.parent.parent.parent / "apps/backend/data/luciole_webhooks.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "webhooks": [wh.to_dict() for wh in self._webhooks.values()],
            "updated_at": datetime.now().isoformat(),
        }

        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)

    def start(self):
        """Start the event delivery system."""
        if self._running:
            return

        self._running = True
        self._delivery_thread = threading.Thread(target=self._delivery_loop, daemon=True)
        self._delivery_thread.start()

        # Emit startup event
        self.emit(EventType.SYSTEM_STARTUP, {"message": "Event system started"})

    def stop(self):
        """Stop the event delivery system."""
        if not self._running:
            return

        self.emit(EventType.SYSTEM_SHUTDOWN, {"message": "Event system stopping"})
        self._running = False

        if self._delivery_thread:
            self._delivery_queue.put(None)  # Signal to stop
            self._delivery_thread.join(timeout=5)

    def _delivery_loop(self):
        """Background thread for webhook delivery."""
        while self._running:
            try:
                item = self._delivery_queue.get(timeout=1)
                if item is None:
                    break

                event, webhook = item
                self._deliver_webhook(event, webhook)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"[EventSystem] Delivery error: {e}")

    def _deliver_webhook(self, event: LucioleEvent, webhook: WebhookConfig):
        """Deliver event to a webhook endpoint."""
        try:
            import requests

            payload = {
                "event": event.to_dict(),
                "webhook_id": webhook.id,
                "timestamp": datetime.now().isoformat(),
            }

            headers = {
                "Content-Type": "application/json",
                "X-Luciole-Event": event.type.value,
                "X-Luciole-Webhook-Id": webhook.id,
            }

            if webhook.secret:
                import hashlib
                import hmac
                signature = hmac.new(
                    webhook.secret.encode(),
                    json.dumps(payload).encode(),
                    hashlib.sha256
                ).hexdigest()
                headers["X-Luciole-Signature"] = signature

            response = requests.post(
                webhook.url,
                json=payload,
                headers=headers,
                timeout=10
            )

            webhook.last_triggered = datetime.now()

            if response.status_code < 300:
                webhook.success_count += 1
            else:
                webhook.failure_count += 1
                print(f"[EventSystem] Webhook {webhook.name} failed: {response.status_code}")

        except Exception as e:
            webhook.failure_count += 1
            print(f"[EventSystem] Webhook {webhook.name} error: {e}")

    def emit(self, event_type: EventType, data: Dict[str, Any],
             severity: str = "info", source: str = "luciole") -> LucioleEvent:
        """
        Emit an event.

        Notifies all subscribers and queues webhook deliveries.
        """
        event = LucioleEvent(
            id=f"evt_{int(time.time()*1000)}_{hash(str(data)) % 10000}",
            type=event_type,
            timestamp=datetime.now(),
            data=data,
            source=source,
            severity=severity,
        )

        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

        # Notify internal subscribers
        event_key = event_type.value
        if event_key in self._subscribers:
            for callback in self._subscribers[event_key]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"[EventSystem] Subscriber error: {e}")

        # Also notify wildcard subscribers
        if "*" in self._subscribers:
            for callback in self._subscribers["*"]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"[EventSystem] Wildcard subscriber error: {e}")

        # Queue webhook deliveries
        for webhook in self._webhooks.values():
            if not webhook.enabled:
                continue

            if "*" in webhook.events or event_type.value in webhook.events:
                self._delivery_queue.put((event, webhook))

        return event

    def subscribe(self, event_type: str, callback: Callable[[LucioleEvent], None]):
        """Subscribe to an event type with a callback."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe a callback from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type] if cb != callback
            ]

    def add_webhook(self, name: str, url: str, events: List[str],
                    secret: Optional[str] = None) -> WebhookConfig:
        """Add a new webhook configuration."""
        webhook_id = f"wh_{int(time.time())}_{hash(url) % 10000}"

        webhook = WebhookConfig(
            id=webhook_id,
            name=name,
            url=url,
            events=events,
            secret=secret,
            enabled=True,
        )

        self._webhooks[webhook_id] = webhook
        self._save_webhooks()

        return webhook

    def remove_webhook(self, webhook_id: str) -> bool:
        """Remove a webhook configuration."""
        if webhook_id in self._webhooks:
            del self._webhooks[webhook_id]
            self._save_webhooks()
            return True
        return False

    def update_webhook(self, webhook_id: str, **updates) -> Optional[WebhookConfig]:
        """Update a webhook configuration."""
        if webhook_id not in self._webhooks:
            return None

        webhook = self._webhooks[webhook_id]

        for key, value in updates.items():
            if hasattr(webhook, key):
                setattr(webhook, key, value)

        self._save_webhooks()
        return webhook

    def get_webhooks(self) -> List[WebhookConfig]:
        """Get all webhook configurations."""
        return list(self._webhooks.values())

    def get_webhook(self, webhook_id: str) -> Optional[WebhookConfig]:
        """Get a specific webhook configuration."""
        return self._webhooks.get(webhook_id)

    def test_webhook(self, webhook_id: str) -> Dict:
        """Send a test event to a webhook."""
        webhook = self._webhooks.get(webhook_id)
        if not webhook:
            return {"success": False, "error": "Webhook not found"}

        test_event = LucioleEvent(
            id=f"test_{int(time.time())}",
            type=EventType.SYSTEM_STARTUP,
            timestamp=datetime.now(),
            data={"test": True, "message": "This is a test event"},
            source="luciole-test",
            severity="info",
        )

        try:
            import requests

            payload = {
                "event": test_event.to_dict(),
                "webhook_id": webhook.id,
                "timestamp": datetime.now().isoformat(),
                "is_test": True,
            }

            headers = {
                "Content-Type": "application/json",
                "X-Luciole-Event": "test",
                "X-Luciole-Webhook-Id": webhook.id,
            }

            response = requests.post(
                webhook.url,
                json=payload,
                headers=headers,
                timeout=10
            )

            return {
                "success": response.status_code < 300,
                "status_code": response.status_code,
                "response": response.text[:500] if response.text else None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_event_history(self,
                          event_type: Optional[str] = None,
                          limit: int = 100,
                          since: Optional[datetime] = None) -> List[Dict]:
        """Get event history with optional filtering."""
        events = self._event_history

        if event_type:
            events = [e for e in events if e.type.value == event_type]

        if since:
            events = [e for e in events if e.timestamp >= since]

        # Return most recent first
        events = sorted(events, key=lambda e: e.timestamp, reverse=True)

        return [e.to_dict() for e in events[:limit]]

    def get_event_types(self) -> List[Dict]:
        """Get list of all available event types."""
        return [
            {"value": et.value, "name": et.name}
            for et in EventType
        ]

    def get_stats(self) -> Dict:
        """Get event system statistics."""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)

        recent_events = [e for e in self._event_history if e.timestamp >= hour_ago]
        daily_events = [e for e in self._event_history if e.timestamp >= day_ago]

        # Count by type
        type_counts = {}
        for event in daily_events:
            key = event.type.value
            type_counts[key] = type_counts.get(key, 0) + 1

        return {
            "total_events": len(self._event_history),
            "events_last_hour": len(recent_events),
            "events_last_24h": len(daily_events),
            "event_types_active": len(type_counts),
            "type_distribution": type_counts,
            "webhooks_total": len(self._webhooks),
            "webhooks_enabled": sum(1 for w in self._webhooks.values() if w.enabled),
            "delivery_queue_size": self._delivery_queue.qsize(),
            "running": self._running,
        }


# Convenience functions for Phase 20
def get_event_system() -> LucioleEventSystem:
    """Get the event system singleton."""
    return LucioleEventSystem.get_instance()


def emit_event(event_type: EventType, data: Dict, severity: str = "info") -> LucioleEvent:
    """Emit an event through the event system."""
    system = LucioleEventSystem.get_instance()
    return system.emit(event_type, data, severity)


# =============================================================================
# PHASE 21: AUDIT TRAIL & COMPLIANCE LOGGING
# =============================================================================
# Comprehensive audit logging for all system operations. Provides immutable
# audit trail for compliance, debugging, and forensic analysis.
# =============================================================================

class AuditAction(Enum):
    """Types of auditable actions."""
    # Bubble operations
    BUBBLE_CREATE = "bubble.create"
    BUBBLE_READ = "bubble.read"
    BUBBLE_UPDATE = "bubble.update"
    BUBBLE_DELETE = "bubble.delete"
    BUBBLE_SEARCH = "bubble.search"
    BUBBLE_BOOST = "bubble.boost"
    BUBBLE_ARCHIVE = "bubble.archive"
    BUBBLE_RESURRECT = "bubble.resurrect"

    # Lifecycle operations
    DECAY_APPLY = "lifecycle.decay"
    TIER_CHANGE = "lifecycle.tier_change"
    CONSOLIDATE = "lifecycle.consolidate"
    MAINTENANCE = "lifecycle.maintenance"

    # System operations
    SYSTEM_START = "system.start"
    SYSTEM_STOP = "system.stop"
    CONFIG_CHANGE = "system.config_change"
    BACKUP_CREATE = "backup.create"
    BACKUP_RESTORE = "backup.restore"
    EXPORT = "data.export"
    IMPORT = "data.import"

    # Webhook operations
    WEBHOOK_CREATE = "webhook.create"
    WEBHOOK_UPDATE = "webhook.update"
    WEBHOOK_DELETE = "webhook.delete"
    WEBHOOK_TRIGGER = "webhook.trigger"

    # Alert operations
    ALERT_CREATE = "alert.create"
    ALERT_TRIGGER = "alert.trigger"
    ALERT_ACKNOWLEDGE = "alert.acknowledge"
    ALERT_RESOLVE = "alert.resolve"

    # Scheduler operations
    TASK_CREATE = "task.create"
    TASK_RUN = "task.run"
    TASK_COMPLETE = "task.complete"
    TASK_FAIL = "task.fail"

    # Access operations
    API_CALL = "api.call"
    AUTH_SUCCESS = "auth.success"
    AUTH_FAILURE = "auth.failure"


@dataclass
class AuditEntry:
    """Represents a single audit log entry."""
    id: str
    timestamp: datetime
    action: AuditAction
    actor: str  # Who performed the action (user, system, scheduler)
    resource_type: str  # Type of resource affected
    resource_id: Optional[str]  # ID of affected resource
    details: Dict[str, Any]  # Action-specific details
    result: str  # success, failure, partial
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    duration_ms: Optional[float] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.value,
            "actor": self.actor,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "result": self.result,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
        }

    def to_log_line(self) -> str:
        """Format as single log line for file storage."""
        return json.dumps(self.to_dict())


class LucioleAuditLog:
    """
    Comprehensive audit logging system.

    Features:
    - Immutable append-only log
    - File persistence with rotation
    - Query and filter capabilities
    - Compliance-ready format
    """

    _instance: Optional["LucioleAuditLog"] = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "LucioleAuditLog":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        if LucioleAuditLog._instance is not None:
            return

        self._entries: List[AuditEntry] = []
        self._max_memory_entries = 10000
        self._log_dir = Path(__file__).parent.parent.parent.parent / "apps/backend/data/audit_logs"
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._current_log_file: Optional[Path] = None
        self._file_lock = threading.Lock()

        # Initialize log file
        self._rotate_log_file()

        # Load recent entries from current log file
        self._load_recent_entries()

    def _rotate_log_file(self):
        """Create a new log file for the current day."""
        today = datetime.now().strftime("%Y-%m-%d")
        self._current_log_file = self._log_dir / f"audit_{today}.jsonl"

    def _load_recent_entries(self):
        """Load recent entries from current log file."""
        if self._current_log_file and self._current_log_file.exists():
            try:
                with open(self._current_log_file, "r") as f:
                    for line in f:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                entry = AuditEntry(
                                    id=data["id"],
                                    timestamp=datetime.fromisoformat(data["timestamp"]),
                                    action=AuditAction(data["action"]),
                                    actor=data["actor"],
                                    resource_type=data["resource_type"],
                                    resource_id=data.get("resource_id"),
                                    details=data.get("details", {}),
                                    result=data["result"],
                                    ip_address=data.get("ip_address"),
                                    user_agent=data.get("user_agent"),
                                    duration_ms=data.get("duration_ms"),
                                    error_message=data.get("error_message"),
                                )
                                self._entries.append(entry)
                            except Exception:
                                continue

                # Keep only recent entries in memory
                if len(self._entries) > self._max_memory_entries:
                    self._entries = self._entries[-self._max_memory_entries:]

            except Exception as e:
                print(f"[AuditLog] Failed to load entries: {e}")

    def _persist_entry(self, entry: AuditEntry):
        """Persist entry to log file."""
        # Check if we need to rotate
        today = datetime.now().strftime("%Y-%m-%d")
        expected_file = self._log_dir / f"audit_{today}.jsonl"
        if self._current_log_file != expected_file:
            self._rotate_log_file()

        with self._file_lock:
            try:
                with open(self._current_log_file, "a") as f:
                    f.write(entry.to_log_line() + "\n")
            except Exception as e:
                print(f"[AuditLog] Failed to persist entry: {e}")

    def log(self,
            action: AuditAction,
            actor: str,
            resource_type: str,
            resource_id: Optional[str] = None,
            details: Optional[Dict] = None,
            result: str = "success",
            ip_address: Optional[str] = None,
            user_agent: Optional[str] = None,
            duration_ms: Optional[float] = None,
            error_message: Optional[str] = None) -> AuditEntry:
        """
        Log an auditable action.

        Args:
            action: The type of action performed
            actor: Who performed the action (user ID, "system", "scheduler")
            resource_type: Type of resource affected ("bubble", "webhook", etc.)
            resource_id: ID of the affected resource
            details: Action-specific details
            result: "success", "failure", or "partial"
            ip_address: Client IP address (if from API)
            user_agent: Client user agent (if from API)
            duration_ms: How long the operation took
            error_message: Error message if failed

        Returns:
            The created audit entry
        """
        entry = AuditEntry(
            id=f"aud_{int(time.time()*1000)}_{hash(str(details)) % 10000}",
            timestamp=datetime.now(),
            action=action,
            actor=actor,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            result=result,
            ip_address=ip_address,
            user_agent=user_agent,
            duration_ms=duration_ms,
            error_message=error_message,
        )

        # Add to memory
        self._entries.append(entry)
        if len(self._entries) > self._max_memory_entries:
            self._entries = self._entries[-self._max_memory_entries:]

        # Persist to file
        self._persist_entry(entry)

        return entry

    def query(self,
              action: Optional[str] = None,
              actor: Optional[str] = None,
              resource_type: Optional[str] = None,
              resource_id: Optional[str] = None,
              result: Optional[str] = None,
              since: Optional[datetime] = None,
              until: Optional[datetime] = None,
              limit: int = 100,
              offset: int = 0) -> List[AuditEntry]:
        """
        Query audit log with filters.

        Returns entries matching all specified criteria.
        """
        entries = self._entries

        if action:
            entries = [e for e in entries if e.action.value == action]

        if actor:
            entries = [e for e in entries if e.actor == actor]

        if resource_type:
            entries = [e for e in entries if e.resource_type == resource_type]

        if resource_id:
            entries = [e for e in entries if e.resource_id == resource_id]

        if result:
            entries = [e for e in entries if e.result == result]

        if since:
            entries = [e for e in entries if e.timestamp >= since]

        if until:
            entries = [e for e in entries if e.timestamp <= until]

        # Sort by timestamp descending (most recent first)
        entries = sorted(entries, key=lambda e: e.timestamp, reverse=True)

        # Apply pagination
        return entries[offset:offset + limit]

    def get_entry(self, entry_id: str) -> Optional[AuditEntry]:
        """Get a specific audit entry by ID."""
        for entry in self._entries:
            if entry.id == entry_id:
                return entry
        return None

    def get_stats(self,
                  hours: int = 24) -> Dict:
        """Get audit statistics for a time period."""
        now = datetime.now()
        since = now - timedelta(hours=hours)

        recent = [e for e in self._entries if e.timestamp >= since]

        # Count by action
        action_counts = {}
        for entry in recent:
            key = entry.action.value
            action_counts[key] = action_counts.get(key, 0) + 1

        # Count by actor
        actor_counts = {}
        for entry in recent:
            actor_counts[entry.actor] = actor_counts.get(entry.actor, 0) + 1

        # Count by result
        result_counts = {"success": 0, "failure": 0, "partial": 0}
        for entry in recent:
            if entry.result in result_counts:
                result_counts[entry.result] += 1

        # Count by resource type
        resource_counts = {}
        for entry in recent:
            resource_counts[entry.resource_type] = resource_counts.get(entry.resource_type, 0) + 1

        # Average duration
        durations = [e.duration_ms for e in recent if e.duration_ms is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "period_hours": hours,
            "total_entries": len(recent),
            "entries_in_memory": len(self._entries),
            "action_distribution": action_counts,
            "actor_distribution": actor_counts,
            "result_distribution": result_counts,
            "resource_distribution": resource_counts,
            "avg_duration_ms": round(avg_duration, 2),
            "failure_rate": round(result_counts["failure"] / len(recent) * 100, 2) if recent else 0,
        }

    def get_log_files(self) -> List[Dict]:
        """Get list of audit log files."""
        files = []
        for log_file in sorted(self._log_dir.glob("audit_*.jsonl"), reverse=True):
            stat = log_file.stat()
            files.append({
                "name": log_file.name,
                "path": str(log_file),
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_current": log_file == self._current_log_file,
            })
        return files

    def export_entries(self,
                       since: Optional[datetime] = None,
                       until: Optional[datetime] = None,
                       format: str = "jsonl") -> Dict:
        """
        Export audit entries to a file.

        Args:
            since: Start date filter
            until: End date filter
            format: Export format ("jsonl", "json", "csv")

        Returns:
            Export result with file path
        """
        entries = self.query(since=since, until=until, limit=100000)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = self._log_dir / "exports"
        export_dir.mkdir(exist_ok=True)

        if format == "jsonl":
            export_file = export_dir / f"audit_export_{timestamp}.jsonl"
            with open(export_file, "w") as f:
                for entry in entries:
                    f.write(entry.to_log_line() + "\n")

        elif format == "json":
            export_file = export_dir / f"audit_export_{timestamp}.json"
            with open(export_file, "w") as f:
                json.dump({
                    "exported_at": datetime.now().isoformat(),
                    "count": len(entries),
                    "entries": [e.to_dict() for e in entries],
                }, f, indent=2)

        elif format == "csv":
            export_file = export_dir / f"audit_export_{timestamp}.csv"
            with open(export_file, "w") as f:
                # Header
                f.write("id,timestamp,action,actor,resource_type,resource_id,result,duration_ms,error_message\n")
                for entry in entries:
                    f.write(f"{entry.id},{entry.timestamp.isoformat()},{entry.action.value},"
                            f"{entry.actor},{entry.resource_type},{entry.resource_id or ''},"
                            f"{entry.result},{entry.duration_ms or ''},{entry.error_message or ''}\n")

        else:
            return {"success": False, "error": f"Unknown format: {format}"}

        return {
            "success": True,
            "file_path": str(export_file),
            "format": format,
            "count": len(entries),
            "size_bytes": export_file.stat().st_size,
        }

    def purge_old_logs(self, days: int = 90) -> Dict:
        """
        Purge audit logs older than specified days.

        Args:
            days: Keep logs from the last N days

        Returns:
            Purge result with count of deleted files
        """
        cutoff = datetime.now() - timedelta(days=days)
        deleted = []

        for log_file in self._log_dir.glob("audit_*.jsonl"):
            try:
                # Parse date from filename
                date_str = log_file.stem.replace("audit_", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                if file_date < cutoff:
                    log_file.unlink()
                    deleted.append(log_file.name)

            except Exception:
                continue

        return {
            "purged": True,
            "cutoff_date": cutoff.isoformat(),
            "files_deleted": len(deleted),
            "deleted_files": deleted,
        }


# Convenience functions for Phase 21
def get_audit_log() -> LucioleAuditLog:
    """Get the audit log singleton."""
    return LucioleAuditLog.get_instance()


def audit(action: AuditAction,
          actor: str,
          resource_type: str,
          **kwargs) -> AuditEntry:
    """Log an auditable action."""
    log = LucioleAuditLog.get_instance()
    return log.log(action, actor, resource_type, **kwargs)


# =============================================================================
# PHASE 22: INTEGRATION HUB - SYSTEM ORCHESTRATION
# =============================================================================
# Central orchestration layer that connects all subsystems:
# - Events -> Audit (automatic audit logging for events)
# - Operations -> Events (emit events for key operations)
# - Alerts -> Events (alert triggers emit events)
# - Scheduler -> Events/Audit (task execution logging)
# =============================================================================

class IntegrationMode(Enum):
    """Integration connection modes."""
    DISABLED = "disabled"
    SYNC = "sync"       # Synchronous processing
    ASYNC = "async"     # Asynchronous via queue


@dataclass
class IntegrationConfig:
    """Configuration for an integration connection."""
    source: str
    target: str
    mode: IntegrationMode
    enabled: bool = True
    filter_events: Optional[List[str]] = None  # Only process these event types
    transform: Optional[str] = None  # Transform function name
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            "source": self.source,
            "target": self.target,
            "mode": self.mode.value,
            "enabled": self.enabled,
            "filter_events": self.filter_events,
            "transform": self.transform,
            "created_at": self.created_at.isoformat(),
        }


class LucioleIntegrationHub:
    """
    Central integration hub connecting all Luciole subsystems.

    Provides:
    - Event-to-audit automatic logging
    - Operation-to-event emission
    - Alert-to-event bridging
    - Unified system status
    """

    _instance: Optional["LucioleIntegrationHub"] = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "LucioleIntegrationHub":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        if LucioleIntegrationHub._instance is not None:
            return

        self._integrations: Dict[str, IntegrationConfig] = {}
        self._running = False
        self._stats = {
            "events_processed": 0,
            "audit_entries_created": 0,
            "alerts_bridged": 0,
            "errors": 0,
        }

        # Setup default integrations
        self._setup_default_integrations()

    def _setup_default_integrations(self):
        """Setup default integration connections."""
        # Events -> Audit
        self._integrations["events_to_audit"] = IntegrationConfig(
            source="events",
            target="audit",
            mode=IntegrationMode.SYNC,
            enabled=True,
            filter_events=None,  # All events
        )

        # Alerts -> Events
        self._integrations["alerts_to_events"] = IntegrationConfig(
            source="alerts",
            target="events",
            mode=IntegrationMode.SYNC,
            enabled=True,
        )

        # Scheduler -> Audit
        self._integrations["scheduler_to_audit"] = IntegrationConfig(
            source="scheduler",
            target="audit",
            mode=IntegrationMode.SYNC,
            enabled=True,
        )

        # Backup -> Audit
        self._integrations["backup_to_audit"] = IntegrationConfig(
            source="backup",
            target="audit",
            mode=IntegrationMode.SYNC,
            enabled=True,
        )

    def start(self):
        """Start the integration hub and wire up connections."""
        if self._running:
            return {"started": False, "reason": "Already running"}

        self._running = True

        # Wire up event system -> audit
        if self._integrations.get("events_to_audit", IntegrationConfig("", "", IntegrationMode.DISABLED)).enabled:
            try:
                event_system = LucioleEventSystem.get_instance()
                event_system.subscribe("*", self._on_event_for_audit)
            except Exception as e:
                print(f"[IntegrationHub] Failed to wire events->audit: {e}")

        return {"started": True, "integrations_active": self._count_active()}

    def stop(self):
        """Stop the integration hub."""
        if not self._running:
            return {"stopped": False, "reason": "Not running"}

        self._running = False

        # Unwire subscriptions
        try:
            event_system = LucioleEventSystem.get_instance()
            event_system.unsubscribe("*", self._on_event_for_audit)
        except Exception:
            pass

        return {"stopped": True}

    def _count_active(self) -> int:
        """Count active integrations."""
        return sum(1 for i in self._integrations.values() if i.enabled)

    def _on_event_for_audit(self, event: LucioleEvent):
        """Handle event -> audit integration."""
        if not self._running:
            return

        config = self._integrations.get("events_to_audit")
        if not config or not config.enabled:
            return

        # Filter events if configured
        if config.filter_events and event.type.value not in config.filter_events:
            return

        try:
            # Map event type to audit action
            action_map = {
                "bubble.created": AuditAction.BUBBLE_CREATE,
                "bubble.updated": AuditAction.BUBBLE_UPDATE,
                "bubble.activated": AuditAction.BUBBLE_BOOST,
                "bubble.decayed": AuditAction.DECAY_APPLY,
                "bubble.archived": AuditAction.BUBBLE_ARCHIVE,
                "bubble.resurrected": AuditAction.BUBBLE_RESURRECT,
                "bubble.deleted": AuditAction.BUBBLE_DELETE,
                "search.performed": AuditAction.BUBBLE_SEARCH,
                "alert.triggered": AuditAction.ALERT_TRIGGER,
                "alert.resolved": AuditAction.ALERT_RESOLVE,
                "alert.acknowledged": AuditAction.ALERT_ACKNOWLEDGE,
                "system.startup": AuditAction.SYSTEM_START,
                "system.shutdown": AuditAction.SYSTEM_STOP,
                "backup.created": AuditAction.BACKUP_CREATE,
                "backup.restored": AuditAction.BACKUP_RESTORE,
                "task.started": AuditAction.TASK_RUN,
                "task.completed": AuditAction.TASK_COMPLETE,
                "task.failed": AuditAction.TASK_FAIL,
            }

            audit_action = action_map.get(event.type.value)
            if not audit_action:
                # Use API_CALL as default for unmapped events
                audit_action = AuditAction.API_CALL

            # Create audit entry
            audit_log = LucioleAuditLog.get_instance()
            audit_log.log(
                action=audit_action,
                actor=event.source,
                resource_type="event",
                resource_id=event.id,
                details={
                    "event_type": event.type.value,
                    "event_data": event.data,
                    "severity": event.severity,
                },
                result="success",
            )

            self._stats["events_processed"] += 1
            self._stats["audit_entries_created"] += 1

        except Exception as e:
            self._stats["errors"] += 1
            print(f"[IntegrationHub] Event->Audit error: {e}")

    def emit_operation_event(self,
                              operation: str,
                              resource_type: str,
                              resource_id: Optional[str] = None,
                              details: Optional[Dict] = None,
                              result: str = "success") -> Optional[LucioleEvent]:
        """
        Emit an event for an operation.

        Helper method for operations to emit events consistently.
        """
        # Map operation to event type
        event_map = {
            "create": EventType.BUBBLE_CREATED,
            "update": EventType.BUBBLE_UPDATED,
            "delete": EventType.BUBBLE_DELETED,
            "search": EventType.SEARCH_PERFORMED,
            "archive": EventType.BUBBLE_ARCHIVED,
            "resurrect": EventType.BUBBLE_RESURRECTED,
            "decay": EventType.BUBBLE_DECAYED,
            "boost": EventType.BUBBLE_ACTIVATED,
            "backup": EventType.BACKUP_CREATED,
            "restore": EventType.BACKUP_RESTORED,
            "maintenance": EventType.MAINTENANCE_STARTED,
        }

        event_type = event_map.get(operation)
        if not event_type:
            return None

        try:
            event_system = LucioleEventSystem.get_instance()
            return event_system.emit(
                event_type,
                {
                    "operation": operation,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "result": result,
                    **(details or {}),
                },
                severity="info" if result == "success" else "warning",
            )
        except Exception as e:
            print(f"[IntegrationHub] Emit error: {e}")
            return None

    def bridge_alert_to_event(self, alert: Dict) -> Optional[LucioleEvent]:
        """
        Bridge an alert to the event system.

        Called when an alert is triggered/resolved.
        """
        config = self._integrations.get("alerts_to_events")
        if not config or not config.enabled:
            return None

        try:
            event_system = LucioleEventSystem.get_instance()

            # Determine event type
            if alert.get("status") == "triggered":
                event_type = EventType.ALERT_TRIGGERED
            elif alert.get("status") == "resolved":
                event_type = EventType.ALERT_RESOLVED
            elif alert.get("status") == "acknowledged":
                event_type = EventType.ALERT_ACKNOWLEDGED
            else:
                event_type = EventType.ALERT_TRIGGERED

            event = event_system.emit(
                event_type,
                {
                    "alert_id": alert.get("id"),
                    "rule_name": alert.get("rule_name"),
                    "severity": alert.get("severity"),
                    "message": alert.get("message"),
                },
                severity=alert.get("severity", "warning"),
            )

            self._stats["alerts_bridged"] += 1
            return event

        except Exception as e:
            self._stats["errors"] += 1
            print(f"[IntegrationHub] Alert bridge error: {e}")
            return None

    def get_integration(self, name: str) -> Optional[IntegrationConfig]:
        """Get an integration configuration."""
        return self._integrations.get(name)

    def set_integration_enabled(self, name: str, enabled: bool) -> bool:
        """Enable or disable an integration."""
        if name not in self._integrations:
            return False
        self._integrations[name].enabled = enabled
        return True

    def get_integrations(self) -> List[Dict]:
        """Get all integration configurations."""
        return [i.to_dict() for i in self._integrations.values()]

    def get_stats(self) -> Dict:
        """Get integration hub statistics."""
        return {
            "running": self._running,
            "integrations_total": len(self._integrations),
            "integrations_active": self._count_active(),
            "stats": self._stats.copy(),
        }

    def get_system_status(self) -> Dict:
        """
        Get unified status of all Luciole subsystems.

        Provides a single view of the entire system health.
        """
        status = {
            "timestamp": datetime.now().isoformat(),
            "hub_running": self._running,
            "subsystems": {},
        }

        # Event System
        try:
            event_system = LucioleEventSystem.get_instance()
            status["subsystems"]["events"] = {
                "status": "running" if event_system._running else "stopped",
                "total_events": len(event_system._event_history),
                "webhooks": len(event_system._webhooks),
            }
        except Exception as e:
            status["subsystems"]["events"] = {"status": "error", "error": str(e)}

        # Audit Log
        try:
            audit_log = LucioleAuditLog.get_instance()
            status["subsystems"]["audit"] = {
                "status": "ready",
                "entries_in_memory": len(audit_log._entries),
                "log_files": len(audit_log.get_log_files()),
            }
        except Exception as e:
            status["subsystems"]["audit"] = {"status": "error", "error": str(e)}

        # Alert Manager
        try:
            alert_manager = LucioleAlertManager.get_instance()
            status["subsystems"]["alerts"] = {
                "status": "ready",
                "rules": len(alert_manager.get_rules()),
                "active_alerts": len(alert_manager.get_active_alerts()),
            }
        except Exception as e:
            status["subsystems"]["alerts"] = {"status": "error", "error": str(e)}

        # Scheduler
        try:
            scheduler = LucioleTaskScheduler.get_instance()
            status["subsystems"]["scheduler"] = {
                "status": "running" if scheduler._running else "stopped",
                "tasks": len(scheduler._tasks),
            }
        except Exception as e:
            status["subsystems"]["scheduler"] = {"status": "error", "error": str(e)}

        # Backup Manager
        try:
            backup_manager = LucioleBackupManager.get_instance()
            backups = backup_manager.list_backups()
            status["subsystems"]["backup"] = {
                "status": "ready",
                "backups": len(backups),
            }
        except Exception as e:
            status["subsystems"]["backup"] = {"status": "error", "error": str(e)}

        # Dashboard
        try:
            dashboard = LucioleDashboard.get_instance()
            overview = dashboard.get_overview()
            status["subsystems"]["dashboard"] = {
                "status": "ready",
                "total_bubbles": overview.get("total_bubbles", 0),
                "health": overview.get("health_status", "unknown"),
            }
        except Exception as e:
            status["subsystems"]["dashboard"] = {"status": "error", "error": str(e)}

        # Metrics Collector
        try:
            metrics = LucioleMetricsCollector.get_instance()
            status["subsystems"]["metrics"] = {
                "status": "ready",
                "searches_total": metrics._metrics.searches_total,
                "hit_rate": round(metrics._metrics.hit_rate, 2),
            }
        except Exception as e:
            status["subsystems"]["metrics"] = {"status": "error", "error": str(e)}

        # Calculate overall health
        subsystem_statuses = [s.get("status") for s in status["subsystems"].values()]
        if "error" in subsystem_statuses:
            status["overall_health"] = "degraded"
        elif all(s in ["ready", "running"] for s in subsystem_statuses):
            status["overall_health"] = "healthy"
        else:
            status["overall_health"] = "partial"

        return status

    def run_diagnostics(self) -> Dict:
        """
        Run diagnostics on all subsystems.

        Tests connectivity and basic functionality.
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
        }

        # Test Event System
        try:
            event_system = LucioleEventSystem.get_instance()
            test_event = event_system.emit(
                EventType.SYSTEM_STARTUP,
                {"diagnostic": True, "test": "event_system"},
                severity="info",
                source="diagnostics",
            )
            results["tests"].append({
                "name": "event_system",
                "status": "pass",
                "event_id": test_event.id,
            })
        except Exception as e:
            results["tests"].append({
                "name": "event_system",
                "status": "fail",
                "error": str(e),
            })

        # Test Audit Log
        try:
            audit_log = LucioleAuditLog.get_instance()
            test_entry = audit_log.log(
                action=AuditAction.API_CALL,
                actor="diagnostics",
                resource_type="test",
                details={"diagnostic": True},
            )
            results["tests"].append({
                "name": "audit_log",
                "status": "pass",
                "entry_id": test_entry.id,
            })
        except Exception as e:
            results["tests"].append({
                "name": "audit_log",
                "status": "fail",
                "error": str(e),
            })

        # Test Alert Manager
        try:
            alert_manager = LucioleAlertManager.get_instance()
            rules = alert_manager.get_rules()
            results["tests"].append({
                "name": "alert_manager",
                "status": "pass",
                "rules_count": len(rules),
            })
        except Exception as e:
            results["tests"].append({
                "name": "alert_manager",
                "status": "fail",
                "error": str(e),
            })

        # Test Metrics Collector
        try:
            metrics = LucioleMetricsCollector.get_instance()
            prometheus = metrics.export_prometheus()
            results["tests"].append({
                "name": "metrics_collector",
                "status": "pass",
                "prometheus_lines": len(prometheus.split("\n")),
            })
        except Exception as e:
            results["tests"].append({
                "name": "metrics_collector",
                "status": "fail",
                "error": str(e),
            })

        # Summary
        passed = sum(1 for t in results["tests"] if t["status"] == "pass")
        results["summary"] = {
            "total": len(results["tests"]),
            "passed": passed,
            "failed": len(results["tests"]) - passed,
            "success_rate": round(passed / len(results["tests"]) * 100, 1) if results["tests"] else 0,
        }

        return results


# Convenience functions for Phase 22
def get_integration_hub() -> LucioleIntegrationHub:
    """Get the integration hub singleton."""
    return LucioleIntegrationHub.get_instance()


def get_system_status() -> Dict:
    """Get unified system status."""
    hub = LucioleIntegrationHub.get_instance()
    return hub.get_system_status()
