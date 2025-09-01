#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["typer","rich"]
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

import sys
import json
import os
import pathlib
from importlib.metadata import version
from typing import Optional, Any, Dict

import typer
from rich.console import Console
from rich.markdown import Markdown
from md_updater import update_markdown_file

# tomllib fallback for Python 3.10
if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

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
    if pyproject_file is None or not pyproject_file.exists():
        return {}
    with pyproject_file.open("rb") as f:
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


def merge_config_dicts(
    *,
    cli: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    toml: dict[str, Any] | None = None,
    env: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge configuration from named sources.

    Later sources overwrite earlier ones. None values are skipped.
    Precedence: defaults → json → toml → env → cli
    """
    cfg: dict[str, Any] = DEFAULT_CONFIG.copy()
    sources = [json, toml, env, cli]

    for source in sources:
        if source:
            for key, value in source.items():
                if value is not None:
                    cfg[key] = value

    return cfg


def merge_config_files(
    *,
    file_name: str | None = None,
    output: str | None = None,
    plain: bool | None = None,
    no_json: bool = False,
    no_pyproject: bool = False,
    no_env: bool = False,
) -> dict[str, Any]:
    """Merge configuration from files, environment, and CLI args."""
    json_cfg = {} if no_json else load_json_config()
    toml_cfg = {} if no_pyproject else load_pyproject_config()
    env_cfg = {} if no_env else load_env_config()
    cli_cfg = {"file_name": file_name, "output": output, "plain": plain}

    return merge_config_dicts(
        cli=cli_cfg,
        json=json_cfg,
        toml=toml_cfg,
        env=env_cfg,
    )



# ----------------------------
# Argument validation
# ----------------------------

def validate_args(
    file_name: str | None,
    output: str | None,
) -> bool:
    """Validate command arguments and exit with error if invalid."""
    hlp = "(--help for details)"
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
            typer.echo(f"Error: '{output}' and input '{file_name}' must differ. {hlp}", err=True)
            raise typer.Exit(code=1)

    return True


def validate_args_expanded(cfg: dict[str, Any]) -> bool:
    """Expanded version accepting full config dict."""
    return validate_args(
        file_name=cfg.get("file_name"),
        output=cfg.get("output"),
    )


# ----------------------------
# Markdown processing
# ----------------------------

def transform_markdown_file(
        file_name: str,
        output: str | None = None,
        bold_values: str | None = None,
        auto_break: bool = True,
) -> str:
    """Process a file using update_markdown_file with explicit arguments."""
    try:
        updated_content = update_markdown_file(file_name, bold_values, auto_break, output)
        typer.echo(f"File '{file_name}' updated successfully.", err=True)
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        updated_content = ""
    return updated_content


def transform_markdown_file_expanded(cfg: dict[str, Any]) -> str:
    """Process a file using update_markdown_file with full config dict."""
    return transform_markdown_file(
        file_name=cfg.get("file_name"),
        output=cfg.get("output"),
        bold_values=cfg.get("bold_values"),
        auto_break=cfg.get("auto_break", True),
    )


# ----------------------------
# CLI command
# ----------------------------

@app.command()
def convert(
    file_name: str = typer.Argument(None, help="The file to convert to Markdown (required unless in config)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file or stdout"),
    plain: bool = typer.Option(False, "--plain", help="Output plain Markdown without Rich formatting"),
    version: bool = typer.Option(False, "--version", "-V", callback=version_callback, help="Show version"),
    no_json: bool = typer.Option(False, "--no_json", help="Disable loading mdfile.json"),
    no_pyproject: bool = typer.Option(False, "--no_pyproject", help="Disable loading pyproject.toml"),
    no_env: bool = typer.Option(False, "--no_env", help="Disable loading environment variables"),
):
    """Convert a file to Markdown using merged configuration."""

    cfg = merge_config_files(
        file_name=file_name,
        output=output,
        plain=plain,
        no_json=no_json,
        no_pyproject=no_pyproject,
        no_env=no_env,
    )

    validate_args_expanded(cfg)
    markdown_text = transform_markdown_file_expanded(cfg)

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
