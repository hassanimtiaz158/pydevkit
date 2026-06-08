# PyDevKit

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CLI](https://img.shields.io/badge/interface-Click%20CLI-purple)

PyDevKit is a Python CLI toolkit for auditing, documenting, and test-bootstrapping Python projects. It finds dead code, generates README files, and creates pytest files with Groq AI or a conservative offline fallback.

## Demo

![PyDevKit demo animation](docs/demo.gif)

## Features

- Detect unused public functions, imports, classes, methods, and module variables with AST parsing
- Skip generated folders, virtual environments, caches, and ignored paths
- Safely remove unused import aliases with `--fix`
- Preview fixes with `--dry-run`
- Emit JSON for CI and automation with `--json`
- Fail CI when issues are found with `--ci`
- Generate a professional README.md with Groq AI
- Generate a basic README.md offline with `--no-ai`
- Generate pytest files with Groq AI or `--offline`
- Inspect project metrics with `inspect`
- Run project health checks with `doctor`
- Tune behavior with `.pydevkit.toml`
- Print polished terminal output with Rich

## Installation

```bash
pip install -e .
```

## Environment Setup

Create a `.env` file or export the variable in your shell:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

The `deadcode`, `readme --no-ai`, and `testgen --offline` flows work without an API key.

## Commands

### Help

```bash
pydevkit --help
```

Expected output:

```text
Usage: pydevkit [OPTIONS] COMMAND [ARGS]...

  PyDevKit developer productivity commands.

Commands:
  deadcode  Find unused functions, variables, and imports.
  doctor    Run project health checks.
  inspect   Inspect project structure, metrics, and risks.
  readme    Generate a README.md file.
  testgen   Generate pytest tests for public functions.
```

### Dead Code Scan

```bash
pydevkit deadcode ./sample_project
```

Expected output:

```text
PyDevKit Deadcode
Scanning dead code in sample_project

Dead Code Report
File                       Line  Type      Name              Severity  Suggestion
sample_project/example.py     4  import    statistics        high      Remove this unused import
sample_project/example.py     8  variable  UNUSED_CONSTANT   medium    Remove this unused variable
sample_project/example.py    35  function  unused_discount   medium    Remove this unused function
sample_project/example.py    43  function  unused_slugify    medium    Remove this unused function

Found 4 unused symbols in 1 files
```

Preview import fixes:

```bash
pydevkit deadcode ./sample_project --fix --dry-run
```

Apply import fixes:

```bash
pydevkit deadcode ./sample_project --fix
```

Automation-friendly output:

```bash
pydevkit deadcode ./sample_project --json
pydevkit deadcode ./sample_project --ci
```

Include test files in the scan:

```bash
pydevkit deadcode ./sample_project --include-tests
```

### Project Inspection

```bash
pydevkit inspect ./sample_project
```

Expected output:

```text
PyDevKit Inspect
Inspecting sample_project

Project Summary
Metric         Value
Python Files      1
Functions         6
Classes           0
Deadcode          4
Syntax Errors     0
```

Machine-readable output:

```bash
pydevkit inspect ./sample_project --json
```

### Doctor Checks

```bash
pydevkit doctor ./sample_project
```

Doctor checks for missing README/license/tests/env examples, syntax errors, unresolved imports, possible unused dependencies, complexity issues, and dead code.

CI mode:

```bash
pydevkit doctor ./sample_project --ci
```

### README Generation

Offline mode:

```bash
pydevkit readme ./sample_project --no-ai
```

Expected output:

```text
PyDevKit README
Generating README for sample_project

README.md created at sample_project/README.md
# sample_project
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
```

AI mode:

```bash
pydevkit readme ./sample_project
```

### Test Generation

AI mode:

```bash
pydevkit testgen ./sample_project
```

Offline mode:

```bash
pydevkit testgen ./sample_project --offline
```

Expected output:

```text
PyDevKit Testgen
Generating tests for sample_project

Generated Tests
File        Functions Found  Tests Generated  Status
example.py                6               12  offline
```

Write generated tests to a custom directory:

```bash
pydevkit testgen ./sample_project --output ./generated_tests
```

## Project Structure

```text
pydevkit/
|-- pydevkit/
|   |-- cli.py
|   |-- deadcode/
|   |-- readme/
|   |-- testgen/
|   `-- utils/
|-- tests/
|-- sample_project/
|-- setup.py
|-- requirements.txt
|-- .pydevkit.toml
`-- README.md
```

## Configuration

PyDevKit reads `.pydevkit.toml` from the project root:

```toml
[deadcode]
ignore_names = ["main"]
ignore_files = ["migrations/*"]
include_tests = false
min_confidence = "low"

[testgen]
offline = false
output = ""

[doctor]
max_function_lines = 80
max_function_args = 6
max_branches = 12
```

## Development

Run the test suite:

```bash
pytest
```

Try the sample project:

```bash
pydevkit deadcode ./sample_project
pydevkit inspect ./sample_project
pydevkit doctor ./sample_project
pydevkit readme ./sample_project --no-ai
pydevkit testgen ./sample_project --offline
```

## Contributing

Contributions are welcome. Keep changes focused, add tests for behavior changes, and verify the CLI before opening a pull request.

## License

MIT
