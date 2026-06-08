"""File helpers for PyDevKit."""

from pathlib import Path
from typing import List


def get_python_files(path: str) -> List[Path]:
    """Return Python files below a path, excluding cache folders."""
    try:
        root = Path(path)
        if not root.exists():
            return []
        if root.is_file():
            return [root] if root.suffix == ".py" and "__pycache__" not in root.parts else []
        return sorted(
            file_path
            for file_path in root.rglob("*.py")
            if "__pycache__" not in file_path.parts
        )
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
