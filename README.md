# PyDevKit

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CLI](https://img.shields.io/badge/CLI-Click-green)
![Tests](https://img.shields.io/badge/Tests-Pytest-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

PyDevKit is a Python developer productivity toolkit that helps you inspect, clean, document, and test Python projects from one simple command-line interface.

It is built for developers who want faster project reviews, better code quality, and less repetitive maintenance work.

## Table of Contents

- [What PyDevKit Does](#what-pydevkit-does)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Quick Start](#quick-start)
- [Command Reference](#command-reference)
- [Configuration](#configuration)
- [Example Workflow](#example-workflow)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## What PyDevKit Does

PyDevKit analyzes Python projects and gives developers useful tools for common tasks:

- Check project health
- Inspect files, functions, classes, imports, syntax errors, and complexity
- Detect unused imports, functions, classes, methods, and variables
- Remove unused imports safely
- Generate starter pytest tests
- Generate project README files
- Support AI-powered README and test generation through the Groq API
- Run in CI with machine-readable JSON output

## Features

### Project Doctor

Runs health checks and reports project issues such as:

- Missing `README.md`
- Missing license file
- Missing test folder
- Missing `.env.example`
- Syntax errors
- Missing runtime imports
- Possibly unused dependencies
- Long or complex functions
- Dead code

### Project Inspector

Scans the project and reports:

- Number of Python files
- Functions and classes
- Imports
- Dead code count
- Syntax error count
- Total source lines
- Function metrics
- Import edges
- Local project modules

### Dead Code Scanner

Finds unused:

- Imports
- Public functions
- Public classes
- Public methods
- Module-level variables

It can also remove unused import aliases with `--fix`.

### Test Generator

Generates pytest files for public functions.

It supports:

- AI-backed test generation with Groq
- Offline smoke-test generation
- Custom output directory
- Project config defaults

### README Generator

Generates a README for any Python project.

It supports:

- AI-powered README generation with Groq
- Offline README generation with `--no-ai`
- Automatic project metadata discovery
- Function, class, dependency, and entry point detection

## Tech Stack

PyDevKit uses:

- **Python 3.10+** for the core package
- **Click** for the command-line interface
- **Rich** for clean terminal tables and panels
- **Pytest** for tests
- **Groq API** for optional AI-powered README and test generation
- **python-dotenv** for loading environment variables
- **setuptools** for packaging
- **TOML configuration** through `.pydevkit.toml`

## Project Structure

```text
pydevkit/
├── pydevkit/
│   ├── analysis/
│   │   ├── doctor.py
│   │   └── inspector.py
│   ├── deadcode/
│   │   ├── reporter.py
│   │   └── scanner.py
│   ├── readme/
│   │   ├── analyzer.py
│   │   └── generator.py
│   ├── testgen/
│   │   ├── extractor.py
│   │   └── generator.py
│   ├── utils/
│   │   ├── api_client.py
│   │   ├── config.py
│   │   └── file_utils.py
│   ├── __init__.py
│   └── cli.py
├── sample_project/
│   ├── example.py
│   └── tests/
│       └── test_example.py
├── tests/
│   ├── test_analysis.py
│   ├── test_deadcode.py
│   ├── test_readme.py
│   └── test_testgen.py
├── .env.example
├── .gitignore
├── .pydevkit.toml
├── README.md
├── requirements.txt
└── setup.py
```

## Installation

### 1. Clone the project

```bash
git clone <your-repository-url>
cd pydevkit
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install PyDevKit locally

```bash
pip install -e .
```

After installation, the `pydevkit` command will be available in your terminal.

## Environment Setup

PyDevKit can run without AI if you use offline options such as `--no-ai` and `--offline`.

For AI-powered README and test generation, create a `.env` file:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

You can copy the example file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Important: never commit your real `.env` file or API key.

## Quick Start

Run these commands from the root of a Python project:

```bash
pydevkit inspect .
pydevkit doctor .
pydevkit deadcode .
pydevkit testgen . --offline
pydevkit readme . --no-ai
```

## Command Reference

## `pydevkit inspect`

Inspect project structure, metrics, imports, dead code, and syntax errors.

```bash
pydevkit inspect .
```

Use JSON output:

```bash
pydevkit inspect . --json
```

Use this command when you want a high-level technical overview of a project.

### Output includes

- Python file count
- Function count
- Class count
- Import count
- Dead code count
- Syntax error count
- Total lines
- Test folder status

## `pydevkit doctor`

Run project health checks.

```bash
pydevkit doctor .
```

Use JSON output:

```bash
pydevkit doctor . --json
```

Use CI mode:

```bash
pydevkit doctor . --ci
```

`--ci` exits with a non-zero status if high or medium issues are found.

Use this command before submitting, deploying, or pushing a project.

### Checks include

- README file
- License file
- Tests folder
- `.env.example`
- Syntax errors
- Missing imports
- Unused dependencies
- Function complexity
- Dead code

## `pydevkit deadcode`

Scan for unused code.

```bash
pydevkit deadcode .
```

Include tests in the scan:

```bash
pydevkit deadcode . --include-tests
```

Show JSON output:

```bash
pydevkit deadcode . --json
```

Fail in CI if dead code is found:

```bash
pydevkit deadcode . --ci
```

Preview unused import cleanup:

```bash
pydevkit deadcode . --fix --dry-run
```

Remove unused import aliases:

```bash
pydevkit deadcode . --fix
```

Use this command when you want to clean up unused imports, functions, variables, classes, or methods.

## `pydevkit testgen`

Generate pytest tests for public functions.

Generate tests with AI:

```bash
pydevkit testgen .
```

Generate offline smoke tests:

```bash
pydevkit testgen . --offline
```

Generate tests into a custom directory:

```bash
pydevkit testgen . --offline --output generated_tests
```

Generate one output file when scanning one source file:

```bash
pydevkit testgen sample_project/example.py --offline --output tests/test_example_generated.py
```

Use this command when you want a quick starting point for pytest coverage.

## `pydevkit readme`

Generate a README file for a Python project.

Generate with AI:

```bash
pydevkit readme .
```

Generate without AI:

```bash
pydevkit readme . --no-ai
```

Use this command when you need project documentation quickly.

## Configuration

PyDevKit reads optional configuration from `.pydevkit.toml`.

Current example:

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

### Deadcode config

| Option | Purpose |
| --- | --- |
| `ignore_names` | Symbol names that should not be reported |
| `ignore_files` | File patterns to skip |
| `include_tests` | Whether test files should be scanned |
| `min_confidence` | Minimum result confidence: `low`, `medium`, or `high` |

### Testgen config

| Option | Purpose |
| --- | --- |
| `offline` | Generate tests without AI by default |
| `output` | Default output file or directory |

### Doctor config

| Option | Purpose |
| --- | --- |
| `max_function_lines` | Warn when a function is too long |
| `max_function_args` | Warn when a function has too many arguments |
| `max_branches` | Warn when a function has too much branching |

## Example Workflow

Here is a practical workflow for reviewing a project:

### 1. Inspect the project

```bash
pydevkit inspect .
```

This gives you a quick summary of the codebase.

### 2. Run health checks

```bash
pydevkit doctor .
```

This shows missing files, syntax problems, missing imports, and quality issues.

### 3. Find unused code

```bash
pydevkit deadcode .
```

Review the report before deleting anything.

### 4. Remove unused imports safely

```bash
pydevkit deadcode . --fix --dry-run
pydevkit deadcode . --fix
```

Always run `--dry-run` first if you want to preview cleanup.

### 5. Generate tests

```bash
pydevkit testgen . --offline
```

This creates starter pytest tests for public functions.

### 6. Generate documentation

```bash
pydevkit readme . --no-ai
```

This creates a README based on project metadata.

### 7. Run tests

```bash
pytest -q
```

## Testing

Run all tests:

```bash
pytest -q
```

Run one test file:

```bash
pytest tests/test_deadcode.py -q
```

Run the sample project tests:

```bash
pytest sample_project/tests -q
```

## Requirements

The project dependencies are:

```text
click>=8.1.0
groq>=0.9.0
rich>=13.0.0
pytest>=7.0.0
python-dotenv>=1.0.0
```

## Troubleshooting

### `pydevkit` command is not found

Make sure the package is installed locally:

```bash
pip install -e .
```

Also confirm your virtual environment is activated.

### `GROQ_API_KEY is missing`

You are using an AI-powered command without a configured Groq API key.

Either add a `.env` file:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

Or use offline mode:

```bash
pydevkit readme . --no-ai
pydevkit testgen . --offline
```

### Tests cannot import local modules

Install the project in editable mode:

```bash
pip install -e .
```

Then run tests again:

```bash
pytest -q
```

### Deadcode reports something that should stay

Add it to `.pydevkit.toml`:

```toml
[deadcode]
ignore_names = ["main", "my_public_api"]
```

### Generated tests are too basic

Offline tests are intentionally conservative. For richer tests, set `GROQ_API_KEY` and run:

```bash
pydevkit testgen .
```

## Best Practices

- Run `pydevkit doctor .` before submitting a project.
- Use `pydevkit deadcode . --fix --dry-run` before applying automatic cleanup.
- Keep `.env` private and commit only `.env.example`.
- Review generated tests before treating them as final coverage.
- Use `.pydevkit.toml` to customize rules for each project.

## Contributing

Contributions are welcome.

Suggested contribution workflow:

```bash
git checkout -b feature/my-improvement
pip install -e .
pytest -q
```

Then open a pull request with:

- A clear description of the change
- Any new tests
- Screenshots or terminal output if the CLI output changes

## License

PyDevKit is released under the MIT License.

## Short Summary

PyDevKit helps Python developers move faster by combining project inspection, health checks, dead code detection, README generation, and pytest generation in one clean CLI.
