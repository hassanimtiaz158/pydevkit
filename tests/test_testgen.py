"""Tests for test generation extraction."""

from pydevkit.testgen.extractor import extract_functions


def test_extract_functions_finds_public_sample_functions() -> None:
    """Assert public sample functions are extracted."""
    try:
        functions = extract_functions("sample_project")
        names = {str(item["name"]) for item in functions}

        assert "add_numbers" in names
        assert "multiply_numbers" in names
        assert "normalize_text" in names
        assert "unused_discount" in names
    except RuntimeError as exc:
        raise AssertionError(f"extract_functions failed unexpectedly: {exc}") from exc


def test_extract_functions_captures_args_and_docstrings() -> None:
    """Assert function args, type hints, and docstrings are captured."""
    try:
        functions = extract_functions("sample_project")
        by_name = {str(item["name"]): item for item in functions}
        add_numbers = by_name["add_numbers"]

        assert add_numbers["args"] == ["left: int", "right: int"]
        assert add_numbers["return_type"] == "int"
        assert add_numbers["docstring"] == "Add two integers and return the total."
    except RuntimeError as exc:
        raise AssertionError(f"extract_functions failed unexpectedly: {exc}") from exc
