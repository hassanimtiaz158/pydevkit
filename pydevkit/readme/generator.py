"""README generation for PyDevKit."""

import json
from pathlib import Path
from typing import Dict

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

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
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


def generate_readme(project_path: str, use_ai: bool = True) -> None:
    """Generate README.md for a project."""
    try:
        context = analyze_project(project_path)
        if use_ai:
            context_json = json.dumps(context, indent=2)
            prompt = (
                "Generate a professional GitHub README.md for this Python project.\n"
                "Include: title, badges (Python version, license), description,\n"
                "features list, installation (pip install -e .), usage examples\n"
                "with code blocks, project structure, contributing guide, license.\n"
                f"Project info: {context_json}"
            )
            content = call_groq(
                prompt=prompt,
                system="You are an expert technical writer. Return only README markdown.",
            )
        else:
            content = _basic_template(context)

        output_path = Path(project_path) / "README.md"
        write_file(output_path, content)
        preview = "\n".join(content.splitlines()[:5])
        console.print(Panel(preview, title=f"README.md created at {output_path}", style="green"))
    except (OSError, RuntimeError) as exc:
        raise RuntimeError(f"README generation failed: {exc}") from exc
