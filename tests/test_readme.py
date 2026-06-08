from pathlib import Path

from pydevkit.readme.analyzer import analyze_project
from pydevkit.readme.generator import generate_readme


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PROJECT = PROJECT_ROOT / "sample_project"


def test_analyze_project_returns_expected_structure() -> None:
    """Assert project analysis returns README-ready metadata."""
    result = analyze_project(str(SAMPLE_PROJECT))

    assert result["project_name"] == "sample_project"
    assert "example.py" in result["python_files"]
    assert "package_name" in result
    assert "version" in result
    assert isinstance(result["functions"], list)
    assert isinstance(result["classes"], list)
    assert isinstance(result["dependencies"], list)
    assert result["has_tests"] is True
    assert "entry_point" in result


def test_generate_readme_without_ai_creates_file(tmp_path: Path) -> None:
    """Assert offline README generation writes markdown to disk."""
    project = tmp_path / "demo"
    project.mkdir()
    (project / "app.py").write_text(
        'def greet(name: str) -> str:\n    """Greet a user."""\n    return f"Hello {name}"\n',
        encoding="utf-8",
    )

    generate_readme(str(project), use_ai=False)

    readme_path = project / "README.md"
    assert readme_path.exists()
    assert "# demo" in readme_path.read_text(encoding="utf-8")
