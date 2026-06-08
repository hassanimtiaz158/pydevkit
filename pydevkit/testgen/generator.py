"""AI-backed pytest generation."""

import ast
import json
import re
from pathlib import Path
from typing import Dict, List

from rich.table import Table

from pydevkit.testgen.extractor import extract_functions
from pydevkit.utils import console
from pydevkit.utils.api_client import call_groq
from pydevkit.utils.file_utils import write_file


def _strip_code_fences(content: str) -> str:
    """Remove Markdown code fences from generated Python code."""
    try:
        stripped = content.strip()
        fence_match = re.search(r"```(?:python|py)?\s*(.*?)```", stripped, flags=re.DOTALL | re.IGNORECASE)
        if fence_match:
            return fence_match.group(1).strip() + "\n"
        return stripped + "\n"
    except re.error as exc:
        raise RuntimeError(f"Unable to clean generated code: {exc}") from exc


def _module_import_path(source_file: str) -> str:
    """Convert a source file path into an importable module path."""
    try:
        path = Path(source_file)
        without_suffix = path.with_suffix("")
        parts = [part for part in without_suffix.parts if part != "__init__"]
        return ".".join(parts)
    except (ValueError, TypeError) as exc:
        raise RuntimeError(f"Unable to determine import path for {source_file}: {exc}") from exc


def _build_prompt(functions: List[Dict[str, object]], source_file: str) -> str:
    """Build the Groq prompt for one source file."""
    try:
        function_signatures_json = json.dumps(
            {
                "source_file": source_file,
                "import_module": _module_import_path(source_file),
                "functions": functions,
            },
            indent=2,
        )
        return (
            "Generate complete pytest unit tests for these Python functions.\n"
            "Use pytest fixtures where appropriate. Include: happy path tests,\n"
            "edge case tests (None, empty, negative numbers), type error tests.\n"
            "Import the functions correctly. Make tests actually runnable.\n"
            f"Functions: {function_signatures_json}"
        )
    except TypeError as exc:
        raise RuntimeError(f"Unable to build test generation prompt: {exc}") from exc


def _validate_python(code: str) -> bool:
    """Return True when generated code parses as Python."""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def _sample_value(argument: str) -> str:
    """Return a conservative sample value for an annotated argument."""
    try:
        lowered = argument.lower()
        annotation = lowered.split(":", 1)[1].strip() if ":" in lowered else ""
        if "float" in annotation:
            return "1.5"
        if "int" in annotation:
            return "1"
        if "bool" in annotation:
            return "True"
        if "str" in annotation:
            return '"example"'
        if "path" in annotation:
            return 'Path(".")'
        if "tuple" in annotation:
            return "()"
        if "list" in annotation or "sequence" in annotation or "iterable" in annotation:
            return "[]"
        if "dict" in annotation or "mapping" in annotation:
            return "{}"
        if "set" in annotation:
            return "set()"
        if "name" in lowered or "text" in lowered or "value" in lowered:
            return '"example"'
        if "price" in lowered or "amount" in lowered:
            return "1.5"
        return "1"
    except AttributeError:
        return "None"


def _offline_tests_for_file(project_root: Path, source_file: str, functions: List[Dict[str, object]]) -> str:
    """Generate runnable pytest smoke tests without an AI provider."""
    try:
        module_path = _module_import_path(source_file)
        names = [str(function["name"]) for function in functions]
        imports = ", ".join(sorted(names))
        lines = [
            '"""Auto-generated smoke tests by PyDevKit."""',
            "",
            "import sys",
            "from pathlib import Path",
            "",
            f"PROJECT_ROOT = str(Path({str(project_root.resolve())!r}))",
            "if PROJECT_ROOT not in sys.path:",
            "    sys.path.insert(0, PROJECT_ROOT)",
            "",
            f"from {module_path} import {imports}",
            "",
            "",
        ]
        for function in functions:
            name = str(function["name"])
            args = [_sample_value(str(argument)) for argument in function.get("args", [])]
            call = f"{name}({', '.join(args)})"
            lines.extend(
                [
                    f"def test_{name}_is_callable() -> None:",
                    f'    """Assert {name} can be imported."""',
                    "    try:",
                    f"        assert callable({name})",
                    "    except AssertionError:",
                    "        raise",
                    "",
                    "",
                    f"def test_{name}_accepts_sample_inputs() -> None:",
                    f'    """Assert {name} accepts representative sample inputs."""',
                    "    try:",
                    f"        {call}",
                    "    except TypeError as exc:",
                    f'        raise AssertionError("{name} rejected generated sample inputs") from exc',
                    "",
                    "",
                ]
            )
        return "\n".join(lines).rstrip() + "\n"
    except (KeyError, RuntimeError) as exc:
        raise RuntimeError(f"Unable to generate offline tests: {exc}") from exc


def _group_by_file(functions: List[Dict[str, object]]) -> Dict[str, List[Dict[str, object]]]:
    """Group extracted functions by their source file."""
    try:
        grouped: Dict[str, List[Dict[str, object]]] = {}
        for function in functions:
            grouped.setdefault(str(function["file"]), []).append(function)
        return grouped
    except KeyError as exc:
        raise RuntimeError(f"Malformed function metadata: {exc}") from exc


def generate_tests(project_path: str, output: str | None = None, use_ai: bool = True) -> None:
    """Generate pytest test files for public functions in a project."""
    try:
        root = Path(project_path)
        functions = extract_functions(project_path)
        grouped = _group_by_file(functions)

        table = Table(title="Generated Tests")
        table.add_column("File")
        table.add_column("Functions Found", justify="right")
        table.add_column("Tests Generated")
        table.add_column("Status")

        for source_file, file_functions in grouped.items():
            status = "offline"
            if use_ai:
                prompt = _build_prompt(file_functions, source_file)
                try:
                    response = call_groq(
                        prompt=prompt,
                        system="You are an expert Python test engineer. Return only valid pytest code.",
                        max_tokens=4096,
                    )
                    code = _strip_code_fences(response)
                    status = "ai"

                    if not _validate_python(code):
                        strict_prompt = prompt + "\nReturn syntactically valid Python only. Do not include markdown fences."
                        response = call_groq(
                            prompt=strict_prompt,
                            system="Return only syntactically valid pytest code.",
                            max_tokens=4096,
                        )
                        code = _strip_code_fences(response)
                        if not _validate_python(code):
                            status = "syntax invalid"
                            table.add_row(source_file, str(len(file_functions)), "0", status)
                            continue
                except RuntimeError as exc:
                    if "GROQ_API_KEY" not in str(exc):
                        raise
                    code = _offline_tests_for_file(root, source_file, file_functions)
                    status = "offline fallback"
            else:
                code = _offline_tests_for_file(root, source_file, file_functions)

            original_filename = Path(source_file).stem
            if output:
                output_path = Path(output)
                if output_path.suffix == ".py" and len(grouped) == 1:
                    target = output_path
                else:
                    target = output_path / f"test_{original_filename}.py"
            else:
                target = root / "tests" / f"test_{original_filename}.py"
            if not _validate_python(code):
                table.add_row(source_file, str(len(file_functions)), "0", "syntax invalid")
                continue
            write_file(target, code)
            table.add_row(source_file, str(len(file_functions)), str(code.count("def test_")), status)

        if not grouped:
            table.add_row("-", "0", "0", "no functions found")
        console.print(table)
    except (OSError, RuntimeError) as exc:
        raise RuntimeError(f"Test generation failed: {exc}") from exc
