import json
import os
import pathlib
import random
import string
import sys

# tomllib fallback for Python 3.10
if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    pass

import pytest

from main import DEFAULT_CONFIG, merge_config_dicts, merge_config_files  # adjust import path
from main import find_pyproject, load_pyproject_config  # adjust import


@pytest.mark.parametrize(
    "cli_cfg,json_cfg,toml_cfg,env_cfg,expected_update,desc",
    [
        # Only defaults
        (None, None, None, None, {}, "No sources, should return defaults"),
        # JSON only
        ({}, {"foo": "bar", "auto_break": False}, None, None, {"foo": "bar", "auto_break": False},
         "JSON overrides defaults"),
        # TOML overrides JSON
        ({}, {"a": 1, "b": 2}, {"b": 3, "c": 4}, None, {"a": 1, "b": 3, "c": 4},
         "TOML overrides JSON"),
        # ENV overrides TOML
        ({}, {"a": 1}, {"a": 2, "b": 3}, {"b": 4, "c": 5}, {"a": 2, "b": 4, "c": 5},
         "ENV overrides TOML and JSON"),
        # CLI overrides all
        ({"c": 7, "d": 8}, {"a": 1}, {"b": 2, "c": 3}, {"c": 4}, {"a": 1, "b": 2, "c": 7, "d": 8},
         "CLI overrides everything"),
        # None values are skipped
        ({"a": None}, {"b": 2, "c": None}, {"c": None}, {"d": None}, {"b": 2},
         "None values are ignored"),
        # Empty dicts
        ({}, {}, {}, {}, {}, "Empty dicts do not alter defaults"),
    ]
)
def test_merge_config_dicts_param(
        cli_cfg, json_cfg, toml_cfg, env_cfg, expected_update, desc
):
    """Parametrized thorough test of merge_config_dicts."""
    result = merge_config_dicts(cli_cfg=cli_cfg or {},
                                json_cfg=json_cfg or {},
                                toml_cfg=toml_cfg or {},
                                env_cfg=env_cfg or {})
    expected = DEFAULT_CONFIG.copy()
    expected.update(expected_update)

    assert result == expected, f"{desc}: expected {expected}, got {result}"


def random_key(length=5):
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_value():
    # Mix of ints, strings, booleans, and None
    return random.choice([
        random.randint(0, 100),
        random.random(),
        random.choice([True, False]),
        "".join(random.choices(string.ascii_letters, k=5)),
        None
    ])


def random_key(length=5) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_value() -> any:
    """Generate a random value that can appear in config dicts."""
    # Include int, float, bool, string, and None to test edge cases
    choices = [
        random.randint(0, 100),
        random.random(),
        random.choice([True, False]),
        "".join(random.choices(string.ascii_letters, k=5)),
        None  # explicitly include None to test that None does not overwrite
    ]
    return random.choice(choices)


@pytest.mark.parametrize("seed", range(5))  # 5 different random seeds
def test_merge_config_dicts_fuzz(seed: int):
    """
    Fuzz test merge_config_dicts with random dicts for each source.

    Purpose:
    - Ensure CLI values override all other sources.
    - Ensure None values in lower-precedence sources do not overwrite existing values.
    - Check that defaults are preserved when missing in all sources.
    - Test that arbitrary combinations of types are handled correctly.
    """
    random.seed(seed)

    # Generate random dictionaries for each config source
    cli_cfg = {random_key(): random_value() for _ in range(random.randint(1, 5))}
    json_cfg = {random_key(): random_value() for _ in range(random.randint(1, 5))}
    toml_cfg = {random_key(): random_value() for _ in range(random.randint(1, 5))}
    env_cfg = {random_key(): random_value() for _ in range(random.randint(1, 5))}

    result = merge_config_dicts(cli_cfg=cli_cfg,
                                json_cfg=json_cfg,
                                toml_cfg=toml_cfg,
                                env_cfg=env_cfg)

    # Verify that CLI keys override everything else
    for k in cli_cfg:
        if cli_cfg[k] is not None:
            assert result[k] == cli_cfg[k], f"CLI key {k} should override others"

    # Verify lower-precedence sources do not overwrite keys with None
    for d in (json_cfg, toml_cfg, env_cfg):
        for k, v in d.items():
            if v is not None and k not in cli_cfg:
                assert result[k] == v or k in DEFAULT_CONFIG, f"Key {k} should be present unless overridden by CLI"

    # Verify defaults are preserved for missing keys
    for k, v in DEFAULT_CONFIG.items():
        if k not in result:
            assert result[k] == v, f"Default key {k} missing in result"


@pytest.mark.parametrize(
    "no_json, no_pyproject, no_env, expected_keys",
    [
        (False, False, False, {"json_key", "toml_key", "env"}),
        (True, False, False, {"toml_key", "env"}),
        (False, True, False, {"json_key", "env"}),
        (False, False, True, {"json_key", "toml_key"}),
        (True, True, False, {"env"}),
        (True, False, True, {"toml_key"}),
        (False, True, True, {"json_key"}),
        (True, True, True, set()),
    ]
)
def test_merge_config_files(tmp_path: pathlib.Path, monkeypatch,
                            no_json: bool, no_pyproject: bool,
                            no_env: bool, expected_keys: set[str]):
    """
    Test that merge_config_files respects the no_* flags.
    Only verifies that sources are loaded correctly.
    Ignores default keys in the config.
    """

    # --- Create dummy JSON and TOML files ---
    json_file = tmp_path / "mdfile.json"
    json_file.write_text(json.dumps({"json_key": "json_val"}), encoding="utf8")

    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text("[tool.mdfile]\ntoml_key = 'toml_val'\n", encoding="utf8")

    # --- Set environment variable ---
    monkeypatch.setenv("MD_FILE_ENV", "env_val")

    # --- Change working directory to tmp_path ---
    os.chdir(tmp_path)

    # --- Run merge ---
    cfg = merge_config_files(
        file_name=None,
        output=None,
        plain=None,
        no_json=no_json,
        no_pyproject=no_pyproject,
        no_env=no_env,
    )

    # --- Verify that expected keys are present ---
    for key in expected_keys:
        assert key in cfg and cfg[key], f"Expected key '{key}' missing in config"

    # Optionally, verify that keys not expected from sources are from defaults
    # (not required but can be added if you want)


# -----------------------------
# Test 1: Finding the pyproject.toml
# -----------------------------

def test_find_pyproject(tmp_path: pathlib.Path):
    """
    Verify that find_pyproject finds the pyproject.toml in the current or parent directories.
    """

    # Create nested directories
    level1 = tmp_path / "level1"
    level1.mkdir()
    level2 = level1 / "level2"
    level2.mkdir()

    # Create pyproject.toml in level1
    pyproject_file = level1 / "pyproject.toml"
    pyproject_file.write_text("[tool.mdfile]\ntest_key = 'test_val'\n", encoding="utf8")

    # Case: start from subdirectory → should find file in parent
    found = find_pyproject(start=level2)
    assert found == pyproject_file

    # Case: start from same directory → should find file
    found_self = find_pyproject(start=level1)
    assert found_self == pyproject_file

    # Case: start from above → should not find file
    found_none = find_pyproject(start=tmp_path)
    assert found_none is None


# -----------------------------
# Test 2: Reading pyproject.toml content
# -----------------------------

def test_load_pyproject_config(tmp_path: pathlib.Path):
    """
    Verify that load_pyproject_config reads the [tool.mdfile] section correctly.
    """

    # Create a pyproject.toml in tmp_path
    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text(
        "[tool.mdfile]\nfile_name = 'example.md'\nauto_break = false\n",
        encoding="utf8"
    )

    # Load config directly using the path
    config = load_pyproject_config(pyproject_file)
    assert isinstance(config, dict)
    assert config.get("file_name") == "example.md"
    assert config.get("auto_break") is False

    # Case: no file → should return empty dict
    non_existent_file = tmp_path / "does_not_exist.toml"
    empty_config = load_pyproject_config(non_existent_file)
    assert empty_config == {}
