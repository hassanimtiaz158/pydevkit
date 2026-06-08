"""Project analyzer used for README generation."""

import ast
from pathlib import Path
from typing import Dict, List

from pydevkit.utils.file_utils import get_python_files, read_file_safe


def _public_name(name: str) -> bool:
    """Return True when a Python symbol is public."""
    try:
        return not name.startswith("_")
    except AttributeError:
        return False


def _relative_name(path: Path, root: Path) -> str:
    """Return a path relative to root when possible."""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _detect_entry_point(root: Path, python_files: List[Path]) -> str | None:
    """Detect a likely Python entry point file."""
    try:
        preferred = ["main.py", "app.py", "cli.py", "server.py", "manage.py"]
        for name in preferred:
            candidate = root / name
            if candidate.exists():
                return _relative_name(candidate, root)
        for file_path in python_files:
            source = read_file_safe(file_path)
            if 'if __name__ == "__main__"' in source or "if __name__ == '__main__'" in source:
                return _relative_name(file_path, root)
        return None
    except OSError:
        return None


def analyze_project(project_path: str) -> Dict[str, object]:
    """Analyze a Python project and return README-friendly metadata."""
    try:
        root = Path(project_path)
        python_files = get_python_files(project_path)
        functions: List[Dict[str, str]] = []
        classes: List[Dict[str, str]] = []

        for file_path in python_files:
            source = read_file_safe(file_path)
            if not source.strip():
                continue
            try:
                tree = ast.parse(source, filename=str(file_path))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _public_name(node.name):
                    functions.append(
                        {
                            "name": node.name,
                            "docstring": ast.get_docstring(node) or "",
                            "file": _relative_name(file_path, root),
                        }
                    )
                elif isinstance(node, ast.ClassDef) and _public_name(node.name):
                    classes.append(
                        {
                            "name": node.name,
                            "docstring": ast.get_docstring(node) or "",
                            "file": _relative_name(file_path, root),
                        }
                    )

        requirements = root / "requirements.txt"
        dependencies = [
            line.strip()
            for line in read_file_safe(requirements).splitlines()
            if line.strip() and not line.strip().startswith("#")
        ] if requirements.exists() else []

        return {
            "project_name": root.name,
            "python_files": [_relative_name(file_path, root) for file_path in python_files],
            "functions": functions,
            "classes": classes,
            "dependencies": dependencies,
            "has_tests": (root / "tests").exists(),
            "entry_point": _detect_entry_point(root, python_files),
        }
    except OSError as exc:
        raise RuntimeError(f"Project analysis failed: {exc}") from exc
