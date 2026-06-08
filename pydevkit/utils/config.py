"""Configuration loading for PyDevKit."""

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    tomllib = None  # type: ignore[assignment]

TOML_DECODE_ERROR = tomllib.TOMLDecodeError if tomllib is not None else ValueError

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
        if value.lower() in {"none", "null"}:
            return None
        if value.startswith("[") and value.endswith("]"):
            items = value[1:-1].strip()
            if not items:
                return []
            return [
                item.strip().strip('"').strip("'")
                for item in items.split(",")
                if item.strip()
            ]
        try:
            return int(value)
        except ValueError:
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


def _normalize_config(config: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Normalize loaded config values into the shapes PyDevKit expects."""
    try:
        testgen = config.setdefault("testgen", {})
        if testgen.get("output") == "":
            testgen["output"] = None
        deadcode = config.setdefault("deadcode", {})
        for key in ("ignore_names", "ignore_files"):
            value = deadcode.get(key, [])
            deadcode[key] = value if isinstance(value, list) else [str(value)]
        return config
    except (AttributeError, TypeError) as exc:
        raise RuntimeError(f"Invalid PyDevKit config values: {exc}") from exc


def _load_with_tomllib(config_path: Path) -> Dict[str, Dict[str, Any]] | None:
    """Load TOML with the standard parser when available."""
    try:
        if tomllib is None:
            return None
        with config_path.open("rb") as config_file:
            parsed = tomllib.load(config_file)
        return {
            str(section): dict(values)
            for section, values in parsed.items()
            if isinstance(values, dict)
        }
    except (OSError, TOML_DECODE_ERROR) as exc:
        raise RuntimeError(f"Invalid .pydevkit.toml: {exc}") from exc


def load_config(project_path: str) -> Dict[str, Dict[str, Any]]:
    """Load .pydevkit.toml from a project directory with safe defaults."""
    try:
        root = Path(project_path)
        config: Dict[str, Dict[str, Any]] = deepcopy(DEFAULT_CONFIG)
        config_path = root / ".pydevkit.toml"
        if not config_path.exists():
            return config

        parsed_config = _load_with_tomllib(config_path)
        if parsed_config is not None:
            for section, values in parsed_config.items():
                config.setdefault(section, {})
                config[section].update(values)
            return _normalize_config(config)

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
        return _normalize_config(config)
    except OSError as exc:
        raise RuntimeError(f"Unable to load PyDevKit config: {exc}") from exc
