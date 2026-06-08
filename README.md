# PyDevKit
A developer productivity kit for Python projects.

[![MIT License](https://img.shields.io/badge/License-MIT-blueviolet)](https://github.com/owner/repository/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.9+-green)](https://www.python.org/downloads/)
[![Code Style](https://img.shields.io/badge/Code%20Style-black-green)](https://github.com/psf/black)

## Description
PyDevKit is a collection of developer productivity tools for Python projects. It includes features for project inspection, dead code scanning, README generation, and test generation.

## Features

### Analysis
- Project inspection with metrics and risks
- Dead code scanning with removal options
- Run project health checks and return a normalized report

### CLI
- Developer productivity commands
- Generate a README.md file
- Find unused functions, variables, and imports
- Generate pytest tests for public functions
- Inspect project structure, metrics, and risks

### Test Generation
- Extract public functions and metadata from a project
- Generate pytest test files for public functions in a project

## Installation
```bash
pip install pydevkit
```

## CLI Usage Examples

### Inspect Project
```bash
pydevkit inspect --project-path /path/to/project
```

### Dead Code Scan
```bash
pydevkit deadcode --project-path /path/to/project
```

### README Generation
```bash
pydevkit readme --project-path /path/to/project
```

### Test Generation
```bash
pydevkit testgen --project-path /path/to/project
```

## Project Structure
```markdown
pydevkit/
|---- analysis/
|       |---- __init__.py
|       |---- doctor.py
|       |---- inspector.py
|
|---- cli.py
|
|---- deadcode/
|       |---- __init__.py
|       |---- reporter.py
|       |---- scanner.py
|
|---- readme/
|       |---- __init__.py
|       |---- analyzer.py
|       |---- generator.py
|
|---- testgen/
|       |---- __init__.py
|       |---- extractor.py
|       |---- generator.py
|
|---- utils/
|       |---- __init__.py
|       |---- api_client.py
|       |---- config.py
|       |---- file_utils.py
|
|---- sample_project/
|       |---- example.py
|       |---- tests/
|
|---- tests/
|       |---- test_analysis.py
|       |---- test_deadcode.py
|       |---- test_readme.py
|       |---- test_testgen.py
|
|---- setup.py
```

## Configuration
PyDevKit uses a `.pydevkit.toml` file for project configuration. You can find more information about the configuration options in [README.md](README.md).

## Testing
This project uses `pytest` for testing. You can run the tests with the command `pytest`.

## Contributing
Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## License
PyDevKit is licensed under the [MIT License](LICENSE).