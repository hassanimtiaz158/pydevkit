"""Project inspection and health analysis package."""

from pydevkit.analysis.doctor import run_doctor
from pydevkit.analysis.inspector import inspect_project

__all__ = ["inspect_project", "run_doctor"]
