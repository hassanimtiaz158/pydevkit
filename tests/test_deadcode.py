"""Tests for dead code scanning."""

from pathlib import Path

from pydevkit.deadcode.scanner import remove_unused_imports, scan_deadcode


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PROJECT = PROJECT_ROOT / "sample_project"


def test_scan_deadcode_detects_unused_sample_symbols() -> None:
    """Assert unused sample functions and imports are reported."""
    try:
        results = scan_deadcode(str(SAMPLE_PROJECT))
        names = {str(item["name"]) for item in results}

        assert "unused_discount" in names
        assert "statistics" in names
    except RuntimeError as exc:
        raise AssertionError(f"scan_deadcode failed unexpectedly: {exc}") from exc


def test_scan_deadcode_does_not_report_used_functions() -> None:
    """Assert functions called elsewhere are not reported as unused."""
    try:
        results = scan_deadcode(str(SAMPLE_PROJECT))
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


def test_scan_deadcode_does_not_report_local_variables(tmp_path: Path) -> None:
    """Assert local variables are not reported as module-level dead code."""
    try:
        module = tmp_path / "module.py"
        module.write_text(
            "def used() -> int:\n"
            "    local_total = 1\n"
            "    return local_total\n"
            "\n"
            "value = used()\n",
            encoding="utf-8",
        )

        results = scan_deadcode(str(tmp_path))
        names = {str(item["name"]) for item in results}

        assert "local_total" not in names
        assert "used" not in names
    except RuntimeError as exc:
        raise AssertionError(f"scan_deadcode failed unexpectedly: {exc}") from exc


def test_remove_unused_imports_removes_only_unused_alias(tmp_path: Path) -> None:
    """Assert import fixing preserves used aliases on the same line."""
    try:
        module = tmp_path / "module.py"
        module.write_text(
            "import os, sys\n"
            "\n"
            "def current_directory() -> str:\n"
            "    return os.getcwd()\n",
            encoding="utf-8",
        )

        results = scan_deadcode(str(tmp_path))
        removed = remove_unused_imports(str(tmp_path), results)

        assert removed == 1
        assert module.read_text(encoding="utf-8").splitlines()[0] == "import os"
    except RuntimeError as exc:
        raise AssertionError(f"remove_unused_imports failed unexpectedly: {exc}") from exc


def test_scan_deadcode_skips_ignored_generated_folders(tmp_path: Path) -> None:
    """Assert generated and ignored folders are skipped by default."""
    try:
        cache_dir = tmp_path / ".venv"
        cache_dir.mkdir()
        (cache_dir / "bad.py").write_text("def unused_cache_func():\n    return 1\n", encoding="utf-8")

        results = scan_deadcode(str(tmp_path))

        assert results == []
    except RuntimeError as exc:
        raise AssertionError(f"scan_deadcode failed unexpectedly: {exc}") from exc


def test_scan_deadcode_respects_min_confidence(tmp_path: Path) -> None:
    """Assert confidence filtering can hide lower-confidence symbols."""
    try:
        module = tmp_path / "module.py"
        module.write_text(
            "import os\n"
            "\n"
            "def maybe_public_api() -> int:\n"
            "    return 1\n",
            encoding="utf-8",
        )

        results = scan_deadcode(str(tmp_path), min_confidence="high")
        names = {str(item["name"]) for item in results}

        assert "os" in names
        assert "maybe_public_api" not in names
    except RuntimeError as exc:
        raise AssertionError(f"scan_deadcode failed unexpectedly: {exc}") from exc


def test_scan_deadcode_respects_config_ignore_files(tmp_path: Path) -> None:
    """Assert configured ignored file globs are not scanned."""
    try:
        (tmp_path / ".pydevkit.toml").write_text(
            "[deadcode]\n"
            'ignore_files = ["generated/*"]\n',
            encoding="utf-8",
        )
        generated = tmp_path / "generated"
        generated.mkdir()
        (generated / "module.py").write_text("def unused_generated() -> int:\n    return 1\n", encoding="utf-8")

        results = scan_deadcode(str(tmp_path))

        assert results == []
    except RuntimeError as exc:
        raise AssertionError(f"scan_deadcode failed unexpectedly: {exc}") from exc


def test_scan_deadcode_treats_dunder_all_as_public_usage(tmp_path: Path) -> None:
    """Assert exported public API symbols are not reported as unused."""
    try:
        module = tmp_path / "module.py"
        module.write_text(
            "__all__ = ['public_api']\n"
            "\n"
            "def public_api() -> int:\n"
            "    return 1\n"
            "\n"
            "def internal_candidate() -> int:\n"
            "    return 2\n",
            encoding="utf-8",
        )

        names = {str(item["name"]) for item in scan_deadcode(str(tmp_path))}

        assert "public_api" not in names
        assert "internal_candidate" in names
    except RuntimeError as exc:
        raise AssertionError(f"scan_deadcode failed unexpectedly: {exc}") from exc


def test_scan_deadcode_treats_incremental_dunder_all_as_public_usage(tmp_path: Path) -> None:
    """Assert simple __all__.append and __all__.extend exports are honored."""
    try:
        module = tmp_path / "module.py"
        module.write_text(
            "__all__ = []\n"
            "__all__.append('first_api')\n"
            "__all__.extend(('second_api',))\n"
            "\n"
            "def first_api() -> int:\n"
            "    return 1\n"
            "\n"
            "def second_api() -> int:\n"
            "    return 2\n",
            encoding="utf-8",
        )

        names = {str(item["name"]) for item in scan_deadcode(str(tmp_path))}

        assert "first_api" not in names
        assert "second_api" not in names
    except RuntimeError as exc:
        raise AssertionError(f"scan_deadcode failed unexpectedly: {exc}") from exc
