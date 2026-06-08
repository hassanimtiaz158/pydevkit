"""AST-based dead code scanner."""

import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple

from pydevkit.utils.file_utils import get_python_files, read_file_safe, write_file


Definition = Tuple[Path, int, str, str]


def _is_skipped_name(name: str) -> bool:
    """Return True when a symbol should not be reported."""
    try:
        return name in {"__init__", "__main__"} or (name.startswith("__") and name.endswith("__")) or name.startswith("_")
    except AttributeError:
        return True


def _target_names(target: ast.AST) -> Set[str]:
    """Extract assigned variable names from an AST assignment target."""
    try:
        names: Set[str] = set()
        if isinstance(target, ast.Name):
            names.add(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for item in target.elts:
                names.update(_target_names(item))
        return names
    except AttributeError:
        return set()


def _import_names(node: ast.AST) -> List[str]:
    """Extract import binding names from an import node."""
    try:
        names: List[str] = []
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if alias.name == "*":
                    continue
                names.append(alias.asname or alias.name.split(".")[0])
        return names
    except AttributeError:
        return []


def _collect_definitions(tree: ast.AST, file_path: Path) -> List[Definition]:
    """Collect public function, import, and variable definitions."""
    try:
        definitions: List[Definition] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not _is_skipped_name(node.name):
                definitions.append((file_path, node.lineno, "function", node.name))
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for name in _import_names(node):
                    if not _is_skipped_name(name):
                        definitions.append((file_path, node.lineno, "import", name))
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    for name in _target_names(target):
                        if not _is_skipped_name(name):
                            definitions.append((file_path, node.lineno, "variable", name))
            elif isinstance(node, ast.AnnAssign):
                for name in _target_names(node.target):
                    if not _is_skipped_name(name):
                        definitions.append((file_path, node.lineno, "variable", name))
        return definitions
    except AttributeError:
        return []


def _collect_usages(tree: ast.AST) -> Set[str]:
    """Collect symbol names used by the AST."""
    try:
        used: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used.add(node.id)
            elif isinstance(node, ast.Attribute):
                used.add(node.attr)
        return used
    except AttributeError:
        return set()


def scan_deadcode(project_path: str) -> List[Dict[str, object]]:
    """Scan a project for unused public functions, imports, and variables."""
    try:
        definitions: List[Definition] = []
        used_names: Set[str] = set()

        for file_path in get_python_files(project_path):
            source = read_file_safe(file_path)
            if not source.strip():
                continue
            try:
                tree = ast.parse(source, filename=str(file_path))
            except SyntaxError:
                continue
            definitions.extend(_collect_definitions(tree, file_path))
            used_names.update(_collect_usages(tree))

        results: List[Dict[str, object]] = []
        for file_path, line, symbol_type, name in definitions:
            if name not in used_names:
                suggestion = f"Remove this unused {symbol_type}" if symbol_type in {"function", "import", "variable"} else "Consider deleting"
                results.append(
                    {
                        "file": str(file_path),
                        "line": line,
                        "type": symbol_type,
                        "name": name,
                        "suggestion": suggestion,
                    }
                )
        return results
    except (OSError, RuntimeError) as exc:
        raise RuntimeError(f"Dead code scan failed: {exc}") from exc


def remove_unused_imports(project_path: str, results: List[Dict[str, object]]) -> int:
    """Remove simple unused import lines identified by scan_deadcode."""
    try:
        imports_by_file: Dict[Path, Set[int]] = {}
        for item in results:
            if item.get("type") == "import":
                imports_by_file.setdefault(Path(str(item["file"])), set()).add(int(item["line"]))

        removed = 0
        for file_path, lines in imports_by_file.items():
            source = read_file_safe(file_path)
            if not source:
                continue
            kept_lines = []
            for index, line in enumerate(source.splitlines(), start=1):
                if index in lines and (line.lstrip().startswith("import ") or line.lstrip().startswith("from ")):
                    removed += 1
                    continue
                kept_lines.append(line)
            trailing_newline = "\n" if source.endswith(("\n", "\r\n")) else ""
            write_file(file_path, "\n".join(kept_lines) + trailing_newline)
        return removed
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"Unable to remove unused imports: {exc}") from exc
