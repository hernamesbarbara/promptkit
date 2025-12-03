#!/usr/bin/env python3
"""
File categorization utility.

Categorizes project files into: Config, Tests, Docs, Scripts, Source Code, Data, AI Tooling, Other.

Implements a 4-phase categorization algorithm:
  Phase 1: Directory and filename pattern matching (High confidence)
  Phase 2: YAML frontmatter analysis (Medium confidence)
  Phase 3: Content structure analysis (Medium confidence)
  Phase 4: Keyword detection (Low confidence)

Directory Exclusion Layers:
  Layer 1: ALWAYS_EXCLUDE - Never scanned (node_modules, .git, __pycache__, venv)
  Layer 2: .gitignore - Respects project-specific exclusions (requires pathspec)
  Layer 3: EXTENDED_EXCLUDE - Fallback defaults when no .gitignore (dist, build, vendor)
  Layer 4: Escape hatches (--include-ignored, --include-all)
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

Category = Literal["Config", "Tests", "Docs", "Scripts", "Source Code", "Data", "AI Tooling", "Other"]
Confidence = Literal["High", "Medium", "Low"]

# =============================================================================
# DIRECTORY EXCLUSION LAYERS
# =============================================================================

# Layer 1: ALWAYS excluded - never useful to categorize
ALWAYS_EXCLUDE_DIRS = {
    # JS package managers
    "node_modules", "bower_components", "jspm_packages",
    # Version control
    ".git", ".svn", ".hg",
    # Python caches
    "__pycache__", ".pytest_cache", ".tox", ".mypy_cache", ".ruff_cache",
    # Python virtualenvs
    "venv", ".venv",
    # Misc caches
    ".cache", ".npm", ".yarn",
}

# Layer 3: Extended defaults when .gitignore unavailable
EXTENDED_EXCLUDE_DIRS = {
    # Build outputs
    "dist", "build", "out", "_build", "target",
    # Vendored dependencies
    "vendor",
    # Test coverage
    "coverage", ".nyc_output", "htmlcov",
    # IDE directories (already handled but explicit)
    ".idea",
    # Alternative virtualenv names
    "env",
    # Eggs and wheels
    "*.egg-info", ".eggs",
}

# Directories to ALLOW even if they start with "."
ALLOWED_DOT_DIRS = {".claude", ".cursor", ".aider", ".github", ".vscode"}


@dataclass
class ExclusionStats:
    """Track which exclusion layer caught directories."""
    layer1_always: int = 0
    layer2_gitignore: int = 0
    layer3_defaults: int = 0
    hidden_dirs: int = 0
    excluded_dirs: set[str] = field(default_factory=set)

    def total(self) -> int:
        return self.layer1_always + self.layer2_gitignore + self.layer3_defaults + self.hidden_dirs

    def summary(self) -> str:
        parts = []
        if self.layer1_always:
            parts.append(f"{self.layer1_always} via Layer 1 (always-exclude)")
        if self.layer2_gitignore:
            parts.append(f"{self.layer2_gitignore} via .gitignore")
        if self.layer3_defaults:
            parts.append(f"{self.layer3_defaults} via Layer 3 (defaults)")
        if self.hidden_dirs:
            parts.append(f"{self.hidden_dirs} hidden directories")
        if not parts:
            return "No directories excluded"
        return f"Excluded {self.total()} directories: " + ", ".join(parts)


def load_gitignore_spec(root: Path) -> tuple[object | None, bool]:
    """
    Try to load .gitignore as a pathspec.

    Returns:
        (spec, success) - spec is PathSpec if successful, None otherwise
    """
    gitignore_path = root / ".gitignore"
    if not gitignore_path.exists():
        return None, False

    try:
        import pathspec
    except ImportError:
        print(
            "Warning: Could not parse .gitignore (pathspec library not installed). "
            "Using default exclusions.",
            file=sys.stderr,
        )
        return None, False

    try:
        with open(gitignore_path) as f:
            spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
        return spec, True
    except Exception as e:
        print(f"Warning: Could not parse .gitignore ({e}). Using default exclusions.", file=sys.stderr)
        return None, False


def should_exclude_dir(
    dir_path: Path,
    rel_path: Path,
    gitignore_spec: object | None,
    use_gitignore: bool,
    include_ignored: bool,
    include_all: bool,
    stats: ExclusionStats,
) -> bool:
    """
    Check if a directory should be excluded using layered logic.

    Args:
        dir_path: Absolute path to directory
        rel_path: Path relative to scan root
        gitignore_spec: Parsed .gitignore (pathspec.PathSpec or None)
        use_gitignore: Whether .gitignore was successfully loaded
        include_ignored: Bypass layers 2-3
        include_all: Bypass ALL layers (use with caution)
        stats: ExclusionStats to update

    Returns:
        True if directory should be excluded
    """
    dir_name = dir_path.name

    # Layer 1: ALWAYS exclude (unless --include-all)
    if not include_all and dir_name in ALWAYS_EXCLUDE_DIRS:
        stats.layer1_always += 1
        stats.excluded_dirs.add(str(rel_path))
        return True

    # Early exit if bypassing layers 2-3
    if include_ignored or include_all:
        return False

    # Layer 2: .gitignore (if available)
    if use_gitignore and gitignore_spec is not None:
        # pathspec expects forward slashes and trailing slash for directories
        rel_str = str(rel_path).replace("\\", "/") + "/"
        if gitignore_spec.match_file(rel_str):
            stats.layer2_gitignore += 1
            stats.excluded_dirs.add(str(rel_path))
            return True
        return False  # .gitignore is authoritative when present

    # Layer 3: Extended defaults (fallback when no .gitignore)
    if dir_name in EXTENDED_EXCLUDE_DIRS:
        stats.layer3_defaults += 1
        stats.excluded_dirs.add(str(rel_path))
        return True

    # Also check for pattern matches like *.egg-info
    for pattern in EXTENDED_EXCLUDE_DIRS:
        if "*" in pattern:
            import fnmatch
            if fnmatch.fnmatch(dir_name, pattern):
                stats.layer3_defaults += 1
                stats.excluded_dirs.add(str(rel_path))
                return True

    return False


def is_hidden_dir(dir_name: str, exclude_hidden: bool) -> bool:
    """Check if directory is hidden and should be excluded."""
    if not exclude_hidden:
        return False
    if dir_name.startswith(".") and dir_name not in ALLOWED_DOT_DIRS:
        return True
    return False


# =============================================================================
# PHASE 1: Directory and Filename Patterns
# =============================================================================

DIR_PATTERNS: dict[str, Category] = {
    r"(^|/)tests?(/|$)": "Tests",
    r"(^|/)__tests__(/|$)": "Tests",
    r"(^|/)spec(/|$)": "Tests",
    r"(^|/)e2e(/|$)": "Tests",
    r"(^|/)docs?(/|$)": "Docs",
    r"(^|/)documentation(/|$)": "Docs",
    r"(^|/)references?(/|$)": "Docs",
    r"(^|/)\.github(/|$)": "Docs",
    r"(^|/)scripts?(/|$)": "Scripts",
    r"(^|/)bin(/|$)": "Scripts",
    r"(^|/)tools(/|$)": "Scripts",
    r"(^|/)src(/|$)": "Source Code",
    r"(^|/)lib(/|$)": "Source Code",
    r"(^|/)pkg(/|$)": "Source Code",
    r"(^|/)app(/|$)": "Source Code",
    r"(^|/)core(/|$)": "Source Code",
    r"(^|/)backend(/|$)": "Source Code",
    r"(^|/)frontend(/|$)": "Source Code",
    r"(^|/)data(/|$)": "Data",
    r"(^|/)datasets?(/|$)": "Data",
    r"(^|/)fixtures(/|$)": "Data",
    r"(^|/)samples?(/|$)": "Data",
    r"(^|/)\.claude(/|$)": "AI Tooling",
    r"(^|/)\.cursor(/|$)": "AI Tooling",
    r"(^|/)\.aider(/|$)": "AI Tooling",
    r"(^|/)prompts?(/|$)": "AI Tooling",
    r"(^|/)config(/|$)": "Config",
    r"(^|/)conf(/|$)": "Config",
    r"(^|/)\.config(/|$)": "Config",
    r"(^|/)\.vscode(/|$)": "Config",
    r"(^|/)\.github/workflows(/|$)": "Config",
}

CONFIG_FILES = {
    ".gitignore", ".gitattributes", ".env", ".env.example", ".env.local",
    ".editorconfig", ".prettierrc", ".eslintrc", ".stylelintrc",
    "Makefile", "Dockerfile", "Procfile", "Vagrantfile",
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "pyproject.toml", "setup.py", "setup.cfg", "MANIFEST.in",
    "requirements.txt", "Pipfile", "Pipfile.lock", "poetry.lock",
    "Gemfile", "Gemfile.lock", "Cargo.toml", "Cargo.lock",
    "go.mod", "go.sum", "composer.json", "composer.lock",
    "tsconfig.json", "jsconfig.json", "babel.config.js",
    "webpack.config.js", "vite.config.js", "rollup.config.js",
    "tox.ini", "pytest.ini", ".coveragerc", "codecov.yml",
}

CONFIG_PATTERNS = [
    r".*\.config\.(js|ts|mjs|cjs|json)$",
    r".*rc\.(js|json|yaml|yml)$",
    r"^\.[a-z]+rc$",
    r".*\.(toml|ini|cfg)$",
    r"docker-compose.*\.ya?ml$",
    r"requirements.*\.txt$",
]

TEST_PATTERNS = [
    r".*_test\.[a-z]+$",
    r".*\.test\.[a-z]+$",
    r".*_spec\.[a-z]+$",
    r".*\.spec\.[a-z]+$",
    r"^test_.*\.[a-z]+$",
    r"^conftest\.py$",
]

DOC_FILES = {"README", "CHANGELOG", "CONTRIBUTING", "LICENSE", "AUTHORS", "HISTORY"}
DOC_EXTENSIONS = {".md", ".rst", ".txt", ".adoc"}

SCRIPT_EXTENSIONS = {".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd"}

SOURCE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
    ".go", ".rs", ".java", ".kt", ".scala", ".clj",
    ".rb", ".php", ".c", ".cpp", ".cc", ".h", ".hpp",
    ".swift", ".m", ".mm", ".cs", ".fs", ".ex", ".exs",
    ".hs", ".ml", ".elm", ".vue", ".svelte",
}

DATA_EXTENSIONS = {
    ".json", ".csv", ".tsv", ".parquet", ".arrow", ".feather",
    ".sqlite", ".db", ".sql", ".xml", ".yaml", ".yml",
    ".pickle", ".pkl", ".npy", ".npz", ".h5", ".hdf5", ".jsonl",
}

AI_FILES = {"SKILL.md", "CLAUDE.md", ".cursorrules", ".cursorignore"}
AI_PATTERNS = [r"^\.aider.*", r".*\.prompt(\.md)?$"]

# Schema/specification files → Docs (they document structure, not contain data)
SCHEMA_FILES = {
    "schema.json", "openapi.json", "openapi.yaml", "openapi.yml",
    "swagger.json", "swagger.yaml", "swagger.yml",
}
SCHEMA_PATTERNS = [
    r".*\.schema\.json$",
    r".*\.schema\.ya?ml$",
    r"(^|/)schema\.sql$",
    r".*\.graphql$",
    r".*\.proto$",
]

# =============================================================================
# PHASE 2: Frontmatter Indicators
# =============================================================================

CONFIG_FRONTMATTER_KEYS = {"settings", "version", "env", "paths", "database", "config"}
AI_FRONTMATTER_KEYS = {"name", "description", "allowed-tools", "model", "prompt"}


def extract_yaml_frontmatter(content: str) -> dict[str, str] | None:
    """Extract YAML frontmatter from content if present."""
    if not content.startswith("---"):
        return None
    lines = content.split("\n")
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return None
    frontmatter = {}
    for line in lines[1:end_idx]:
        if ":" in line:
            key = line.split(":")[0].strip().lower()
            frontmatter[key] = line.split(":", 1)[1].strip() if ":" in line else ""
    return frontmatter


def analyze_frontmatter(content: str) -> Category | None:
    """Phase 2: Analyze YAML frontmatter for category indicators."""
    fm = extract_yaml_frontmatter(content)
    if not fm:
        return None
    keys = set(fm.keys())
    # AI Tooling: has name + description (skill pattern)
    if {"name", "description"} <= keys:
        return "AI Tooling"
    if keys & AI_FRONTMATTER_KEYS:
        if len(keys & AI_FRONTMATTER_KEYS) >= 2:
            return "AI Tooling"
    if keys & CONFIG_FRONTMATTER_KEYS:
        return "Config"
    return None


# =============================================================================
# PHASE 3: Content Structure Analysis
# =============================================================================

TEST_SIGNALS = [
    r"\bassert\b", r"\bexpect\(", r"\bpytest\b", r"\bunittest\b",
    r"\bdescribe\(", r"\bit\(", r"\btest\(", r"\bbeforeEach\b", r"\bafterEach\b",
    r"TestCase", r"@pytest", r"@test",
]

SCRIPT_SIGNALS = [
    r"\bargparse\b", r"\bclick\b", r"\bsys\.argv\b",
    r"if\s+__name__\s*==\s*['\"]__main__['\"]",
    r"^#!", r"\bgetopt\b", r"\bdocopt\b",
]

SOURCE_SIGNALS = [
    r"^class\s+\w+", r"^def\s+\w+", r"^function\s+\w+",
    r"^import\s+", r"^from\s+\w+\s+import", r"^export\s+",
    r"module\.exports", r"^package\s+\w+",
]

DOCS_SIGNALS = [
    r"^#{1,6}\s+\w+",  # Markdown headers
    r"^={3,}$", r"^-{3,}$",  # RST underlines
    r"^\.\.\s+\w+::",  # RST directives
]

DATA_SIGNALS = [
    r'^\s*\[', r'^\s*\{',  # JSON arrays/objects
    r'^"?\w+"?,', r'^\d+,',  # CSV patterns
    r'^[\w-]+\t[\w-]+',  # TSV patterns
]

AI_SIGNALS = [
    r"\bsub-agent\b", r"\bhandoff\b", r"\ballowed-tools\b",
    r"\bsystem prompt\b", r"\bworkflow\b", r"\bClaude\b",
    r"\bagent\b", r"\bskill\b",
]


def analyze_content_structure(content: str) -> Category | None:
    """Phase 3: Analyze content structure for category signals."""
    lines = content[:5000]  # Sample first 5KB

    def has_signals(signals: list[str]) -> int:
        count = 0
        for pattern in signals:
            if re.search(pattern, lines, re.MULTILINE | re.IGNORECASE):
                count += 1
        return count

    # Check each category (order matters for priority)
    if has_signals(TEST_SIGNALS) >= 2:
        return "Tests"
    if has_signals(SCRIPT_SIGNALS) >= 2:
        return "Scripts"
    if has_signals(AI_SIGNALS) >= 2:
        return "AI Tooling"
    if has_signals(SOURCE_SIGNALS) >= 2:
        return "Source Code"
    if has_signals(DOCS_SIGNALS) >= 2:
        return "Docs"
    if has_signals(DATA_SIGNALS) >= 2:
        return "Data"

    return None


# =============================================================================
# PHASE 4: Keyword Detection
# =============================================================================

CATEGORY_KEYWORDS: dict[Category, list[str]] = {
    "Config": ["config", "settings", "workspace", "lint", "dependencies", "environment"],
    "Tests": ["fixtures", "assert", "mock", "unit test", "integration", "coverage"],
    "Docs": ["guide", "overview", "tutorial", "how to", "best practices", "documentation"],
    "Scripts": ["usage:", "examples:", "run:", "startup", "entrypoint"],
    "Source Code": ["class", "def", "function", "import", "export", "module"],
    "Data": ["records", "rows", "columns", "dataset"],
    "AI Tooling": ["skill", "agent", "prompt", "workflow", "Claude", "assistant"],
}


def detect_by_keywords(content: str) -> Category | None:
    """Phase 4: Detect category by keyword frequency."""
    content_lower = content[:10000].lower()
    scores: dict[Category, int] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in content_lower)
        if score >= 2:
            scores[category] = score
    if scores:
        return max(scores, key=lambda k: scores[k])
    return None


# =============================================================================
# Main Categorization Functions
# =============================================================================

def categorize_by_path(filepath: Path) -> Category | None:
    """Phase 1: Categorize based on path and filename patterns only."""
    name = filepath.name
    suffix = filepath.suffix.lower()
    dir_path = str(filepath.parent)

    # Directory patterns
    for pattern, category in DIR_PATTERNS.items():
        if re.search(pattern, dir_path, re.IGNORECASE):
            return category

    # AI tooling files
    if name in AI_FILES:
        return "AI Tooling"
    for pattern in AI_PATTERNS:
        if re.match(pattern, name, re.IGNORECASE):
            return "AI Tooling"

    # Schema/specification files → Docs
    if name in SCHEMA_FILES:
        return "Docs"
    for pattern in SCHEMA_PATTERNS:
        if re.match(pattern, name, re.IGNORECASE):
            return "Docs"

    # Test files
    for pattern in TEST_PATTERNS:
        if re.match(pattern, name, re.IGNORECASE):
            return "Tests"

    # Config files
    if name in CONFIG_FILES:
        return "Config"
    for pattern in CONFIG_PATTERNS:
        if re.match(pattern, name, re.IGNORECASE):
            return "Config"

    # Doc files
    stem = filepath.stem.upper()
    if stem in DOC_FILES or name.upper().startswith("README"):
        return "Docs"

    # Script extensions
    if suffix in SCRIPT_EXTENSIONS:
        return "Scripts"

    # Source code extensions
    if suffix in SOURCE_EXTENSIONS:
        return "Source Code"

    # Data extensions
    if suffix in DATA_EXTENSIONS:
        if dir_path and dir_path != ".":
            return "Data"
        if suffix in {".json", ".yaml", ".yml"}:
            return "Config"
        return "Data"

    return None


def categorize_file(
    filepath: str | Path,
    analyze_content: bool = False,
) -> tuple[Category, Confidence]:
    """
    Categorize a file using 4-phase algorithm.

    Args:
        filepath: Path to the file
        analyze_content: If True, read file and apply Phases 2-4

    Returns:
        Tuple of (category, confidence)
    """
    path = Path(filepath)

    # Phase 1: Path-based categorization
    category = categorize_by_path(path)
    if category:
        return category, "High"

    if not analyze_content:
        return "Other", "Low"

    # Read content for Phases 2-4
    try:
        content = path.read_text(errors="ignore")
    except (OSError, IOError):
        return "Other", "Low"

    # Phase 2: Frontmatter analysis
    fm_category = analyze_frontmatter(content)
    if fm_category:
        return fm_category, "Medium"

    # Phase 3: Content structure analysis
    struct_category = analyze_content_structure(content)
    if struct_category:
        return struct_category, "Medium"

    # Phase 4: Keyword detection
    kw_category = detect_by_keywords(content)
    if kw_category:
        return kw_category, "Low"

    return "Other", "Low"


def categorize_directory(
    root: str | Path,
    analyze_content: bool = False,
    exclude_hidden: bool = True,
    include_ignored: bool = False,
    include_all: bool = False,
) -> tuple[dict[Category, list[tuple[Path, Confidence]]], ExclusionStats]:
    """
    Categorize all files in a directory tree with layered exclusion.

    Args:
        root: Directory to scan
        analyze_content: Enable content analysis (Phases 2-4)
        exclude_hidden: Skip hidden directories (except allowed ones)
        include_ignored: Bypass .gitignore and default exclusions (Layer 2-3)
        include_all: Bypass ALL exclusions including always-exclude (use with caution)

    Returns:
        Tuple of (results dict, exclusion stats)
    """
    root = Path(root).resolve()
    results: dict[Category, list[tuple[Path, Confidence]]] = {
        "Config": [],
        "Tests": [],
        "Docs": [],
        "Scripts": [],
        "Source Code": [],
        "Data": [],
        "AI Tooling": [],
        "Other": [],
    }
    stats = ExclusionStats()

    # Load .gitignore if available
    gitignore_spec, use_gitignore = load_gitignore_spec(root)

    # Track excluded directories to skip their contents
    excluded_prefixes: set[Path] = set()

    for item in sorted(root.rglob("*")):
        rel_path = item.relative_to(root)

        # Check if we're inside an already-excluded directory
        skip = False
        for prefix in excluded_prefixes:
            try:
                rel_path.relative_to(prefix)
                skip = True
                break
            except ValueError:
                pass
        if skip:
            continue

        # Handle directories
        if item.is_dir():
            dir_name = item.name

            # Check hidden directories
            if is_hidden_dir(dir_name, exclude_hidden):
                stats.hidden_dirs += 1
                stats.excluded_dirs.add(str(rel_path))
                excluded_prefixes.add(rel_path)
                continue

            # Check exclusion layers
            if should_exclude_dir(
                item, rel_path, gitignore_spec, use_gitignore,
                include_ignored, include_all, stats
            ):
                excluded_prefixes.add(rel_path)
                continue

            continue  # Don't categorize directories

        # Handle files
        if not item.is_file():
            continue

        category, confidence = categorize_file(item, analyze_content=analyze_content)
        results[category].append((rel_path, confidence))

    # Sort each category
    for cat in results:
        results[cat].sort(key=lambda x: x[0])

    return results, stats


def print_summary(
    results: dict[Category, list[tuple[Path, Confidence]]],
    stats: ExclusionStats | None = None,
) -> None:
    """Print a formatted summary of categorized files."""
    for category, files in results.items():
        if not files:
            continue
        print(f"\n{category} ({len(files)}):")
        for path, confidence in files:
            if confidence == "High":
                print(f"  - {path}")
            else:
                print(f"  - {path} ({confidence})")

    if stats and stats.total() > 0:
        print(f"\n{stats.summary()}")


def main():
    parser = argparse.ArgumentParser(
        description="Categorize project files into Config, Tests, Docs, Scripts, Source Code, Data, AI Tooling, Other.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Directory Exclusion Layers:
  Layer 1: Always excluded (node_modules, .git, venv, __pycache__)
  Layer 2: .gitignore patterns (if pathspec library is installed)
  Layer 3: Default exclusions (dist, build, vendor) when no .gitignore

Use --include-ignored to bypass Layers 2-3.
Use --include-all to bypass ALL layers (use with extreme caution).
""",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="File or directory to categorize (default: current directory)",
    )
    parser.add_argument(
        "--analyze-content", "-a",
        action="store_true",
        help="Enable content analysis (Phases 2-4) for more accurate categorization",
    )
    parser.add_argument(
        "--include-ignored",
        action="store_true",
        help="Include files/dirs normally excluded by .gitignore or defaults (bypasses Layers 2-3)",
    )
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="Include ALL directories including node_modules, .git, venv (bypasses ALL layers - use with caution)",
    )
    parser.add_argument(
        "--no-exclude-hidden",
        action="store_true",
        help="Include hidden directories (those starting with .)",
    )
    args = parser.parse_args()

    target = Path(args.path)

    if target.is_file():
        category, confidence = categorize_file(target, analyze_content=args.analyze_content)
        print(f"{target}: {category} ({confidence})")
    else:
        results, stats = categorize_directory(
            target,
            analyze_content=args.analyze_content,
            exclude_hidden=not args.no_exclude_hidden,
            include_ignored=args.include_ignored,
            include_all=args.include_all,
        )
        print_summary(results, stats)


if __name__ == "__main__":
    main()
