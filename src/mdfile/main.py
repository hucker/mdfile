#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["typer","rich","click"]
# ///
"""
Markdown File Manipulation (MNM) - CLI tool for converting files to Markdown.

Supports CSV, JSON, code files, plain text, and updating existing Markdown
with variable replacements and custom formatting.

Configuration sources (lowest → highest precedence):
1. Defaults
2. mdfile.json
3. pyproject.toml ([tool.mdfile] section)
4. Environment variables (MD_FILE_*)
5. CLI arguments
"""

import json
import os
import pathlib
import tomllib
from importlib.metadata import version
from typing import Optional, Any, Dict

import typer
from rich.console import Console
from rich.markdown import Markdown

from md_updater import update_markdown_file

__app_name__ = "mdfile"
__version__ = version(__app_name__)

DEFAULT_CONFIG: Dict[str, Any] = {
    "file_name": None,
    "output": None,
    "bold_values": None,
    "auto_break": True,
    "vars_file": None,
    "plain": False,
}

app = typer.Typer(add_completion=False)


# ----------------------------
# Helper functions
# ----------------------------

def version_callback(value: bool):
    """Show version and exit."""
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


def load_json_config(path: pathlib.Path | None = None) -> dict[str, Any]:
    """Load configuration from mdfile.json."""
    if path is None:
        path = pathlib.Path.cwd() / "mdfile.json"
    if not path.exists():
        return {}
    with path.open("rt") as f:
        return json.load(f)


def find_pyproject(start: pathlib.Path | None = None,
                   name: str = "pyproject.toml") -> pathlib.Path | None:
    """Walk upward from start to find first pyproject.toml."""
    if start is None:
        start = pathlib.Path.cwd()
    for p in [start] + list(start.parents):
        candidate = p / name
        if candidate.exists():
            return candidate
    return None


def load_pyproject_config(pyproject_file: pathlib.Path | None = None) -> dict[str, Any]:
    """Load [tool.mdfile] from pyproject.toml."""
    if pyproject_file is None:
        pyproject_file = find_pyproject()
        if pyproject_file is None:
            return {}
    with pyproject_file.open("rt") as f:
        data = tomllib.load(f)
    return data.get("tool", {}).get("mdfile", {})


def load_env_config() -> dict[str, Any]:
    """Load environment variables starting with MD_FILE_ (case-insensitive)."""
    cfg: dict[str, Any] = {}
    prefix = "MD_FILE_"
    for k, v in os.environ.items():
        if k.upper().startswith(prefix):
            key = k[len(prefix):].lower()
            cfg[key] = v
    return cfg


def merge_config(
    *,
    file_name: str | None = None,
    output: str | None = None,
    bold_values: str | None = None,
    auto_break: bool | None = None,
    vars_file: pathlib.Path | None = None,
    plain: bool | None = None,
    base_path: pathlib.Path | None = None,
    pyproject_dir: pathlib.Path | None = None,
) -> dict[str, Any]:
    """Merge configuration sources into a single dict.

    Precedence: CLI > Env > pyproject.toml > mdfile.json > defaults
    """
    cfg = DEFAULT_CONFIG.copy()
    cfg |= load_json_config(base_path)
    cfg |= load_pyproject_config(pyproject_dir)
    cfg |= load_env_config()

    # CLI overrides
    cli_args = {
        "file_name": file_name,
        "output": output,
        "bold_values": bold_values,
        "auto_break": auto_break,
        "vars_file": vars_file,
        "plain": plain,
    }
    for k, v in cli_args.items():
        if v is not None:
            cfg[k] = v
    return cfg


def ensure_valid_args(
    file_name: str | None,
    output: str | None,
    bold_values: str | None,
    auto_break: bool,
    plain: bool,
    vars_file: str | None,
)->bool:
    """
    Validate command arguments and exit with an error message if invalid.

    Ensures required arguments are provided and files exist. Also prevents
    dangerous overwrites where output file is the same as input file.
    """
    hlp = '(--help for details'
    if file_name is None:
        typer.echo(f"Error: Please provide a markdown file to process {hlp}", err=True)
        raise typer.Exit(code=1)

    file_path = pathlib.Path(file_name)
    if not file_path.exists():
        typer.echo(f"Error: File '{file_name}' does not exist.", err=True)
        raise typer.Exit(code=1)

    if output is not None:
        output_path = pathlib.Path(output)
        if output_path.resolve() == file_path.resolve():
            typer.echo(msg = f"Error: '{output}' and input '{file_name}' must differ.{hlp}", err=True)
            raise typer.Exit(code=1)

    return True

def handle_update_markdown_file(
        cfg: dict[str, Any],
        file_name: str | None = None,
        bold: str | None = None,
        auto_break: bool | None = None,
        vars_file: pathlib.Path | None = None,
) -> str:
    """Wrapper to call update_markdown_file using merged cfg."""
    file_name = file_name or cfg.get("file_name")
    bold = bold or cfg.get("bold_values")
    auto_break = auto_break if auto_break is not None else cfg.get("auto_break", False)
    vars_file = vars_file or cfg.get("vars_file")

    try:
        updated_content = update_markdown_file(file_name,
                                               bold,
                                               auto_break,
                                               cfg.get("output"),
                                               vars_file)
        typer.echo(f"File '{file_name}' updated successfully.", err=True)
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        updated_content = ""
    return updated_content


# ----------------------------
# CLI command
# ----------------------------

@app.command()
def convert(
    file_name: str = typer.Argument(
        None,
        help="The file to convert to Markdown (required unless specified in config)"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Output file. If not specified, prints to stdout or overwrites input file"
    ),
    bold_values: Optional[str] = typer.Option(
        None,
        "--bold", "-b",
        help="Comma-separated values to make bold (e.g., CSV headers)"
    ),
    auto_break: Optional[bool] = typer.Option(
        True,
        "--auto-break/--no-auto-break",
        help="Enable or disable automatic line breaks in CSV headers or long lines"
    ),
    plain: bool = typer.Option(
        False,
        "--plain",
        help="Output plain Markdown without Rich formatting"
    ),
    version: bool = typer.Option(
        False,
        "--version", "-V",
        callback=version_callback,
        help="Show the application version and exit"
    ),
    vars_file: pathlib.Path | None = typer.Option(
        None,
        "--vars", "-v",
        exists=True,
        file_okay=True,
        dir_okay=False,
        help="Path to JSON file with variable overrides"
    ),
    pyproject_dir: pathlib.Path | None = typer.Option(
        None,
        "--pyproject_dir", "-p",
        help="Directory to start searching for pyproject.toml (default: cwd, searches up the tree)"
    ),
    base_path: pathlib.Path | None = typer.Option(
        None,
        "--base_path",
        help="Root folder for project, used for locating JSON config and relative paths (default: cwd)"
    )
):
    """Convert a file to Markdown based on its extension, using merged configuration."""

    cfg = merge_config(
        file_name=file_name,
        output=output,
        bold_values=bold_values,
        auto_break=auto_break,
        vars_file=vars_file,
        plain=plain,
        base_path=base_path,
        pyproject_dir=pyproject_dir,
    )

    ensure_valid_args(cfg)
    markdown_text = handle_update_markdown_file(cfg)

    # Output
    out_file = cfg.get("output")
    if out_file:
        pathlib.Path(out_file).write_text(markdown_text, encoding="utf8")
        typer.echo(f"Markdown written to {out_file}", err=True)
    else:
        if markdown_text:
            if not cfg.get("plain"):
                console = Console()
                md = Markdown(markdown_text)
                console.print(md)
            else:
                typer.echo(markdown_text)
        else:
            typer.echo("An error occurred", err=True)


if __name__ == "__main__":
    app()
