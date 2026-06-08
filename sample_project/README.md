# Sample Project
================

A Python project providing utility functions for various tasks.

### Badges

[![Python Version](https://img.shields.io/badge/Python->=3.8-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue)](https://opensource.org/licenses/MIT)

### Description
------------

This project contains a set of utility functions for various tasks, including basic math operations, string normalization, and more.

### Features
------------

*   Basic math operations
*   String normalization
*   Point distance calculation

### Installation
------------

To install this project, run the following command:

```bash
pip install -e .
```

### Usage Examples
---------------

### Basic Math Operations

```python
# Example usage of add_numbers and multiply_numbers
import example

print(example.add_numbers(2, 3))  # Output: 5
print(example.multiply_numbers(4, 5))  # Output: 20
```

### String Normalization

```python
# Example usage of normalize_text
import example

print(example.normalize_text("   Hello   World   "))  # Output: "hello world"
```

### Point Distance Calculation

```python
# Example usage of distance_from_origin
import example

print(example.distance_from_origin(10, 15))  # Output: 17.320508075688775
```

### Project Structure
-------------------

```markdown
-sample_project/
    |- example.py
    |- tests/
        |- test_example.py
    |- README.md
    |- setup.py
    |- requirements.txt
```

### Contributing Guide
-------------------

Contributions are welcome! To contribute, create a pull request with your changes. Please make sure to:

*   Read the code style guidelines
*   Follow the PEP 8 style guide
*   Write comprehensive unit tests
*   Update the changelog if necessary

### License
-----

Licensed under the MIT License. See [LICENSE.md](LICENSE.md) for details.