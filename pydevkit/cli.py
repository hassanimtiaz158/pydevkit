"""Command line interface for PyDevKit."""

import json
from pathlib import Path

import click
from rich.panel import Panel
from rich.table import Table

from pydevkit.analysis.doctor import run_doctor
from pydevkit.analysis.inspector import inspect_project
from pydevkit.deadcode.reporter import print_deadcode_report
from pydevkit.deadcode.scanner import remove_unused_imports, scan_deadcode
from pydevkit.readme.generator import generate_readme
from pydevkit.report.generator import generate_report
from pydevkit.testgen.generator import generate_tests
from pydevkit.utils import console
from pydevkit.utils.config import load_config


@click.group()
def cli() -> None:
    """PyDevKit developer productivity commands."""


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
        results = scan_deadcode(path, include_tests=include_tests if include_tests else None)
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
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.argument("path")
@click.option("--no-ai", is_flag=True, help="Generate README.md without calling Groq AI.")
def readme(path: str, no_ai: bool) -> None:
    """Generate a README.md file."""
    try:
        console.print(Panel(f"Generating README for {Path(path)}", title="PyDevKit README", style="bold blue"))
        generate_readme(path, use_ai=not no_ai)
    except (OSError, RuntimeError) as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.argument("path")
@click.option("--output", default=None, help="Optional output file or directory for generated tests.")
@click.option("--offline", is_flag=True, help="Generate conservative tests without calling Groq AI.")
def testgen(path: str, output: str | None, offline: bool) -> None:
    """Generate pytest tests for public functions."""
    try:
        console.print(Panel(f"Generating tests for {Path(path)}", title="PyDevKit Testgen", style="bold blue"))
        config = load_config(path).get("testgen", {})
        configured_output = output or config.get("output")
        configured_offline = offline or bool(config.get("offline", False))
        generate_tests(path, output=str(configured_output) if configured_output else None, use_ai=not configured_offline)
    except (OSError, RuntimeError) as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.argument("path")
@click.option("--json", "json_output", is_flag=True, help="Print machine-readable JSON inspection.")
def inspect(path: str, json_output: bool) -> None:
    """Inspect project structure, metrics, and risks."""
    try:
        console.print(Panel(f"Inspecting {Path(path)}", title="PyDevKit Inspect", style="bold blue"))
        report = inspect_project(path)
        if json_output:
            console.print_json(json.dumps(report, indent=2))
            return

        summary = report["summary"]
        table = Table(title="Project Summary")
        table.add_column("Metric")
        table.add_column("Value", justify="right")
        for key, value in summary.items():
            table.add_row(str(key).replace("_", " ").title(), str(value))
        console.print(table)

        if report.get("syntax_errors"):
            error_table = Table(title="Syntax Errors")
            error_table.add_column("File")
            error_table.add_column("Line", justify="right")
            error_table.add_column("Message")
            for item in report["syntax_errors"]:
                error_table.add_row(str(item["file"]), str(item["line"]), str(item["message"]))
            console.print(error_table)
    except (OSError, RuntimeError) as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.argument("path")
@click.option("--json", "json_output", is_flag=True, help="Print machine-readable doctor report.")
@click.option("--ci", is_flag=True, help="Exit with a non-zero status if high or medium issues are found.")
def doctor(path: str, json_output: bool, ci: bool) -> None:
    """Run project health checks."""
    try:
        console.print(Panel(f"Checking project health for {Path(path)}", title="PyDevKit Doctor", style="bold blue"))
        report = run_doctor(path)
        if json_output:
            console.print_json(json.dumps(report, indent=2))
        else:
            summary = report["summary"]
            console.print(
                Panel(
                    f"Issues: {summary['issues']} | High: {summary['high']} | Medium: {summary['medium']} | Low: {summary['low']}",
                    title="Health Summary",
                    style="green" if summary["issues"] == 0 else "yellow",
                )
            )
            table = Table(title="Doctor Issues")
            table.add_column("Severity")
            table.add_column("Code")
            table.add_column("Message")
            table.add_column("Suggestion")
            for issue in report["issues"]:
                table.add_row(
                    str(issue["severity"]),
                    str(issue["code"]),
                    str(issue["message"]),
                    str(issue["suggestion"]),
                )
            console.print(table)
        if ci and int(report["summary"]["high"]) + int(report["summary"]["medium"]) > 0:
            raise click.exceptions.Exit(1)
    except (OSError, RuntimeError) as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.argument("path")
@click.option("--output", default=None, help="Output file path (defaults to <path>/pydevkit-report.html).")
def report(path: str, output: str | None) -> None:
    """Generate an HTML report for the project."""
    try:
        console.print(Panel(f"Generating HTML report for {Path(path)}", title="PyDevKit Report", style="bold blue"))
        generate_report(path, output=output)
    except (OSError, RuntimeError) as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    cli()
