import os
import tempfile
import json
import pytest
from mdfile.updater.variables import VariableReplacer


@pytest.fixture
def vars_file():
    """Create a temporary JSON vars file."""
    data = {"USER": "alice", "PROJECT": "pytest_demo", "API_KEY": "12345"}
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as f:
        json.dump(data, f)
        f.flush()
        yield f.name
    os.unlink(f.name)


def test_basic_replacement(vars_file):
    replacer = VariableReplacer(vars_file)
    content = "Hello {{$USER}}, project is {{$PROJECT}}."
    result = replacer.update(content)
    assert result == "Hello alice, project is pytest_demo."


def test_missing_variable(vars_file):
    replacer = VariableReplacer(vars_file)
    content = "Hello {{$MISSING}}!"
    result = replacer.update(content)
    assert "ERROR: Variable" in result


def test_sensitive_block(vars_file):
    replacer = VariableReplacer(vars_file)
    content = "API key: {{$API_KEY}}"
    result = replacer.update(content)
    assert "API key: ERROR: Variable" in result


def test_env_variable(monkeypatch, vars_file):
    monkeypatch.setenv("HOME", "/home/testuser")
    replacer = VariableReplacer(vars_file)
    content = "Home dir: {{$ENV.HOME}}"
    result = replacer.update(content)
    assert result == "Home dir: /home/testuser"


def test_env_missing(monkeypatch, vars_file):
    monkeypatch.delenv("NONEXISTENT", raising=False)
    replacer = VariableReplacer(vars_file)
    content = "Variable {{$ENV.NONEXISTENT}}"
    result = replacer.update(content)
    assert "ERROR: Variable" in result



def test_spacing_variations(vars_file):
    replacer = VariableReplacer(vars_file)
    content = "Hello {{ $USER }} and {{   $PROJECT   }}!"
    result = replacer.update(content)
    assert result == "Hello alice and pytest_demo!"


def test_no_vars_file():
    replacer = VariableReplacer(None)
    content = "Missing {{$VAR}}"
    result = replacer.update(content)
    assert "ERROR: Variable" in result

