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


def _module_name(file_path: Path, root: Path) -> str:
    """Return an import-style module name for a Python file."""
    try:
        relative = file_path.relative_to(root).with_suffix("")
        parts = [part for part in relative.parts if part != "__init__"]
        return ".".join(parts)
    except ValueError:
        return file_path.stem


def _project_modules(project_path: str) -> Set[str]:
    """Return importable module names that belong to the project."""
    try:
        root = Path(project_path)
        modules: Set[str] = set()
        for file_path in get_python_files(project_path):
            module = _module_name(file_path, root)
            if module:
                modules.add(module)
                modules.add(module.split(".", 1)[0])
        return modules
    except OSError:
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
        import_edges: List[Dict[str, str]] = []
        function_metrics: List[Dict[str, object]] = []
        total_lines = 0

        for file_path in get_python_files(project_path):
            module_name = _module_name(file_path, root)
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
            file_imports = _imports_from_tree(tree)
            imports.update(file_imports)
            for imported in sorted(file_imports):
                import_edges.append({"from": module_name, "to": imported})
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    function_metrics.append(_function_metrics(node, file_path, root))

        return {
            "total_lines": total_lines,
            "imports": sorted(imports),
            "import_edges": import_edges,
            "project_modules": sorted(_project_modules(project_path)),
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
            "import_edges": source_metrics["import_edges"],
            "project_modules": source_metrics["project_modules"],
            "deadcode": deadcode,
            "syntax_errors": source_metrics["syntax_errors"],
            "function_metrics": function_metrics,
        }
    except RuntimeError:
        raise
