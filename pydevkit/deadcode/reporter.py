"""Rich reporting for dead code results."""

from pathlib import Path
from typing import Dict, List

from rich.panel import Panel
from rich.table import Table

from pydevkit.utils import console


def print_deadcode_report(results: List[Dict[str, object]]) -> None:
    """Print dead code results as a Rich table."""
    try:
        if not results:
            console.print(Panel("No dead code found! ✅", style="green", title="Success"))
            return

        table = Table(title="Dead Code Report")
        table.add_column("File", overflow="fold")
        table.add_column("Line", justify="right")
        table.add_column("Type")
        table.add_column("Name")
        table.add_column("Suggestion")

        styles = {"function": "red", "import": "yellow", "variable": "cyan"}
        files = set()
        for item in results:
            symbol_type = str(item.get("type", ""))
            style = styles.get(symbol_type, "white")
            file_name = str(Path(str(item.get("file", ""))))
            files.add(file_name)
            table.add_row(
                file_name,
                str(item.get("line", "")),
                symbol_type,
                str(item.get("name", "")),
                str(item.get("suggestion", "")),
                style=style,
            )

        console.print(table)
        console.print(f"[bold]Found {len(results)} unused symbols in {len(files)} files[/bold]")
    except (OSError, RuntimeError) as exc:
        raise RuntimeError(f"Unable to print dead code report: {exc}") from exc
