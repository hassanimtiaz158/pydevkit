"""AST-based dead code scanner."""

import ast
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Set

from pydevkit.utils.config import load_config
from pydevkit.utils.file_utils import get_python_files, read_file_safe, write_file


@dataclass(frozen=True)
class Definition:
    """A symbol definition that can be reported as dead code."""

    file: Path
    line: int
    symbol_type: str
    name: str


@dataclass(frozen=True)
class ImportBinding:
    """A single import alias binding found in a source file."""

    file: Path
    line: int
    name: str


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
    """Collect top-level public definitions with conservative scope rules."""
    try:
        definitions: List[Definition] = []
        body = tree.body if isinstance(tree, ast.Module) else []
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not _is_skipped_name(node.name):
                definitions.append(Definition(file_path, node.lineno, "function", node.name))
            elif isinstance(node, ast.ClassDef) and not _is_skipped_name(node.name):
                definitions.append(Definition(file_path, node.lineno, "class", node.name))
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and not _is_skipped_name(child.name):
                        definitions.append(Definition(file_path, child.lineno, "method", child.name))
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for name in _import_names(node):
                    if not _is_skipped_name(name):
                        definitions.append(Definition(file_path, node.lineno, "import", name))
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    for name in _target_names(target):
                        if not _is_skipped_name(name):
                            definitions.append(Definition(file_path, node.lineno, "variable", name))
            elif isinstance(node, ast.AnnAssign):
                for name in _target_names(node.target):
                    if not _is_skipped_name(name):
                        definitions.append(Definition(file_path, node.lineno, "variable", name))
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


def _literal_string_names(node: ast.AST) -> Set[str]:
    """Extract literal string values from a node used for public exports."""
    try:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return {node.value}
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            names: Set[str] = set()
            for item in node.elts:
                names.update(_literal_string_names(item))
            return names
        return set()
    except AttributeError:
        return set()


def _collect_exported_names(tree: ast.AST) -> Set[str]:
    """Collect names declared through simple __all__ export patterns."""
    try:
        exported: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                if any(isinstance(target, ast.Name) and target.id == "__all__" for target in targets):
                    exported.update(_literal_string_names(node.value))
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                receiver = node.func.value
                if not (isinstance(receiver, ast.Name) and receiver.id == "__all__"):
                    continue
                if node.func.attr == "append" and node.args:
                    exported.update(_literal_string_names(node.args[0]))
                elif node.func.attr == "extend" and node.args:
                    exported.update(_literal_string_names(node.args[0]))
        return exported
    except AttributeError:
        return set()


def _is_test_path(file_path: Path) -> bool:
    """Return True when a path appears to be a test file."""
    try:
        return "tests" in file_path.parts or file_path.name.startswith("test_")
    except AttributeError:
        return False


def _relative_path(file_path: Path, root: Path) -> str:
    """Return a portable relative path for matching and reporting."""
    try:
        return file_path.relative_to(root).as_posix()
    except ValueError:
        return file_path.as_posix()


def _is_ignored_file(file_path: Path, root: Path, patterns: List[str]) -> bool:
    """Return True when a file matches configured ignore patterns."""
    try:
        relative = _relative_path(file_path, root)
        for pattern in patterns:
            normalized = pattern.replace("\\", "/").strip()
            if not normalized:
                continue
            if fnmatch(relative, normalized) or fnmatch(relative, f"**/{normalized}"):
                return True
            if normalized.endswith("/*") and relative.startswith(normalized[:-1]):
                return True
        return False
    except TypeError:
        return False


def _confidence_rank(value: str) -> int:
    """Return a comparable rank for confidence labels."""
    try:
        return {"low": 0, "medium": 1, "high": 2}.get(value, 0)
    except TypeError:
        return 0


def _result_confidence(symbol_type: str) -> str:
    """Return a confidence label for a result type."""
    try:
        if symbol_type == "import":
            return "high"
        if symbol_type == "variable":
            return "high"
        if symbol_type in {"class", "function", "method"}:
            return "medium"
        return "low"
    except RuntimeError:
        return "low"


def _result_severity(symbol_type: str, confidence: str) -> str:
    """Return a severity label for a result."""
    try:
        if symbol_type == "import":
            return "high"
        if symbol_type == "variable":
            return "medium"
        if confidence == "medium":
            return "medium"
        return "low"
    except RuntimeError:
        return "low"


def _collect_import_bindings(tree: ast.AST, file_path: Path) -> List[ImportBinding]:
    """Collect import bindings for import-specific rewrites."""
    try:
        bindings: List[ImportBinding] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for name in _import_names(node):
                    bindings.append(ImportBinding(file_path, node.lineno, name))
        return bindings
    except AttributeError:
        return []


def scan_deadcode(
    project_path: str,
    include_tests: bool | None = None,
    ignore_names: List[str] | None = None,
    ignore_files: List[str] | None = None,
    min_confidence: str | None = None,
) -> List[Dict[str, object]]:
    """Scan a project for unused public functions, imports, and variables."""
    try:
        root = Path(project_path)
        config = load_config(project_path)
        deadcode_config = config.get("deadcode", {})
        active_include_tests = bool(deadcode_config.get("include_tests", False)) if include_tests is None else include_tests
        active_ignore_names = set(ignore_names if ignore_names is not None else deadcode_config.get("ignore_names", []))
        active_ignore_files = list(ignore_files if ignore_files is not None else deadcode_config.get("ignore_files", []))
        active_min_confidence = min_confidence or str(deadcode_config.get("min_confidence", "low"))
        definitions: List[Definition] = []
        used_names: Set[str] = set()

        for file_path in get_python_files(project_path):
            if not active_include_tests and _is_test_path(file_path):
                continue
            if _is_ignored_file(file_path, root, active_ignore_files):
                continue
            source = read_file_safe(file_path)
            if not source.strip():
                continue
            try:
                tree = ast.parse(source, filename=str(file_path))
            except SyntaxError:
                continue
            definitions.extend(_collect_definitions(tree, file_path))
            used_names.update(_collect_usages(tree))
            used_names.update(_collect_exported_names(tree))

        results: List[Dict[str, object]] = []
        seen: Set[tuple[str, int, str, str]] = set()
        for definition in definitions:
            key = (str(definition.file), definition.line, definition.symbol_type, definition.name)
            if key in seen:
                continue
            seen.add(key)
            if definition.name not in used_names:
                if definition.name in active_ignore_names:
                    continue
                confidence = _result_confidence(definition.symbol_type)
                if _confidence_rank(confidence) < _confidence_rank(active_min_confidence):
                    continue
                suggestion = (
                    f"Remove this unused {definition.symbol_type}"
                    if definition.symbol_type in {"function", "import", "variable", "class", "method"}
                    else "Consider deleting"
                )
                results.append(
                    {
                        "file": str(definition.file),
                        "line": definition.line,
                        "type": definition.symbol_type,
                        "name": definition.name,
                        "suggestion": suggestion,
                        "severity": _result_severity(definition.symbol_type, confidence),
                        "confidence": confidence,
                    }
                )
        return results
    except (OSError, RuntimeError, TypeError) as exc:
        raise RuntimeError(f"Dead code scan failed: {exc}") from exc


def _format_alias(alias: ast.alias) -> str:
    """Render an import alias."""
    try:
        return f"{alias.name} as {alias.asname}" if alias.asname else alias.name
    except AttributeError:
        return ""


def _rewrite_import_line(line: str, node: ast.Import | ast.ImportFrom, unused_names: Set[str]) -> tuple[str | None, int]:
    """Rewrite a simple one-line import statement by removing unused aliases."""
    try:
        if node.end_lineno != node.lineno:
            return line, 0
        kept = [alias for alias in node.names if (alias.asname or alias.name.split(".")[0]) not in unused_names]
        removed = len(node.names) - len(kept)
        if removed == 0:
            return line, 0
        if not kept:
            return None, removed
        indentation = line[: len(line) - len(line.lstrip())]
        if isinstance(node, ast.Import):
            return f"{indentation}import {', '.join(_format_alias(alias) for alias in kept)}", removed
        module = "." * node.level + (node.module or "")
        return f"{indentation}from {module} import {', '.join(_format_alias(alias) for alias in kept)}", removed
    except AttributeError:
        return line, 0


def remove_unused_imports(project_path: str, results: List[Dict[str, object]], dry_run: bool = False) -> int:
    """Remove unused import aliases identified by scan_deadcode."""
    try:
        imports_by_file: Dict[Path, Set[str]] = {}
        for item in results:
            if item.get("type") == "import":
                imports_by_file.setdefault(Path(str(item["file"])), set()).add(str(item["name"]))

        removed = 0
        for file_path, unused_names in imports_by_file.items():
            source = read_file_safe(file_path)
            if not source:
                continue
            try:
                tree = ast.parse(source, filename=str(file_path))
            except SyntaxError:
                continue
            import_nodes = {
                node.lineno: node
                for node in ast.walk(tree)
                if isinstance(node, (ast.Import, ast.ImportFrom))
            }
            changed = False
            kept_lines: List[str] = []
            for index, line in enumerate(source.splitlines(), start=1):
                node = import_nodes.get(index)
                if node is None:
                    kept_lines.append(line)
                    continue
                rewritten, removed_count = _rewrite_import_line(line, node, unused_names)
                removed += removed_count
                changed = changed or removed_count > 0
                if rewritten is not None:
                    kept_lines.append(rewritten)
            trailing_newline = "\n" if source.endswith(("\n", "\r\n")) else ""
            if changed and not dry_run:
                write_file(file_path, "\n".join(kept_lines) + trailing_newline)
        return removed
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"Unable to remove unused imports: {exc}") from exc
