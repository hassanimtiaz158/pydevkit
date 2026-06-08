"""Project health checks for PyDevKit."""

import importlib.util
from pathlib import Path
from typing import Dict, List

from pydevkit.analysis.inspector import inspect_project
from pydevkit.utils.config import load_config
from pydevkit.utils.file_utils import read_file_safe


Issue = Dict[str, object]


PACKAGE_IMPORT_OVERRIDES = {
    "beautifulsoup4": "bs4",
    "opencv-python": "cv2",
    "pillow": "PIL",
    "pyyaml": "yaml",
    "python-dotenv": "dotenv",
    "scikit-learn": "sklearn",
}


def _issue(code: str, severity: str, message: str, suggestion: str) -> Issue:
    """Create a normalized doctor issue."""
    try:
        return {
            "code": code,
            "severity": severity,
            "message": message,
            "suggestion": suggestion,
        }
    except RuntimeError:
        raise


def _dependency_import_name(requirement: str) -> str:
    """Infer an import package name from a requirement line."""
    try:
        package = requirement.split(";", 1)[0].strip()
        for separator in ("==", ">=", "<=", "~=", "!=", ">", "<"):
            package = package.split(separator, 1)[0].strip()
        normalized = package.lower().replace("_", "-")
        return PACKAGE_IMPORT_OVERRIDES.get(normalized, normalized.replace("-", "_"))
    except AttributeError:
        return ""


def _missing_runtime_imports(imports: List[str]) -> List[str]:
    """Return imported modules that cannot be resolved in the current environment."""
    try:
        missing = []
        for name in imports:
            if name.startswith("."):
                continue
            try:
                if importlib.util.find_spec(name) is None:
                    missing.append(name)
            except (ImportError, ModuleNotFoundError, ValueError):
                missing.append(name)
        return sorted(set(missing))
    except RuntimeError:
        raise


def _unused_dependencies(dependencies: List[str], imports: List[str]) -> List[str]:
    """Return requirements that do not appear in collected imports."""
    try:
        imported = set(imports)
        unused = []
        for requirement in dependencies:
            import_name = _dependency_import_name(requirement)
            if import_name and import_name not in imported:
                unused.append(requirement)
        return unused
    except RuntimeError:
        raise


def _complexity_issues(report: Dict[str, object], project_path: str) -> List[Issue]:
    """Create issues for functions that exceed configured complexity limits."""
    try:
        config = load_config(project_path)
        doctor_config = config.get("doctor", {})
        max_lines = int(doctor_config.get("max_function_lines", 80))
        max_args = int(doctor_config.get("max_function_args", 6))
        max_branches = int(doctor_config.get("max_branches", 12))
        issues: List[Issue] = []
        for metric in report.get("function_metrics", []):
            if not isinstance(metric, dict):
                continue
            location = f"{metric.get('file')}:{metric.get('line')}"
            if int(metric.get("lines", 0)) > max_lines:
                issues.append(_issue("long-function", "medium", f"{location} is {metric.get('lines')} lines long.", "Split the function into smaller units."))
            if int(metric.get("args", 0)) > max_args:
                issues.append(_issue("many-args", "medium", f"{location} has {metric.get('args')} arguments.", "Group related arguments or introduce a small data object."))
            if int(metric.get("branches", 0)) > max_branches:
                issues.append(_issue("complex-function", "medium", f"{location} has {metric.get('branches')} branch points.", "Reduce branching or extract decision logic."))
        return issues
    except (RuntimeError, ValueError) as exc:
        raise RuntimeError(f"Unable to evaluate complexity: {exc}") from exc


def run_doctor(project_path: str) -> Dict[str, object]:
    """Run project health checks and return a normalized report."""
    try:
        root = Path(project_path)
        report = inspect_project(project_path)
        project = report.get("project", {})
        dependencies = project.get("dependencies", []) if isinstance(project, dict) else []
        imports = report.get("imports", [])
        issues: List[Issue] = []

        if not (root / "README.md").exists():
            issues.append(_issue("missing-readme", "medium", "README.md is missing.", "Run pydevkit readme . --no-ai or create a README."))
        if not any((root / name).exists() for name in ("LICENSE", "LICENSE.md", "LICENSE.txt")):
            issues.append(_issue("missing-license", "low", "License file is missing.", "Add a LICENSE file that matches your package metadata."))
        if not bool(project.get("has_tests")):
            issues.append(_issue("missing-tests", "medium", "No tests directory was found.", "Run pydevkit testgen . --offline to bootstrap tests."))
        if not (root / ".env.example").exists():
            issues.append(_issue("missing-env-example", "low", ".env.example is missing.", "Add documented environment variable examples."))

        for syntax_error in report.get("syntax_errors", []):
            if isinstance(syntax_error, dict):
                issues.append(_issue("syntax-error", "high", f"{syntax_error.get('file')}:{syntax_error.get('line')} {syntax_error.get('message')}", "Fix the syntax error before running generators."))

        for missing_import in _missing_runtime_imports(imports if isinstance(imports, list) else []):
            issues.append(_issue("missing-import", "high", f"Import '{missing_import}' cannot be resolved in this environment.", "Install the dependency or fix the import name."))

        for dependency in _unused_dependencies(dependencies if isinstance(dependencies, list) else [], imports if isinstance(imports, list) else []):
            issues.append(_issue("possibly-unused-dependency", "low", f"Requirement '{dependency}' was not observed in imports.", "Remove it if it is not needed at runtime."))

        issues.extend(_complexity_issues(report, project_path))
        deadcode = report.get("deadcode", [])
        if isinstance(deadcode, list) and deadcode:
            issues.append(_issue("deadcode", "medium", f"{len(deadcode)} unused symbols were detected.", "Run pydevkit deadcode . and review the findings."))

        return {
            "summary": {
                "issues": len(issues),
                "high": sum(1 for item in issues if item.get("severity") == "high"),
                "medium": sum(1 for item in issues if item.get("severity") == "medium"),
                "low": sum(1 for item in issues if item.get("severity") == "low"),
            },
            "issues": issues,
            "inspection": report["summary"],
        }
    except RuntimeError:
        raise
