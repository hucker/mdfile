import datetime as dt
import json
import pathlib
from importlib.metadata import version

from .dotted_dict import DottedDict


def load_vars(vars_file: str | None) -> DottedDict:
    """
    Load variables from built-in defaults and optional JSON file overrides.

    Built-in defaults include version, name, date, and time. If a JSON file is
    provided, its top-level keys override the defaults. The returned DottedDict
    allows convenient dotted-key lookup for top-level or nested keys, e.g.,
    `vars["foo.bar"]` will resolve to `vars["foo"]["bar"]` without changing
    the underlying dictionary structure.

    Note:
        - Only lookup is dotted; nested dictionaries themselves remain normal dicts.
        - Setting values using dotted keys is not supported.

    Args:
        vars_file (str | None): Path to JSON file containing variable overrides.

    Returns:
        DottedDict: Merged variables with convenient dotted-key lookup.
    """
    base_vars: dict[str, str] = {
        "version": version("mdfile"),
        "name": "mdfile",
        "date": dt.datetime.now().strftime("%Y-%m-%d"),
        "time": dt.datetime.now().strftime("%H:%M:%S"),
    }

    if vars_file:
        path = pathlib.Path(vars_file)
        if path.exists():
            with path.open("r", encoding="utf8") as f:
                try:
                    user_vars = json.load(f)
                    if not isinstance(user_vars, dict):
                        raise ValueError(
                            "JSON vars file must contain an object at top level."
                        )
                    base_vars.update(user_vars)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in {vars_file}: {e}")

    return DottedDict(base_vars)



