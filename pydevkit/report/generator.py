"""Self-contained HTML report generator for PyDevKit."""

from pathlib import Path
from typing import Any, Dict, List

from pydevkit.analysis.doctor import run_doctor
from pydevkit.analysis.inspector import inspect_project
from pydevkit.deadcode.scanner import scan_deadcode
from pydevkit.readme.analyzer import analyze_project
from pydevkit.testgen.extractor import extract_functions
from pydevkit.utils import console


def _escape(text: Any) -> str:
    """Escape HTML special characters."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _severity_color(severity: str) -> str:
    """Return a hex color for a severity level."""
    return {"high": "#e74c3c", "medium": "#f39c12", "low": "#3498db"}.get(severity, "#95a5a6")


def _type_color(symbol_type: str) -> str:
    """Return a hex color for a dead-code symbol type."""
    return {
        "function": "#e74c3c",
        "import": "#f39c12",
        "variable": "#3498db",
        "class": "#9b59b6",
        "method": "#1abc9c",
    }.get(symbol_type, "#95a5a6")


def _build_summary_card(label: str, value: Any, color: str = "#2c3e50") -> str:
    """Render a single summary metric card."""
    return f"""
    <div class="card">
      <div class="card-value" style="color:{color}">{_escape(value)}</div>
      <div class="card-label">{_escape(label)}</div>
    </div>"""


def _build_summary_section(inspection: Dict[str, Any], doctor_summary: Dict[str, Any]) -> str:
    """Render the top summary cards."""
    cards = [
        _build_summary_card("Python Files", inspection.get("python_files", 0), "#2c3e50"),
        _build_summary_card("Functions", inspection.get("functions", 0), "#2c3e50"),
        _build_summary_card("Classes", inspection.get("classes", 0), "#2c3e50"),
        _build_summary_card("Lines of Code", f"{inspection.get('total_lines', 0):,}", "#2c3e50"),
        _build_summary_card("Dead Code Items", inspection.get("deadcode", 0), "#e74c3c" if inspection.get("deadcode") else "#27ae60"),
        _build_summary_card("Syntax Errors", inspection.get("syntax_errors", 0), "#e74c3c" if inspection.get("syntax_errors") else "#27ae60"),
        _build_summary_card("Health Issues", doctor_summary.get("issues", 0), "#e74c3c" if doctor_summary.get("high") else "#f39c12" if doctor_summary.get("medium") else "#27ae60"),
        _build_summary_card("Tests Folder", "Yes" if inspection.get("has_tests") else "No", "#27ae60" if inspection.get("has_tests") else "#e74c3c"),
    ]
    return f'<div class="summary-grid">{"".join(cards)}</div>'


def _build_deadcode_section(results: List[Dict[str, Any]]) -> str:
    """Render the dead code table."""
    if not results:
        return '<div class="empty-state">✅ No dead code detected — your project looks clean!</div>'

    rows = ""
    for item in results:
        color = _type_color(item.get("type", ""))
        rows += f"""
      <tr>
        <td><code>{_escape(item.get("file", ""))}</code></td>
        <td>{_escape(item.get("line", ""))}</td>
        <td><span class="badge" style="background:{color}">{_escape(item.get("type", ""))}</span></td>
        <td><strong>{_escape(item.get("name", ""))}</strong></td>
        <td><span class="badge" style="background:{_severity_color(item.get("severity", ""))}">{_escape(item.get("severity", ""))}</span></td>
        <td>{_escape(item.get("suggestion", ""))}</td>
      </tr>"""

    return f"""
    <table class="data-table">
      <thead>
        <tr>
          <th>File</th><th>Line</th><th>Type</th><th>Name</th><th>Severity</th><th>Suggestion</th>
        </tr>
      </thead>
      <tbody>{rows}
      </tbody>
    </table>"""


def _build_doctor_section(issues: List[Dict[str, Any]]) -> str:
    """Render the doctor issues list."""
    if not issues:
        return '<div class="empty-state">✅ No health issues found — great job!</div>'

    items = ""
    for issue in issues:
        sev = issue.get("severity", "low")
        color = _severity_color(sev)
        items += f"""
      <div class="issue-card" style="border-left:4px solid {color}">
        <div class="issue-header">
          <span class="badge" style="background:{color}">{_escape(sev.upper())}</span>
          <code>{_escape(issue.get("code", ""))}</code>
        </div>
        <p class="issue-message">{_escape(issue.get("message", ""))}</p>
        <p class="issue-suggestion">💡 {_escape(issue.get("suggestion", ""))}</p>
      </div>"""

    return f'<div class="issues-list">{items}</div>'


def _build_functions_section(functions: List[Dict[str, Any]]) -> str:
    """Render the public functions table."""
    if not functions:
        return '<div class="empty-state">No public functions found.</div>'

    rows = ""
    for func in functions:
        args = ", ".join(func.get("args", [])) or "—"
        doc = (func.get("docstring", "") or "—").strip()
        if len(doc) > 80:
            doc = doc[:77] + "…"
        rows += f"""
      <tr>
        <td><strong>{_escape(func.get("name", ""))}</strong></td>
        <td><code>{_escape(args)}</code></td>
        <td><code>{_escape(func.get("return_type") or "—")}</code></td>
        <td><code>{_escape(func.get("file", ""))}</code></td>
        <td>{_escape(doc)}</td>
      </tr>"""

    return f"""
    <table class="data-table">
      <thead>
        <tr>
          <th>Function</th><th>Arguments</th><th>Returns</th><th>File</th><th>Description</th>
        </tr>
      </thead>
      <tbody>{rows}
      </tbody>
    </table>"""


def _build_classes_section(classes: List[Dict[str, Any]]) -> str:
    """Render the public classes table."""
    if not classes:
        return '<div class="empty-state">No public classes found.</div>'

    rows = ""
    for cls in classes:
        doc = (cls.get("docstring", "") or "—").strip()
        if len(doc) > 80:
            doc = doc[:77] + "…"
        rows += f"""
      <tr>
        <td><strong>{_escape(cls.get("name", ""))}</strong></td>
        <td><code>{_escape(cls.get("file", ""))}</code></td>
        <td>{_escape(doc)}</td>
      </tr>"""

    return f"""
    <table class="data-table">
      <thead>
        <tr><th>Class</th><th>File</th><th>Description</th></tr>
      </thead>
      <tbody>{rows}
      </tbody>
    </table>"""


def _build_dependencies_section(deps: List[str]) -> str:
    """Render the dependencies list."""
    if not deps:
        return '<div class="empty-state">No dependencies detected (no requirements.txt found).</div>'

    items = "".join(f"<li><code>{_escape(dep)}</code></li>" for dep in deps)
    return f"<ul class='dep-list'>{items}</ul>"


def _build_syntax_errors_section(errors: List[Dict[str, Any]]) -> str:
    """Render syntax errors table."""
    if not errors:
        return '<div class="empty-state">✅ No syntax errors found.</div>'

    rows = ""
    for err in errors:
        rows += f"""
      <tr class="error-row">
        <td><code>{_escape(err.get("file", ""))}</code></td>
        <td>{_escape(err.get("line", ""))}</td>
        <td>{_escape(err.get("message", ""))}</td>
      </tr>"""

    return f"""
    <table class="data-table">
      <thead><tr><th>File</th><th>Line</th><th>Error</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>"""


def _build_structure_section(python_files: List[str], entry_point: str | None) -> str:
    """Render the project structure overview."""
    entry = _escape(entry_point or "Not detected")
    file_items = "".join(f"<li><code>{_escape(f)}</code></li>" for f in sorted(python_files))
    return f"""
    <div class="structure-section">
      <p><strong>Entry Point:</strong> <code>{entry}</code></p>
      <h4>Python Files ({len(python_files)})</h4>
      <ul class="file-list">{file_items}</ul>
    </div>"""


def generate_html_report(
    project_name: str,
    inspection: Dict[str, Any],
    doctor_report: Dict[str, Any],
    deadcode_results: List[Dict[str, Any]],
    functions: List[Dict[str, Any]],
    classes: List[Dict[str, Any]],
    dependencies: List[str],
    python_files: List[str],
    entry_point: str | None,
) -> str:
    """Build the complete HTML report string."""
    summary = inspection.get("summary", {})
    doctor_summary = doctor_report.get("summary", {})
    issues = doctor_report.get("issues", [])
    syntax_errors = inspection.get("syntax_errors", [])

    high_count = doctor_summary.get("high", 0)
    medium_count = doctor_summary.get("medium", 0)
    low_count = doctor_summary.get("low", 0)

    health_grade = "A" if high_count == 0 and medium_count == 0 else "B" if high_count == 0 else "C"
    grade_color = {"A": "#27ae60", "B": "#f39c12", "C": "#e74c3c"}[health_grade]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PyDevKit Report — {_escape(project_name)}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
      background: #f5f7fa; color: #2c3e50; line-height: 1.6;
    }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; }}

    /* Header */
    .report-header {{
      background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
      color: white; border-radius: 12px; padding: 2rem 2.5rem; margin-bottom: 2rem;
      display: flex; justify-content: space-between; align-items: center;
    }}
    .report-header h1 {{ font-size: 1.8rem; font-weight: 700; }}
    .report-header h1 span {{ opacity: 0.7; font-weight: 400; font-size: 0.95rem; display: block; margin-top: 0.25rem; }}
    .grade-badge {{
      width: 72px; height: 72px; border-radius: 50%;
      background: {grade_color}; color: white; font-size: 2rem; font-weight: 800;
      display: flex; align-items: center; justify-content: center;
      box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}

    /* Summary cards */
    .summary-grid {{
      display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
      gap: 1rem; margin-bottom: 2rem;
    }}
    .card {{
      background: white; border-radius: 10px; padding: 1.25rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07); text-align: center;
    }}
    .card-value {{ font-size: 1.8rem; font-weight: 700; }}
    .card-label {{ font-size: 0.8rem; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 0.25rem; }}

    /* Sections */
    .section {{
      background: white; border-radius: 12px; padding: 1.75rem 2rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07); margin-bottom: 1.5rem;
    }}
    .section h2 {{
      font-size: 1.25rem; margin-bottom: 1.25rem; padding-bottom: 0.75rem;
      border-bottom: 2px solid #f0f0f0; display: flex; align-items: center; gap: 0.5rem;
    }}
    .section h2 .count {{
      background: #ecf0f1; color: #7f8c8d; font-size: 0.75rem;
      padding: 0.15rem 0.55rem; border-radius: 20px; font-weight: 600;
    }}

    /* Badges */
    .badge {{
      display: inline-block; padding: 0.15rem 0.55rem; border-radius: 4px;
      color: white; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;
    }}

    /* Tables */
    .data-table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
    .data-table th {{
      text-align: left; padding: 0.65rem 0.75rem; background: #f8f9fa;
      color: #7f8c8d; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.4px;
    }}
    .data-table td {{ padding: 0.65rem 0.75rem; border-bottom: 1px solid #f0f0f0; vertical-align: top; }}
    .data-table tr:last-child td {{ border-bottom: none; }}
    .data-table tr:hover td {{ background: #fafbfc; }}
    .error-row td {{ color: #e74c3c; }}

    /* Issues */
    .issues-list {{ display: flex; flex-direction: column; gap: 0.75rem; }}
    .issue-card {{
      background: #fafbfc; border-radius: 8px; padding: 1rem 1.25rem;
    }}
    .issue-header {{ display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem; }}
    .issue-header code {{ font-size: 0.82rem; color: #7f8c8d; }}
    .issue-message {{ font-size: 0.92rem; margin-bottom: 0.35rem; }}
    .issue-suggestion {{ font-size: 0.85rem; color: #27ae60; }}

    /* Empty state */
    .empty-state {{
      text-align: center; padding: 2rem; color: #27ae60; font-size: 1rem;
      background: #f0fff4; border-radius: 8px;
    }}

    /* Lists */
    .dep-list, .file-list {{ list-style: none; display: flex; flex-wrap: wrap; gap: 0.4rem; }}
    .dep-list li code, .file-list li code {{
      background: #f0f4f8; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.82rem;
    }}
    .structure-section p {{ margin-bottom: 0.75rem; }}
    .structure-section h4 {{ margin-bottom: 0.5rem; color: #7f8c8d; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.4px; }}

    /* Footer */
    .report-footer {{
      text-align: center; color: #bdc3c7; font-size: 0.82rem; margin-top: 2rem; padding-top: 1rem;
      border-top: 1px solid #ecf0f1;
    }}

    @media (max-width: 640px) {{
      .report-header {{ flex-direction: column; text-align: center; gap: 1rem; }}
      .summary-grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}
  </style>
</head>
<body>
<div class="container">

  <div class="report-header">
    <h1>📊 PyDevKit Report<br><span>{_escape(project_name)}</span></h1>
    <div class="grade-badge">{health_grade}</div>
  </div>

  {_build_summary_section(summary, doctor_summary)}

  <div class="section">
    <h2>🏥 Health Issues <span class="count">{high_count} high · {medium_count} medium · {low_count} low</span></h2>
    {_build_doctor_section(issues)}
  </div>

  <div class="section">
    <h2>🧹 Dead Code <span class="count">{len(deadcode_results)} found</span></h2>
    {_build_deadcode_section(deadcode_results)}
  </div>

  <div class="section">
    <h2>⚠️ Syntax Errors <span class="count">{len(syntax_errors)}</span></h2>
    {_build_syntax_errors_section(syntax_errors)}
  </div>

  <div class="section">
    <h2>📦 Public Functions <span class="count">{len(functions)}</span></h2>
    {_build_functions_section(functions)}
  </div>

  <div class="section">
    <h2>🏗️ Public Classes <span class="count">{len(classes)}</span></h2>
    {_build_classes_section(classes)}
  </div>

  <div class="section">
    <h2>📁 Project Structure</h2>
    {_build_structure_section(python_files, entry_point)}
  </div>

  <div class="section">
    <h2>📋 Dependencies <span class="count">{len(dependencies)}</span></h2>
    {_build_dependencies_section(dependencies)}
  </div>

  <div class="report-footer">
    Generated by <strong>PyDevKit</strong> — Python Developer Productivity Toolkit
  </div>

</div>
</body>
</html>"""


def generate_report(project_path: str, output: str | None = None) -> None:
    """Run all analyses and write an HTML report."""
    root = Path(project_path)

    console.print(f"[bold blue]Generating HTML report for {root}...[/bold blue]")

    # Collect all data
    inspection = inspect_project(project_path)
    doctor_report = run_doctor(project_path)
    deadcode_results = scan_deadcode(project_path)
    functions = extract_functions(project_path)
    project_meta = analyze_project(project_path)
    classes = project_meta.get("classes", [])
    dependencies = project_meta.get("dependencies", [])
    python_files = project_meta.get("python_files", [])
    entry_point = project_meta.get("entry_point")
    project_name = project_meta.get("package_name") or project_meta.get("project_name") or root.name

    # Build HTML
    html = generate_html_report(
        project_name=project_name,
        inspection=inspection,
        doctor_report=doctor_report,
        deadcode_results=deadcode_results,
        functions=functions,
        classes=classes,
        dependencies=dependencies,
        python_files=python_files,
        entry_point=entry_point,
    )

    # Write output
    if output:
        output_path = Path(output)
    else:
        output_path = root / "pydevkit-report.html"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    console.print(f"[bold green]Report saved to: {output_path}[/bold green]")
