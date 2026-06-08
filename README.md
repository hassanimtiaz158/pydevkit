# PyDevKit

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CLI](https://img.shields.io/badge/CLI-Click-green)
![Tests](https://img.shields.io/badge/Tests-Pytest-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

PyDevKit is a beginner-friendly command-line toolkit for Python developers.

It helps you check a Python project, find unused code, generate starter tests, and create README files without manually inspecting every file yourself.

## Why Use PyDevKit?

When you work on a Python project, you often need to answer questions like:

- Does this project have tests?
- Are there syntax errors?
- Are there unused imports or functions?
- What files, functions, and classes are inside the project?
- Can I quickly generate starter pytest tests?
- Can I quickly generate a README file?

PyDevKit gives you commands for all of these tasks.

## Features

- Inspect project structure and metrics
- Run project health checks
- Find unused imports, variables, functions, classes, and methods
- Remove unused import aliases safely
- Generate pytest smoke tests for public functions
- Generate README files with or without AI
- Use `.pydevkit.toml` for project-specific settings
- Support JSON output for automation and CI

## Requirements

- Python 3.10 or newer
- pip
- A terminal such as PowerShell, Command Prompt, Terminal, or Bash

## Installation

### 1. Clone the project

```bash
git clone https://github.com/hassanimtiaz158/pydevkit.git
cd pydevkit
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
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

### 5. Check that it works

```bash
pydevkit --help
```

You should see commands such as `inspect`, `doctor`, `deadcode`, `testgen`, and `readme`.

## Environment Variables

PyDevKit can run without AI. Use `--offline` for test generation and `--no-ai` for README generation.

If you want AI-powered README or test generation, set a Groq API key.

Copy the example file:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Important: do not commit your real `.env` file. It is already ignored by `.gitignore`.

## Quick Start

Run these commands from the root of any Python project:

```bash
pydevkit inspect .
pydevkit doctor .
pydevkit deadcode .
pydevkit testgen . --offline
pydevkit readme . --no-ai
```

The `.` means "use the current folder".

You can also pass another path:

```bash
pydevkit inspect sample_project
pydevkit doctor sample_project
```

## Commands Explained

## `pydevkit inspect`

Use this command when you want a quick overview of a project.

```bash
pydevkit inspect .
```

What it checks:

- Number of Python files
- Number of functions and classes
- Imports used in the project
- Syntax errors
- Total lines of code
- Dead-code count
- Whether a `tests/` folder exists

JSON output:

```bash
pydevkit inspect . --json
```

JSON output is useful for scripts, CI tools, and automated checks.

## `pydevkit doctor`

Use this command when you want a health report for a project.

```bash
pydevkit doctor .
```

What it checks:

- Missing `README.md`
- Missing license file
- Missing tests folder
- Missing `.env.example`
- Syntax errors
- Imports that cannot be resolved
- Possibly unused dependencies
- Long or complex functions
- Dead code

JSON output:

```bash
pydevkit doctor . --json
```

CI mode:

```bash
pydevkit doctor . --ci
```

`--ci` exits with an error code if high or medium severity issues are found.

## `pydevkit deadcode`

Use this command when you want to find unused code.

```bash
pydevkit deadcode .
```

It can detect unused:

- Imports
- Variables
- Functions
- Classes
- Methods

Include test files in the scan:

```bash
pydevkit deadcode . --include-tests
```

Get JSON output:

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

Actually remove unused import aliases:

```bash
pydevkit deadcode . --fix
```

Tip: run `--dry-run` first before using `--fix`.

## `pydevkit testgen`

Use this command when you want to generate starter pytest tests.

Generate tests without AI:

```bash
pydevkit testgen . --offline
```

Generate tests into a custom folder:

```bash
pydevkit testgen . --offline --output generated_tests
```

Generate tests for one Python file:

```bash
pydevkit testgen sample_project/example.py --offline --output tests/test_example_generated.py
```

Generate AI-assisted tests with Groq:

```bash
pydevkit testgen .
```

AI mode requires `GROQ_API_KEY` in `.env`.

Note: generated tests are starter smoke tests. Review them before treating them as full test coverage.

## `pydevkit readme`

Use this command when you want to generate a README file for a project.

Generate without AI:

```bash
pydevkit readme . --no-ai
```

Generate with Groq AI:

```bash
pydevkit readme .
```

AI mode requires `GROQ_API_KEY` in `.env`.

Important: this command overwrites the target project's `README.md`.

## Configuration

PyDevKit reads optional settings from `.pydevkit.toml`.

Example:

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

### Deadcode Settings

| Setting | Meaning |
| --- | --- |
| `ignore_names` | Names that should not be reported as dead code |
| `ignore_files` | File patterns to skip |
| `include_tests` | Whether to scan test files |
| `min_confidence` | Minimum confidence level: `low`, `medium`, or `high` |

### Testgen Settings

| Setting | Meaning |
| --- | --- |
| `offline` | Generate tests without AI by default |
| `output` | Default output file or folder |

### Doctor Settings

| Setting | Meaning |
| --- | --- |
| `max_function_lines` | Warn if a function is too long |
| `max_function_args` | Warn if a function has too many arguments |
| `max_branches` | Warn if a function has too many branches |

## Example Workflow

A simple workflow for checking a project:

```bash
pydevkit inspect .
pydevkit doctor .
pydevkit deadcode .
pytest -q
```

If you want to generate starter tests:

```bash
pydevkit testgen . --offline
pytest -q
```

If you want to generate a README:

```bash
pydevkit readme . --no-ai
```

## Testing This Repository

Run all tests:

```bash
pytest -q
```

Run tests with warnings treated as errors:

```bash
pytest -q -W error
```

Run one test file:

```bash
pytest tests/test_deadcode.py -q
```

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
│   └── cli.py
├── sample_project/
│   ├── example.py
│   └── tests/
├── tests/
├── .env.example
├── .pydevkit.toml
├── pytest.ini
├── requirements.txt
├── setup.py
└── README.md
```

## Troubleshooting

### `pydevkit` is not recognized

Run:

```bash
pip install -e .
```

Also make sure your virtual environment is activated.

### `GROQ_API_KEY is missing`

Use offline commands:

```bash
pydevkit readme . --no-ai
pydevkit testgen . --offline
```

Or add your Groq key to `.env`.

### Groq says the request is too large

PyDevKit tries to keep AI prompts compact. If Groq still rate-limits the request, use:

```bash
pydevkit readme . --no-ai
pydevkit testgen . --offline
```

### Pytest has a Windows temp permission error

This project uses a local pytest temp folder through `pytest.ini`:

```ini
addopts =
    --basetemp=.pytest_tmp
```

Close other Python/pytest processes and run:

```bash
pytest -q
```

## Contributing

Contributions are welcome.

Suggested workflow:

```bash
git checkout -b feature/my-change
pip install -r requirements.txt
pip install -e .
pytest -q
```

Then open a pull request with:

- A clear explanation of the change
- Tests for new behavior
- Notes about any CLI output changes

## License

PyDevKit is released under the MIT License. See [LICENSE](LICENSE).
