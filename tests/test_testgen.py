"""Tests for test generation extraction."""

from pathlib import Path

from pydevkit.testgen.extractor import extract_functions
from pydevkit.testgen.generator import generate_tests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PROJECT = PROJECT_ROOT / "sample_project"


def test_extract_functions_finds_public_sample_functions() -> None:
    """Assert public sample functions are extracted."""
    try:
        functions = extract_functions(str(SAMPLE_PROJECT))
        names = {str(item["name"]) for item in functions}

        assert "add_numbers" in names
        assert "multiply_numbers" in names
        assert "normalize_text" in names
        assert "unused_discount" in names
    except RuntimeError as exc:
        raise AssertionError(f"extract_functions failed unexpectedly: {exc}") from exc


def test_generate_tests_offline_creates_syntax_valid_file(tmp_path: Path) -> None:
    """Assert offline test generation works without a Groq API key."""
    try:
        project = tmp_path / "demo"
        project.mkdir()
        (project / "calculator.py").write_text(
            "def add(left: int, right: int) -> int:\n"
            "    \"\"\"Add two integers.\"\"\"\n"
            "    return left + right\n",
            encoding="utf-8",
        )

        generate_tests(str(project), use_ai=False)

        test_file = project / "tests" / "test_calculator.py"
        content = test_file.read_text(encoding="utf-8")
        assert test_file.exists()
        assert "def test_add_is_callable" in content
        assert "add(" not in content
    except RuntimeError as exc:
        raise AssertionError(f"generate_tests failed unexpectedly: {exc}") from exc


def test_generated_offline_tests_include_project_path(tmp_path: Path) -> None:
    """Assert generated tests can import source modules from custom output dirs."""
    try:
        project = tmp_path / "demo"
        output = tmp_path / "generated"
        project.mkdir()
        (project / "worker.py").write_text(
            "def double(value: int) -> int:\n"
            "    \"\"\"Double an integer.\"\"\"\n"
            "    return value * 2\n",
            encoding="utf-8",
        )

        generate_tests(str(project), output=str(output), use_ai=False)
        content = (output / "test_worker.py").read_text(encoding="utf-8")

        assert "PROJECT_ROOT" in content
        assert "sys.path.insert" in content
        assert repr(str(project.resolve()))[1:-1] in content
    except RuntimeError as exc:
        raise AssertionError(f"generate_tests failed unexpectedly: {exc}") from exc


def test_generated_offline_tests_alias_test_prefixed_imports(tmp_path: Path) -> None:
    """Assert generated imports do not create pytest collection collisions."""
    try:
        project = tmp_path / "demo"
        project.mkdir()
        (project / "commands.py").write_text(
            "def testgen() -> None:\n"
            "    pass\n",
            encoding="utf-8",
        )

        generate_tests(str(project), use_ai=False)
        content = (project / "tests" / "test_commands.py").read_text(encoding="utf-8")

        assert "from commands import testgen as subject_testgen" in content
        assert "assert callable(subject_testgen)" in content
    except RuntimeError as exc:
        raise AssertionError(f"generate_tests failed unexpectedly: {exc}") from exc


def test_extract_functions_captures_args_and_docstrings() -> None:
    """Assert function args, type hints, and docstrings are captured."""
    try:
        functions = extract_functions(str(SAMPLE_PROJECT))
        by_name = {str(item["name"]): item for item in functions}
        add_numbers = by_name["add_numbers"]

        assert add_numbers["args"] == ["left: int", "right: int"]
        assert add_numbers["return_type"] == "int"
        assert add_numbers["docstring"] == "Add two integers and return the total."
    except RuntimeError as exc:
        raise AssertionError(f"extract_functions failed unexpectedly: {exc}") from exc
