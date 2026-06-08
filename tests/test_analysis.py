"""Tests for project inspection and doctor checks."""

from pathlib import Path

from pydevkit.analysis.doctor import run_doctor
from pydevkit.analysis.inspector import inspect_project
from pydevkit.deadcode.scanner import scan_deadcode
from pydevkit.utils.config import load_config


def test_load_config_reads_pydevkit_toml(tmp_path: Path) -> None:
    """Assert .pydevkit.toml values are loaded into config."""
    try:
        (tmp_path / ".pydevkit.toml").write_text(
            "[deadcode]\n"
            'ignore_names = ["keep_me"]\n'
            "include_tests = true\n"
            "\n"
            "[testgen]\n"
            "offline = true\n",
            encoding="utf-8",
        )

        config = load_config(str(tmp_path))

        assert config["deadcode"]["ignore_names"] == ["keep_me"]
        assert config["deadcode"]["include_tests"] is True
        assert config["testgen"]["offline"] is True
    except RuntimeError as exc:
        raise AssertionError(f"load_config failed unexpectedly: {exc}") from exc


def test_load_config_normalizes_empty_output(tmp_path: Path) -> None:
    """Assert empty configured output is normalized to None."""
    try:
        (tmp_path / ".pydevkit.toml").write_text(
            "[testgen]\n"
            'output = ""\n',
            encoding="utf-8",
        )

        config = load_config(str(tmp_path))

        assert config["testgen"]["output"] is None
    except RuntimeError as exc:
        raise AssertionError(f"load_config failed unexpectedly: {exc}") from exc


def test_deadcode_respects_config_ignore_names(tmp_path: Path) -> None:
    """Assert configured names are ignored by the deadcode scanner."""
    try:
        (tmp_path / ".pydevkit.toml").write_text(
            "[deadcode]\n"
            'ignore_names = ["keep_me"]\n',
            encoding="utf-8",
        )
        (tmp_path / "module.py").write_text(
            "def keep_me() -> int:\n"
            "    return 1\n"
            "\n"
            "def remove_me() -> int:\n"
            "    return 2\n",
            encoding="utf-8",
        )

        names = {str(item["name"]) for item in scan_deadcode(str(tmp_path))}

        assert "keep_me" not in names
        assert "remove_me" in names
    except RuntimeError as exc:
        raise AssertionError(f"scan_deadcode failed unexpectedly: {exc}") from exc


def test_inspect_project_returns_summary() -> None:
    """Assert inspect_project returns useful summary metrics."""
    try:
        report = inspect_project("sample_project")

        assert report["summary"]["python_files"] >= 1
        assert report["summary"]["functions"] >= 1
        assert "deadcode" in report
        assert "function_metrics" in report
        assert "project_modules" in report
        assert "import_edges" in report
    except RuntimeError as exc:
        raise AssertionError(f"inspect_project failed unexpectedly: {exc}") from exc


def test_doctor_does_not_flag_local_imports_as_missing(tmp_path: Path) -> None:
    """Assert doctor treats project modules as local imports."""
    try:
        (tmp_path / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")
        (tmp_path / "app.py").write_text("import helper\n\nresult = helper.VALUE\n", encoding="utf-8")
        (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
        (tmp_path / "LICENSE").write_text("MIT\n", encoding="utf-8")
        (tmp_path / ".env.example").write_text("KEY=value\n", encoding="utf-8")
        (tmp_path / "tests").mkdir()

        report = run_doctor(str(tmp_path))
        missing_imports = [
            item for item in report["issues"]
            if item["code"] == "missing-import"
        ]

        assert missing_imports == []
    except RuntimeError as exc:
        raise AssertionError(f"run_doctor failed unexpectedly: {exc}") from exc


def test_run_doctor_reports_health_issues(tmp_path: Path) -> None:
    """Assert doctor reports missing project hygiene files."""
    try:
        (tmp_path / "module.py").write_text("def useful() -> int:\n    return 1\n", encoding="utf-8")

        report = run_doctor(str(tmp_path))
        codes = {str(item["code"]) for item in report["issues"]}

        assert "missing-readme" in codes
        assert "missing-tests" in codes
        assert report["summary"]["issues"] >= 2
    except RuntimeError as exc:
        raise AssertionError(f"run_doctor failed unexpectedly: {exc}") from exc
