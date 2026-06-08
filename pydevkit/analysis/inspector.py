"""Project inspection helpers."""

import ast
from pathlib import Path
from typing import Dict, List, Set

from pydevkit.deadcode.scanner import scan_deadcode
from pydevkit.readme.analyzer import analyze_project
from pydevkit.utils.file_utils import get_python_files, read_file_safe


BRANCH_NODES = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.Try,
    ast.ExceptHandler,
    ast.BoolOp,
    ast.IfExp,
    ast.Match,
)


def _imports_from_tree(tree: ast.AST) -> Set[str]:
    """Collect top-level imported package roots from an AST."""
    try:
        imports: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                imports.add(node.module.split(".")[0])
        return imports
    except AttributeError:
        return set()


def _function_metrics(node: ast.FunctionDef | ast.AsyncFunctionDef, file_path: Path, root: Path) -> Dict[str, object]:
    """Build complexity metrics for a function node."""
    try:
        end_line = node.end_lineno or node.lineno
        branch_count = sum(1 for child in ast.walk(node) if isinstance(child, BRANCH_NODES))
        arg_count = len(node.args.args) + len(node.args.kwonlyargs) + len(node.args.posonlyargs)
        return {
            "name": node.name,
            "file": str(file_path.relative_to(root)) if file_path.is_relative_to(root) else str(file_path),
            "line": node.lineno,
            "lines": end_line - node.lineno + 1,
            "args": arg_count,
            "branches": branch_count,
        }
    except AttributeError as exc:
        raise RuntimeError(f"Unable to inspect function metrics: {exc}") from exc


def _source_metrics(project_path: str) -> Dict[str, object]:
    """Collect syntax, import, and complexity metrics from Python files."""
    try:
        root = Path(project_path)
        syntax_errors: List[Dict[str, object]] = []
        imports: Set[str] = set()
        function_metrics: List[Dict[str, object]] = []
        total_lines = 0

        for file_path in get_python_files(project_path):
            source = read_file_safe(file_path)
            total_lines += len(source.splitlines())
            if not source.strip():
                continue
            try:
                tree = ast.parse(source, filename=str(file_path))
            except SyntaxError as exc:
                syntax_errors.append(
                    {
                        "file": str(file_path.relative_to(root)) if file_path.is_relative_to(root) else str(file_path),
                        "line": exc.lineno or 0,
                        "message": exc.msg,
                    }
                )
                continue
            imports.update(_imports_from_tree(tree))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    function_metrics.append(_function_metrics(node, file_path, root))

        return {
            "total_lines": total_lines,
            "imports": sorted(imports),
            "syntax_errors": syntax_errors,
            "function_metrics": function_metrics,
        }
    except OSError as exc:
        raise RuntimeError(f"Unable to inspect source metrics: {exc}") from exc


def inspect_project(project_path: str) -> Dict[str, object]:
    """Return a consolidated project inspection report."""
    try:
        metadata = analyze_project(project_path)
        source_metrics = _source_metrics(project_path)
        deadcode = scan_deadcode(project_path)
        python_files = metadata.get("python_files", [])
        function_metrics = source_metrics["function_metrics"]
        return {
            "project": metadata,
            "summary": {
                "python_files": len(python_files) if isinstance(python_files, list) else 0,
                "functions": len(metadata.get("functions", [])),
                "classes": len(metadata.get("classes", [])),
                "imports": len(source_metrics["imports"]),
                "deadcode": len(deadcode),
                "syntax_errors": len(source_metrics["syntax_errors"]),
                "total_lines": source_metrics["total_lines"],
                "has_tests": bool(metadata.get("has_tests")),
            },
            "imports": source_metrics["imports"],
            "deadcode": deadcode,
            "syntax_errors": source_metrics["syntax_errors"],
            "function_metrics": function_metrics,
        }
    except RuntimeError:
        raise
