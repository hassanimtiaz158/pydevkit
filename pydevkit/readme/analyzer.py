"""Project analyzer used for README generation."""

import ast
import re
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


def _literal_setup_kwargs(setup_path: Path) -> Dict[str, object]:
    """Extract simple literal setup.py keyword arguments."""
    try:
        if not setup_path.exists():
            return {}
        source = read_file_safe(setup_path)
        tree = ast.parse(source, filename=str(setup_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "setup":
                values: Dict[str, object] = {}
                for keyword in node.keywords:
                    if keyword.arg is None:
                        continue
                    try:
                        values[keyword.arg] = ast.literal_eval(keyword.value)
                    except (ValueError, SyntaxError):
                        continue
                return values
        return {}
    except (OSError, SyntaxError):
        return {}


def _pyproject_metadata(pyproject_path: Path) -> Dict[str, object]:
    """Extract common project metadata from pyproject.toml with simple parsing."""
    try:
        if not pyproject_path.exists():
            return {}
        metadata: Dict[str, object] = {}
        section = ""
        for line in read_file_safe(pyproject_path).splitlines():
            stripped = line.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                section = stripped.strip("[]")
                continue
            if section != "project" or "=" not in stripped:
                continue
            key, raw_value = [part.strip() for part in stripped.split("=", 1)]
            match = re.match(r'^["\'](.*)["\']$', raw_value)
            if match:
                metadata[key] = match.group(1)
        return metadata
    except (OSError, re.error):
        return {}


def _metadata(root: Path) -> Dict[str, object]:
    """Collect package metadata from modern and legacy packaging files."""
    try:
        project_name = root.name or root.resolve().name
        setup_metadata = _literal_setup_kwargs(root / "setup.py")
        pyproject_metadata = _pyproject_metadata(root / "pyproject.toml")
        merged = {**setup_metadata, **pyproject_metadata}
        entry_points = setup_metadata.get("entry_points", {})
        console_scripts = []
        if isinstance(entry_points, dict):
            scripts = entry_points.get("console_scripts", [])
            if isinstance(scripts, list):
                console_scripts = [str(item) for item in scripts]
        return {
            "package_name": str(merged.get("name", project_name)),
            "version": str(merged.get("version", "")),
            "license": str(merged.get("license", "MIT")),
            "console_scripts": console_scripts,
        }
    except (OSError, TypeError) as exc:
        raise RuntimeError(f"Unable to read project metadata: {exc}") from exc


def analyze_project(project_path: str) -> Dict[str, object]:
    """Analyze a Python project and return README-friendly metadata."""
    try:
        root = Path(project_path)
        project_name = root.name or root.resolve().name
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

        package_metadata = _metadata(root)
        return {
            "project_name": project_name,
            **package_metadata,
            "python_files": [_relative_name(file_path, root) for file_path in python_files],
            "functions": functions,
            "classes": classes,
            "dependencies": dependencies,
            "has_tests": (root / "tests").exists(),
            "entry_point": _detect_entry_point(root, python_files),
        }
    except OSError as exc:
        raise RuntimeError(f"Project analysis failed: {exc}") from exc
