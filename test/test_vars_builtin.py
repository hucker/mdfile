import importlib
import datetime as dt
import json
import pytest

from mdfile.md_updater import update_markdown_from_string

@pytest.mark.parametrize(
    "template, expected",
    [
        ("{{$version}}", importlib.metadata.version("mdfile")),  # Test for {{$version}}
        ("{{$date}}", dt.datetime.now().strftime("%Y-%m-%d")),  # Test for {{$date}}
        (       "Version: {{$version}}, Date: {{$date}}",
                f"Version: {importlib.metadata.version('mdfile')}, Date: {dt.datetime.now().strftime('%Y-%m-%d')}",
        ),
    ],
)
def test_var_version(template, expected):
    result = update_markdown_from_string(template, "", False)
    assert result == expected

def test_var_with_json_override(tmp_path):
    # Create a temporary vars.json file
    json_vars = {"project": "CoolApp", "name": "OverriddenName"}
    vars_file = tmp_path / "vars.json"
    vars_file.write_text(json.dumps(json_vars), encoding="utf8")

    template = "Project: {{$project}}, Name: {{$name}}, Date: {{$date}}"
    result = update_markdown_from_string(template, "", False, vars_file=str(vars_file))

    # Built-in 'date' stays, JSON adds 'project', JSON overrides 'name'
    expected_date = dt.datetime.now().strftime("%Y-%m-%d")
    assert f"Project: {json_vars['project']}" in result
    assert f"Name: {json_vars['name']}" in result
    assert f"Date: {expected_date}" in result



