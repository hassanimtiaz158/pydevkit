# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyDevKit is a CLI toolkit for Python project maintenance — dead code detection, project inspection, health checks, test generation, and README generation. Built with Click, Rich, and Groq AI (optional).

## Commands

```bash
# Install for development
pip install -r requirements.txt
pip install -e .

# Run all tests
pytest -q

# Run a single test file
pytest tests/test_deadcode.py -q

# Run a single test
pytest tests/test_deadcode.py::test_scan_deadcode_detects_unused_sample_symbols -q

# Run tests with warnings as errors
pytest -q -W error

# CLI usage examples
pydevkit inspect .
pydevkit doctor .
pydevkit deadcode .
pydevkit testgen . --offline
pydevkit readme . --no-ai
pydevkit report .
```

## Architecture

The CLI entry point is `pydevkit/cli.py` (a Click group). It dispatches to four sub-packages under `pydevkit/`:

- **`analysis/`** — `inspector.py` walks Python files collecting AST metrics (imports, functions, classes, syntax errors, complexity). `doctor.py` runs the inspector and layers on health checks (missing files, unresolved imports, unused deps, complexity thresholds).
- **`deadcode/`** — `scanner.py` does AST-based dead code detection by collecting definitions vs usages across files, with configurable confidence thresholds and file/name ignore patterns. `reporter.py` renders results via Rich tables.
- **`testgen/`** — `extractor.py` pulls public function signatures from AST. `generator.py` either calls Groq for AI-generated pytest tests or produces offline smoke tests (import + callable assertion).
- **`readme/`** — `analyzer.py` collects project metadata (setup.py/pyproject.toml, functions, classes, deps, entry points). `generator.py` uses Groq or a built-in template to write README.md.
- **`report/`** — `generator.py` combines data from inspect, doctor, deadcode, and testgen into a self-contained HTML file with a health grade, summary cards, and color-coded issue/dead-code tables.
- **`utils/`** — `file_utils.py` handles file discovery (respects `.gitignore`/`.pydevkitignore`), safe reads/writes. `config.py` loads `.pydevkit.toml` with a custom TOML parser (supports `tomllib` on 3.11+, falls back to line-based parsing). `api_client.py` wraps Groq with retry + offline fallback logic.

## Key Design Decisions

- **AST-based analysis**: All code inspection (deadcode, inspection, test extraction, README analysis) uses Python's `ast` module — no runtime imports of target projects. This keeps analysis safe and fast.
- **Offline-first fallbacks**: AI features (testgen, readme) degrade gracefully. When `GROQ_API_KEY` is missing or rate-limited, `is_offline_fallback_error()` returns True and deterministic templates are used instead.
- **Config via `.pydevkit.toml`**: Per-project settings for deadcode ignore patterns, test output paths, and doctor complexity thresholds. `load_config()` merges defaults with project overrides.
- **`sample_project/` is the test fixture**: Tests use `sample_project/` as a known fixture with intentionally unused symbols (`unused_discount`, `UNUSED_CONSTANT`, `statistics` import).

## Testing Notes

- Tests use `tmp_path` fixtures for isolation; avoid relying on global state.
- `pytest.ini` sets `--basetemp=.pytest_tmp` to work around Windows temp permission issues.
- All test files use a `PROJECT_ROOT` constant resolved from `__file__` to locate `sample_project/`.
- Tests wrap calls in `try/except RuntimeError` because internal functions raise `RuntimeError` on unrecoverable errors (OSError, SyntaxError in target files, etc.).

## Dependencies

- `click` — CLI framework
- `rich` — terminal output formatting
- `groq` — AI API client (optional at runtime, required at install)
- `python-dotenv` — loads `.env` for `GROQ_API_KEY`
- `pytest` — test runner
