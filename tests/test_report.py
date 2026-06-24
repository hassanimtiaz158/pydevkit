"""Tests for HTML report generation."""

from pathlib import Path

from pydevkit.report.generator import generate_html_report, generate_report

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PROJECT = PROJECT_ROOT / "sample_project"


def test_generate_html_report_contains_project_name() -> None:
    """Assert the rendered HTML includes the project name."""
    html = generate_html_report(
        project_name="my_project",
        inspection={
            "summary": {
                "python_files": 3, "functions": 5, "classes": 1,
                "imports": 10, "deadcode": 2, "syntax_errors": 0,
                "total_lines": 150, "has_tests": True,
            },
            "syntax_errors": [],
        },
        doctor_report={
            "summary": {"issues": 1, "high": 0, "medium": 1, "low": 0},
            "issues": [
                {"code": "missing-license", "severity": "low",
                 "message": "License file is missing.", "suggestion": "Add a LICENSE file."},
            ],
        },
        deadcode_results=[
            {"file": "module.py", "line": 10, "type": "function",
             "name": "unused_func", "suggestion": "Remove this unused function",
             "severity": "medium", "confidence": "medium"},
        ],
        functions=[
            {"name": "add", "args": ["x: int", "y: int"], "return_type": "int",
             "docstring": "Add two numbers.", "file": "module.py", "line": 1},
        ],
        classes=[
            {"name": "Calculator", "docstring": "A calculator.", "file": "calc.py", "line": 1},
        ],
        dependencies=["click>=8.0", "rich>=13.0"],
        python_files=["module.py", "calc.py", "tests/test_module.py"],
        entry_point="module.py",
    )

    assert "my_project" in html
    assert "missing-license" in html
    assert "unused_func" in html
    assert "Calculator" in html
    assert "click&gt;=8.0" in html
    assert "module.py" in html


def test_generate_html_report_escapes_html_entities() -> None:
    """Assert special characters are escaped in the report."""
    html = generate_html_report(
        project_name="<script>alert('xss')</script>",
        inspection={
            "summary": {
                "python_files": 0, "functions": 0, "classes": 0,
                "imports": 0, "deadcode": 0, "syntax_errors": 0,
                "total_lines": 0, "has_tests": False,
            },
            "syntax_errors": [],
        },
        doctor_report={"summary": {"issues": 0, "high": 0, "medium": 0, "low": 0}, "issues": []},
        deadcode_results=[],
        functions=[],
        classes=[],
        dependencies=[],
        python_files=[],
        entry_point=None,
    )

    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_generate_report_writes_file_to_disk(tmp_path: Path) -> None:
    """Assert generate_report writes an HTML file to the specified path."""
    (tmp_path / "app.py").write_text(
        "def greet(name: str) -> str:\n    return f'Hello {name}'\n",
        encoding="utf-8",
    )

    output = tmp_path / "report.html"
    generate_report(str(tmp_path), output=str(output))

    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "greet" in content


def test_generate_report_defaults_to_project_dir(tmp_path: Path) -> None:
    """Assert generate_report writes to pydevkit-report.html by default."""
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")

    generate_report(str(tmp_path))

    expected = tmp_path / "pydevkit-report.html"
    assert expected.exists()


def test_generate_report_against_sample_project() -> None:
    """Assert generate_report works against the real sample_project fixture."""
    output = SAMPLE_PROJECT / "test-report-output.html"
    generate_report(str(SAMPLE_PROJECT), output=str(output))

    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "sample_project" in content
    assert "unused_discount" in content

    # Clean up
    output.unlink()
