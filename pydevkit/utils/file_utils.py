"""File helpers for PyDevKit."""

from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, List


DEFAULT_SKIP_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "htmlcov",
    "node_modules",
    "site-packages",
    "venv",
}


def _load_ignore_patterns(root: Path) -> List[str]:
    """Load simple ignore patterns from .pydevkitignore and .gitignore."""
    try:
        patterns: List[str] = []
        for ignore_file in (root / ".pydevkitignore", root / ".gitignore"):
            if not ignore_file.exists():
                continue
            for line in read_file_safe(ignore_file).splitlines():
                cleaned = line.strip()
                if cleaned and not cleaned.startswith("#"):
                    patterns.append(cleaned)
        return patterns
    except OSError:
        return []


def _matches_ignore(path: Path, root: Path, patterns: Iterable[str]) -> bool:
    """Return True when a path matches a simple ignore pattern."""
    try:
        relative = path.relative_to(root).as_posix()
        for pattern in patterns:
            normalized = pattern.rstrip("/").replace("\\", "/")
            if fnmatch(relative, normalized) or fnmatch(relative, f"{normalized}/**"):
                return True
            if "/" not in normalized and normalized in path.parts:
                return True
        return False
    except ValueError:
        return False


def get_python_files(path: str) -> List[Path]:
    """Return Python files below a path, excluding ignored/generated folders."""
    try:
        root = Path(path)
        if not root.exists():
            return []
        if root.is_file():
            return [root] if root.suffix == ".py" and not any(part in DEFAULT_SKIP_DIRS for part in root.parts) else []

        ignore_patterns = _load_ignore_patterns(root)
        python_files: List[Path] = []
        stack = [root]
        while stack:
            current = stack.pop()
            try:
                for child in current.iterdir():
                    if child.is_dir():
                        if child.name in DEFAULT_SKIP_DIRS or _matches_ignore(child, root, ignore_patterns):
                            continue
                        stack.append(child)
                    elif child.suffix == ".py" and not _matches_ignore(child, root, ignore_patterns):
                        python_files.append(child)
            except OSError:
                continue
        return sorted(python_files)
    except (OSError, RuntimeError):
        return []


def read_file_safe(path: Path) -> str:
    """Read a text file while tolerating encoding issues."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""
    except OSError:
        return ""


def write_file(path: Path, content: str) -> None:
    """Write text to a file, creating parent directories when required."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise OSError(f"Unable to write file {path}: {exc}") from exc
