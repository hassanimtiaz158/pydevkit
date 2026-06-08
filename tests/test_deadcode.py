"""Tests for dead code scanning."""

from pathlib import Path

from pydevkit.deadcode.scanner import scan_deadcode


def test_scan_deadcode_detects_unused_sample_symbols() -> None:
    """Assert unused sample functions and imports are reported."""
    try:
        results = scan_deadcode("sample_project")
        names = {str(item["name"]) for item in results}

        assert "unused_discount" in names
        assert "statistics" in names
    except RuntimeError as exc:
        raise AssertionError(f"scan_deadcode failed unexpectedly: {exc}") from exc


def test_scan_deadcode_does_not_report_used_functions() -> None:
    """Assert functions called elsewhere are not reported as unused."""
    try:
        results = scan_deadcode("sample_project")
        names = {str(item["name"]) for item in results}

        assert "add_numbers" not in names
        assert "multiply_numbers" not in names
        assert "normalize_text" not in names
    except RuntimeError as exc:
        raise AssertionError(f"scan_deadcode failed unexpectedly: {exc}") from exc


def test_scan_deadcode_empty_folder(tmp_path: Path) -> None:
    """Assert an empty folder returns no results."""
    try:
        results = scan_deadcode(str(tmp_path))
        assert results == []
    except RuntimeError as exc:
        raise AssertionError(f"scan_deadcode failed unexpectedly: {exc}") from exc


def test_scan_deadcode_folder_with_no_python_files(tmp_path: Path) -> None:
    """Assert a folder without Python files returns no results."""
    try:
        (tmp_path / "notes.txt").write_text("hello", encoding="utf-8")
        results = scan_deadcode(str(tmp_path))
        assert results == []
    except RuntimeError as exc:
        raise AssertionError(f"scan_deadcode failed unexpectedly: {exc}") from exc
