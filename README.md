# [![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](https://choosealicense.com/licenses/mit/)
# [![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)

# PyDevKit
================

PyDevKit is a developer productivity toolkit designed to automate tasks, improve code quality, and increase collaboration.

### Features

* Run project health checks and generate reports
* Inspect project structure, metrics, and risks
* Find unused functions, variables, and imports
* Generate pytest tests for public functions
* Create README.md files for projects
* Normalize and standardize code

### Installation

```bash
pip install -e .
```

### Usage

#### Run Project Health Checks
```bash
pydevkit doctor
```

#### Inspect Project Structure and Metrics
```bash
pydevkit inspect
```

#### Find Unused Functions, Variables, and Imports
```bash
pydevkit deadcode
```

#### Generate Pytest Tests
```bash
pydevkit testgen
```

#### Create README.md File
```bash
pydevkit readme
```

### Project Structure
```markdown
pydevkit/
pydevkit/
analysis/
doctor.py
inspector.py
cli.py
deadcode/
scanner.py
reporter.py
readme/
analyzer.py
generator.py
testgen/
extractor.py
generator.py
utils/
api_client.py
config.py
file_utils.py
sample_project/
example.py
setup.py
tests/
test_analysis.py
test_deadcode.py
test_readme.py
test_testgen.py
```

### Contributing

Contributions are welcome! Please create a pull request or issue to share your ideas or fix any issues you've found.

### License

PyDevKit is released under the MIT License. See [LICENSE](LICENSE) for details.

### Dependencies

* [Click](https://click.palletsprojects.com/en/8.1.x/)
* [Groq](https://groq.com/)
* [Rich](https://rich.readthedocs.io/en/latest/)
* [Pytest](https://docs.pytest.org/en/latest/)
* [Python-dotenv](https://pypi.org/project/python-dotenv/)