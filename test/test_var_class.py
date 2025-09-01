import os
import tempfile
import json
import pytest
from mdfile.updater.variables import VariableReplacer

import pytest


FIELDS = [
    "name",
    "version",
    "summary",
    "author",
    "author_email",
    "license",
    "home_page",
    "requires_python",
    "keywords",
    "description_content_type",
    "project_url",
    "platform",
    "requires_dist",
    "classifier"
]


@pytest.mark.parametrize("field", FIELDS)
def test_default_matches_explicit(field):
    replacer = VariableReplacer()
    default_var = f"$meta.{field}"
    explicit_var = f"$meta.mdfile.{field}"

    def_val = replacer.update(f"{{{{{default_var}}}}}")
    exp_val = replacer.update(f"{{{{{explicit_var}}}}}")
    assert def_val == exp_val, f"Mismatch for field '{field}' vs default from meta"



def test_basic_replacement():
    replacer = VariableReplacer({"USER":"alice", "PROJECT":"pytest_demo"})
    content = "Hello {{$USER}}, project is {{$PROJECT}}."
    result = replacer.update(content)
    assert result == "Hello alice, project is pytest_demo."


def test_missing_variable():
    replacer = VariableReplacer()
    content = "Hello {{$MISSING}}!"
    result = replacer.update(content)
    assert "ERROR: Variable" in result


def test_sensitive_block():
    replacer = VariableReplacer()
    content = "API key: {{$API_KEY}}"
    result = replacer.update(content)
    assert "API key: ERROR: Variable" in result


def test_env_variable(monkeypatch ):
    monkeypatch.setenv("HOME", "/home/testuser")
    replacer = VariableReplacer()
    content = "Home dir: {{$ENV.HOME}}"
    result = replacer.update(content)
    assert result == "Home dir: /home/testuser"


def test_env_missing(monkeypatch, ):
    monkeypatch.delenv("NONEXISTENT", raising=False)
    replacer = VariableReplacer()
    content = "Variable {{$ENV.NONEXISTENT}}"
    result = replacer.update(content)
    assert "ERROR: Variable" in result



import pytest

def test_spacing_variations_parametric():
    replacer = VariableReplacer(extra_vars={"USER": "alice", "PROJECT": "pytest_demo"})

    test_cases = [
        # USER variations
        ("Hello {{$USER}}!", "Hello alice!", "no extra spacing"),
        ("Hello {{   $USER}}!", "Hello alice!", "leading spaces before var"),
        ("Hello {{$USER   }}!", "Hello alice!", "trailing spaces after var"),
        ("Hello {{   $USER   }}!", "Hello alice!", "both leading and trailing spaces"),
        ("Hello {{\t$USER}}!", "Hello alice!", "leading tab before var"),
        ("Hello {{$USER\t}}!", "Hello alice!", "trailing tab after var"),
        ("Hello {{\t$USER\t}}!", "Hello alice!", "tabs around var"),

        # PROJECT variations
        ("Hi {{$PROJECT}}!", "Hi pytest_demo!", "no extra spacing project"),
        ("Hi {{   $PROJECT   }}!", "Hi pytest_demo!", "spaces around project"),
        ("Hi {{\t$PROJECT\t}}!", "Hi pytest_demo!", "tabs around project"),

        # Both variables together
        (
            "User={{   $USER   }}, Project={{\t$PROJECT\t}}",
            "User=alice, Project=pytest_demo",
            "multiple variables with mixed spacing"
        ),
    ]

    @pytest.mark.parametrize("content,expected,desc", test_cases)
    def _run(content: str, expected: str, desc: str) -> None:
        result = replacer.update(content)
        assert result == expected, f"Failed: {desc}"

    for content, expected, desc in test_cases:
        _run(content, expected, desc)

def test_no_vars_file():
    replacer = VariableReplacer()
    content = "Missing {{$VAR}}"
    result = replacer.update(content)
    assert "ERROR: Variable" in result



@pytest.mark.parametrize(
    "content, setup_vars, expected, description",
    [
        # Single variable replacement
        ("Hello {{$USER}}", {"USER": "Chuck"}, "Hello Chuck",
         "Single variable replacement from vars dict"),

        # Multiple replacements of same variable
        ("{{$GREETING}}, {{$GREETING}}!", {"GREETING": "Hi"}, "Hi, Hi!",
         "Multiple replacements of the same variable"),

        # Empty string replacement
        ("Value is {{$EMPTY}}.", {"EMPTY": ""}, "Value is .",
         "Variable with empty string replacement"),

        # Case sensitivity: variable missing due to lowercase key
        ("Hi {{$user}}", {"USER": "Chuck"}, "Hi (ERROR: Variable `user` not found)",
         "Variable names are case sensitive, lowercase mismatch triggers error"),

        # Multiple different variables
        ("{{$A}} + {{$B}} = {{$C}}", {"A": "1", "B": "2", "C": "3"}, "1 + 2 = 3",
         "Multiple distinct variables replaced correctly"),
    ]
)
def test_variable_replacements(content, setup_vars, expected, description):
    replacer = VariableReplacer(extra_vars=setup_vars)
    result = replacer.update(content)
    assert result == expected, f"Test failed: {description}. Got '{result}'"
