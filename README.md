# PyDevKit

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CLI](https://img.shields.io/badge/interface-Click%20CLI-purple)

PyDevKit is a Python CLI toolkit for quickly auditing and documenting Python projects. It can find dead code, generate a project README, and create pytest files with Groq AI.

## Demo

![Demo GIF placeholder](docs/demo.gif)

## Features

- Detect unused public functions, imports, and assigned variables with AST parsing
- Generate a professional README.md with Groq AI
- Generate a basic README.md offline with `--no-ai`
- Generate pytest files for public functions with Groq AI
- Print polished terminal output with Rich
- Install as a local editable CLI package

## Installation

```bash
pip install -e .
```

## Environment Setup

Create a `.env` file or export the variable in your shell:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

The `deadcode` command and `readme --no-ai` work without an API key.

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
File                       Line  Type      Name              Suggestion
sample_project/example.py     4  import    statistics        Remove this unused import
sample_project/example.py     8  variable  UNUSED_CONSTANT   Remove this unused variable
sample_project/example.py    35  function  unused_discount   Remove this unused function
sample_project/example.py    43  function  unused_slugify    Remove this unused function

Found 4 unused symbols in 1 files
```

To remove unused import lines detected by the scanner:

```bash
pydevkit deadcode ./sample_project --fix
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
![License](https://img.shields.io/badge/license-MIT-green)
```

AI mode:

```bash
pydevkit readme ./sample_project
```

### Test Generation

```bash
pydevkit testgen ./sample_project
```

Expected output:

```text
PyDevKit Testgen
Generating tests for sample_project

Generated Tests
File        Functions Found  Tests Generated  Status
example.py                7                8  ok
```

Write generated tests to a custom directory:

```bash
pydevkit testgen ./sample_project --output ./generated_tests
```

## Project Structure

```text
pydevkit/
├── pydevkit/
│   ├── cli.py
│   ├── deadcode/
│   ├── readme/
│   ├── testgen/
│   └── utils/
├── tests/
├── sample_project/
├── setup.py
├── requirements.txt
└── README.md
```

## Development

Run the test suite:

```bash
pytest
```

Try the sample project:

```bash
pydevkit deadcode ./sample_project
pydevkit readme ./sample_project --no-ai
pydevkit testgen ./sample_project
```

## Contributing

Contributions are welcome. Keep changes focused, add tests for behavior changes, and verify the CLI before opening a pull request.

## License

MIT
