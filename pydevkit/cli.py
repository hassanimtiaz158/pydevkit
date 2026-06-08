"""Command line interface for PyDevKit."""

import json
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
@click.option("--dry-run", is_flag=True, help="Show how many imports would be fixed without editing files.")
@click.option("--json", "json_output", is_flag=True, help="Print machine-readable JSON results.")
@click.option("--ci", is_flag=True, help="Exit with a non-zero status if dead code is found.")
@click.option("--include-tests", is_flag=True, help="Include tests and test_*.py files in the scan.")
def deadcode(path: str, fix: bool, dry_run: bool, json_output: bool, ci: bool, include_tests: bool) -> None:
    """Find unused functions, variables, and imports."""
    try:
        console.print(Panel(f"Scanning dead code in {Path(path)}", title="PyDevKit Deadcode", style="bold blue"))
        results = scan_deadcode(path, include_tests=include_tests)
        if json_output:
            console.print_json(json.dumps(results, indent=2))
        else:
            print_deadcode_report(results)
        if fix:
            removed = remove_unused_imports(path, results, dry_run=dry_run)
            action = "Would remove" if dry_run else "Removed"
            console.print(f"[green]{action} {removed} unused import aliases.[/green]")
        if ci and results:
            raise click.exceptions.Exit(1)
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
@click.option("--offline", is_flag=True, help="Generate conservative tests without calling Groq AI.")
def testgen(path: str, output: str | None, offline: bool) -> None:
    """Generate pytest tests for public functions."""
    try:
        console.print(Panel(f"Generating tests for {Path(path)}", title="PyDevKit Testgen", style="bold blue"))
        generate_tests(path, output=output, use_ai=not offline)
    except (OSError, RuntimeError) as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")


if __name__ == "__main__":
    try:
        cli()
    except RuntimeError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
