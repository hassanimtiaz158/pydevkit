"""Configuration loading for PyDevKit."""

from pathlib import Path
from typing import Any, Dict

from pydevkit.utils.file_utils import read_file_safe


DEFAULT_CONFIG: Dict[str, Dict[str, Any]] = {
    "deadcode": {
        "ignore_names": [],
        "ignore_files": [],
        "include_tests": False,
        "min_confidence": "low",
    },
    "testgen": {
        "offline": False,
        "output": None,
    },
    "doctor": {
        "max_function_lines": 80,
        "max_function_args": 6,
        "max_branches": 12,
    },
}


def _parse_value(raw_value: str) -> Any:
    """Parse a small TOML-like scalar or list value."""
    try:
        value = raw_value.strip()
        if value.lower() in {"true", "false"}:
            return value.lower() == "true"
        if value.startswith("[") and value.endswith("]"):
            items = value[1:-1].strip()
            if not items:
                return []
            return [
                item.strip().strip('"').strip("'")
                for item in items.split(",")
                if item.strip()
            ]
        if value.isdigit():
            return int(value)
        return value.strip('"').strip("'")
    except (AttributeError, ValueError):
        return raw_value


def _merge_config(config: Dict[str, Dict[str, Any]], section: str, key: str, value: Any) -> None:
    """Merge one parsed config key into the active config."""
    try:
        config.setdefault(section, {})
        config[section][key] = value
    except TypeError as exc:
        raise RuntimeError(f"Invalid config entry [{section}] {key}: {exc}") from exc


def load_config(project_path: str) -> Dict[str, Dict[str, Any]]:
    """Load .pydevkit.toml from a project directory with safe defaults."""
    try:
        root = Path(project_path)
        config: Dict[str, Dict[str, Any]] = {
            section: values.copy()
            for section, values in DEFAULT_CONFIG.items()
        }
        config_path = root / ".pydevkit.toml"
        if not config_path.exists():
            return config

        current_section = ""
        for line in read_file_safe(config_path).splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("[") and stripped.endswith("]"):
                current_section = stripped.strip("[]").strip()
                continue
            if "=" not in stripped or not current_section:
                continue
            key, raw_value = [part.strip() for part in stripped.split("=", 1)]
            _merge_config(config, current_section, key, _parse_value(raw_value))
        return config
    except OSError as exc:
        raise RuntimeError(f"Unable to load PyDevKit config: {exc}") from exc
