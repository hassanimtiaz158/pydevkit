from pathlib import Path

from pydevkit.readme.analyzer import analyze_project
from pydevkit.readme.generator import generate_readme


def test_analyze_project_returns_expected_structure() -> None:
    
    try:
        result = analyze_project("sample_project")

        assert result["project_name"] == "sample_project"
        assert "example.py" in result["python_files"]
        assert "package_name" in result
        assert "version" in result
        assert isinstance(result["functions"], list)
        assert isinstance(result["classes"], list)
        assert isinstance(result["dependencies"], list)
        assert result["has_tests"] is False
        assert "entry_point" in result
    except RuntimeError as exc:
        raise AssertionError(f"analyze_project failed unexpectedly: {exc}") from exc


def test_generate_readme_without_ai_creates_file(tmp_path: Path) -> None:
    
    try:
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
    except RuntimeError as exc:
        raise AssertionError(f"generate_readme failed unexpectedly: {exc}") from exc
