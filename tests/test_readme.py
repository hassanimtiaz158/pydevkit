from pathlib import Path

from pydevkit.readme.analyzer import analyze_project
from pydevkit.readme.generator import _compact_ai_context, generate_readme


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


def test_compact_ai_context_limits_large_project_metadata() -> None:
    """Assert AI README prompts stay compact for larger projects."""
    context = {
        "project_name": "demo",
        "functions": [
            {"name": f"function_{index}", "file": "module.py", "docstring": "x" * 500}
            for index in range(40)
        ],
        "classes": [
            {"name": f"Class{index}", "file": "module.py", "docstring": "x" * 500}
            for index in range(30)
        ],
        "python_files": [f"module_{index}.py" for index in range(60)],
        "dependencies": [f"package-{index}" for index in range(30)],
        "console_scripts": [f"cmd-{index}" for index in range(20)],
    }

    compact = _compact_ai_context(context)

    assert len(compact["functions"]) == 25
    assert len(compact["classes"]) == 15
    assert len(compact["python_files"]) == 30
    assert len(compact["dependencies"]) == 12
    assert len(compact["console_scripts"]) == 8
    assert len(compact["functions"][0]["docstring"]) == 160


def test_generate_readme_falls_back_when_ai_prompt_is_too_large(tmp_path: Path, monkeypatch) -> None:
    """Assert token-limit errors fall back to offline README generation."""
    project = tmp_path / "demo"
    project.mkdir()
    (project / "app.py").write_text("def greet() -> str:\n    return 'hello'\n", encoding="utf-8")

    def fail_with_token_limit(*args, **kwargs):
        raise RuntimeError("Groq API request failed: Request too large for model tokens per minute")

    monkeypatch.setattr("pydevkit.readme.generator.call_groq", fail_with_token_limit)

    generate_readme(str(project), use_ai=True)

    readme_path = project / "README.md"
    assert readme_path.exists()
    assert "# demo" in readme_path.read_text(encoding="utf-8")
