"""Function extraction for pytest generation."""

import ast
from pathlib import Path
from typing import Dict, List

from pydevkit.utils.file_utils import get_python_files, read_file_safe


def _annotation_to_string(annotation: ast.AST | None) -> str | None:
    """Convert an AST annotation to source-like text."""
    try:
        if annotation is None:
            return None
        return ast.unparse(annotation)
    except (AttributeError, ValueError):
        return None


def _format_arg(arg: ast.arg) -> str:
    """Format a function argument with its type annotation when present."""
    try:
        annotation = _annotation_to_string(arg.annotation)
        return f"{arg.arg}: {annotation}" if annotation else arg.arg
    except AttributeError:
        return ""


def _is_public_function(name: str) -> bool:
    """Return True when a function should be considered for test generation."""
    try:
        return not name.startswith("_") and not (name.startswith("__") and name.endswith("__"))
    except AttributeError:
        return False


def _is_test_file(file_path: Path) -> bool:
    """Return True when a file is inside a tests folder or named as a test."""
    try:
        return "tests" in file_path.parts or file_path.name.startswith("test_")
    except AttributeError:
        return False


def extract_functions(project_path: str) -> List[Dict[str, object]]:
    """Extract public functions and metadata from a project."""
    try:
        root = Path(project_path)
        functions: List[Dict[str, object]] = []

        for file_path in get_python_files(project_path):
            if _is_test_file(file_path):
                continue
            source = read_file_safe(file_path)
            if not source.strip():
                continue
            try:
                tree = ast.parse(source, filename=str(file_path))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_public_function(node.name):
                    args = [_format_arg(arg) for arg in node.args.args]
                    functions.append(
                        {
                            "name": node.name,
                            "args": [arg for arg in args if arg],
                            "return_type": _annotation_to_string(node.returns),
                            "docstring": ast.get_docstring(node) or "",
                            "file": str(file_path.relative_to(root)) if file_path.is_relative_to(root) else str(file_path),
                            "line": node.lineno,
                        }
                    )
        return functions
    except OSError as exc:
        raise RuntimeError(f"Function extraction failed: {exc}") from exc
