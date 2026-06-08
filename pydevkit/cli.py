"""Command line interface for PyDevKit."""

from pathlib import Path

import click
from rich.panel import Panel

from pydevkit.deadcode.reporter import print_deadcode_report
from pydevkit.deadcode.scanner import remove_unused_imports, scan_deadcode
from pydevkit.readme.generator import generate_readme
from pydevkit.testgen.generator import generate_tests
from pydevkit.utils import console


@click.group()
def cli() -> None:
    """PyDevKit developer productivity commands."""
    try:
        return None
    except RuntimeError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")


@cli.command()
@click.argument("path")
@click.option("--fix", is_flag=True, help="Remove unused imports detected by the scanner.")
def deadcode(path: str, fix: bool) -> None:
    """Find unused functions, variables, and imports."""
    try:
        console.print(Panel(f"Scanning dead code in {Path(path)}", title="PyDevKit Deadcode", style="bold blue"))
        results = scan_deadcode(path)
        print_deadcode_report(results)
        if fix:
            removed = remove_unused_imports(path, results)
            console.print(f"[green]Removed {removed} unused import lines.[/green]")
    except (OSError, RuntimeError) as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")


@cli.command()
@click.argument("path")
@click.option("--no-ai", is_flag=True, help="Generate README.md without calling Groq AI.")
def readme(path: str, no_ai: bool) -> None:
    """Generate a README.md file."""
    try:
        console.print(Panel(f"Generating README for {Path(path)}", title="PyDevKit README", style="bold blue"))
        generate_readme(path, use_ai=not no_ai)
    except (OSError, RuntimeError) as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")


@cli.command()
@click.argument("path")
@click.option("--output", default=None, help="Optional output file or directory for generated tests.")
def testgen(path: str, output: str | None) -> None:
    """Generate pytest tests for public functions."""
    try:
        console.print(Panel(f"Generating tests for {Path(path)}", title="PyDevKit Testgen", style="bold blue"))
        generate_tests(path, output=output)
    except (OSError, RuntimeError) as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")


if __name__ == "__main__":
    try:
        cli()
    except RuntimeError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
