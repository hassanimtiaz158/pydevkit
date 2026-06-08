"""README generation for PyDevKit."""

import json
from pathlib import Path
from typing import Dict, List

from rich.panel import Panel

from pydevkit.readme.analyzer import analyze_project
from pydevkit.utils import console
from pydevkit.utils.api_client import call_groq
from pydevkit.utils.file_utils import write_file


def _basic_template(context: Dict[str, object]) -> str:
    """Render a basic README without external AI calls."""
    try:
        project_name = str(context.get("package_name") or context["project_name"])
        version = str(context.get("version") or "0.1.0")
        license_name = str(context.get("license") or "MIT")
        console_scripts = context.get("console_scripts", [])
        dependencies = context.get("dependencies", [])
        functions = context.get("functions", [])
        classes = context.get("classes", [])
        python_files = context.get("python_files", [])
        entry_point = context.get("entry_point") or "No obvious entry point detected"

        dependency_text = "\n".join(f"- `{item}`" for item in dependencies) if dependencies else "- None detected"
        command_text = "\n".join(f"- `{item}`" for item in console_scripts) if console_scripts else "- No console scripts detected"
        function_text = "\n".join(
            f"- `{item['name']}` in `{item['file']}`: {item['docstring'] or 'No docstring'}"
            for item in functions
        ) or "- No public functions detected"
        class_text = "\n".join(
            f"- `{item['name']}` in `{item['file']}`: {item['docstring'] or 'No docstring'}"
            for item in classes
        ) or "- No public classes detected"
        structure_text = "\n".join(f"- `{item}`" for item in python_files) or "- No Python files detected"

        return f"""# {project_name}

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Version](https://img.shields.io/badge/version-{version}-blue)
![License](https://img.shields.io/badge/license-{license_name}-green)

## Description

{project_name} is a Python project analyzed by PyDevKit.

## Features

- Automatic project metadata discovery
- Public function and class inventory
- Dependency and entry point detection

## Installation

```bash
pip install -e .
```

## Usage

```bash
python {entry_point}
```

## CLI Commands

{command_text}

## Project Structure

{structure_text}

## Public Functions

{function_text}

## Public Classes

{class_text}

## Dependencies

{dependency_text}

## Contributing

Contributions are welcome. Create a branch, add focused tests, and open a pull request.

## License

MIT
"""
    except (KeyError, TypeError) as exc:
        raise RuntimeError(f"Unable to render README template: {exc}") from exc


def _limit_items(items: object, limit: int) -> List[object]:
    """Return a bounded list for compact AI prompts."""
    if not isinstance(items, list):
        return []
    return items[:limit]


def _compact_ai_context(context: Dict[str, object]) -> Dict[str, object]:
    """Build a small project summary that stays under low TPM limits."""
    return {
        "project_name": context.get("project_name"),
        "package_name": context.get("package_name"),
        "version": context.get("version"),
        "license": context.get("license"),
        "entry_point": context.get("entry_point"),
        "has_tests": context.get("has_tests"),
        "console_scripts": _limit_items(context.get("console_scripts"), 8),
        "dependencies": _limit_items(context.get("dependencies"), 12),
        "python_files": _limit_items(context.get("python_files"), 30),
        "functions": [
            {
                "name": item.get("name"),
                "file": item.get("file"),
                "docstring": str(item.get("docstring", ""))[:160],
            }
            for item in _limit_items(context.get("functions"), 25)
            if isinstance(item, dict)
        ],
        "classes": [
            {
                "name": item.get("name"),
                "file": item.get("file"),
                "docstring": str(item.get("docstring", ""))[:160],
            }
            for item in _limit_items(context.get("classes"), 15)
            if isinstance(item, dict)
        ],
    }


def generate_readme(project_path: str, use_ai: bool = True) -> None:
    """Generate README.md for a project."""
    try:
        context = analyze_project(project_path)
        if use_ai:
            context_json = json.dumps(_compact_ai_context(context), separators=(",", ":"))
            prompt = (
                "Generate a professional GitHub README.md for this Python project.\n"
                "Keep it concise but complete. Include: title, badges, description,\n"
                "features, installation, CLI usage examples, project structure,\n"
                "configuration, testing, contributing, and license.\n"
                f"Project info: {context_json}"
            )
            try:
                content = call_groq(
                    prompt=prompt,
                    system="You are an expert technical writer. Return only README markdown.",
                    max_tokens=1200,
                )
            except RuntimeError as exc:
                if "Request too large" not in str(exc) and "tokens per minute" not in str(exc):
                    raise
                console.print("[yellow]Groq token limit reached; generating README offline instead.[/yellow]")
                content = _basic_template(context)
        else:
            content = _basic_template(context)

        output_path = Path(project_path) / "README.md"
        write_file(output_path, content)
        preview = "\n".join(content.splitlines()[:5])
        console.print(Panel(preview, title=f"README.md created at {output_path}", style="green"))
    except (OSError, RuntimeError) as exc:
        raise RuntimeError(f"README generation failed: {exc}") from exc
