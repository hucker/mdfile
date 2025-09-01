import pytest
import textwrap
from updater.process import ProcessReplacer,ProcessBlockReplacer
from updater.process import ShellBlockReplacer,ShellReplacer




def test_update_process_command():
    """Test that process commands are executed and their output is inserted."""
    # Test input with process placeholder
    test_input = """<!--process ls-->\n<!--process end-->"""

    # Update the markdown
    pbr = ProcessBlockReplacer()
    result = pbr.update(test_input)

    # Verify that the process command was executed
    assert "<!--process ls-->" in result
    assert "<!--process end-->" in result

    # The output format should match our expected structure
    # Output is between the process tags, on a separate line
    lines = result.strip().split('\n')
    assert len(lines) >= 3  # At least opening tag, content, closing tag
    assert lines[0] == "<!--process ls-->"
    assert lines[-1] == "<!--process end-->"
    # There should be atleast an input.  This is pretty crude in that it just checks that
    # some "stuff" is in the output rather than the exact "stuff"
    assert 'mdfile.json' in lines



def test_process_cat_verifies_function_declarations(tmp_path):
    """
    Test that executes a 'cat <tempfile>' command through the process insertion
    and verifies that expected function declarations are present in the result.
    """
    # Create a temporary Python file with known content
    test_file = tmp_path / "test_mnm.py"
    file_content = textwrap.dedent("""
        def test_update_file_from_another_file(): pass
        def test_update_file_with_output_flag(): pass
        def test_update_markdown_csv_file(): pass
        def test_update_markdown_csv_br_file(): pass
        def test_update_markdown_python_file(): pass
        def test_update_markdown_code_file(): pass
        def test_csv_to_markdown_file_not_found(): pass
        def test_update_process_command(): pass
    """).strip()
    test_file.write_text(file_content)

    # Input content with process placeholder for cat command
    test_input = f"<!--process cat {test_file}-->\n<!--process end-->"

    # Run the ProcessBlockReplacer
    pbr = ProcessBlockReplacer()
    result = pbr.update(test_input)

    # Verify each expected function declaration is present in the output
    expected_functions = [
        "def test_update_file_from_another_file",
        "def test_update_file_with_output_flag",
        "def test_update_markdown_csv_file",
        "def test_update_markdown_csv_br_file",
        "def test_update_markdown_python_file",
        "def test_update_markdown_code_file",
        "def test_csv_to_markdown_file_not_found",
        "def test_update_process_command",
    ]
    for func_decl in expected_functions:
        assert func_decl in result, f"Function declaration '{func_decl}' not found in cat output"

    # Verify placeholder structure is intact
    assert result.startswith(f"<!--process cat {test_file}-->\n")
    assert "<!--process end-->" in result



def test_process_replacer_cat(tmp_path):
    """
    Test that executes a '{{process cat <file>}}' placeholder and verifies
    that the expected content from the file appears in the output.
    """
    # Create a temporary file with known content
    test_file = tmp_path / "test_file.py"
    file_content = textwrap.dedent("""
        def foo(): pass
        def bar(): pass
        def baz(): pass
    """).strip()
    test_file.write_text(file_content)

    # Input content with the process placeholder
    test_input = f"{{{{process cat {test_file}}}}}"

    # Create the replacer and update the content
    replacer = ProcessReplacer(timeout_sec=5)
    result = replacer.update(test_input)

    # Verify each function declaration appears in the output
    expected_functions = ["def foo", "def bar", "def baz"]
    for func_decl in expected_functions:
        assert func_decl in result, f"Expected '{func_decl}' in output"

    # Verify the output is wrapped in a code block
    assert result.startswith("```text\n")
    assert result.endswith("```\n") or result.endswith("```")



@pytest.mark.parametrize(
    "cls,test_input",
    [
        (
            ProcessBlockReplacer,
            """<!--process sleep 5-->\n<!--process end-->"""
        ),
        (
            ProcessReplacer,
            r"""{{process sleep 5}}"""
        ),
        (
                ShellBlockReplacer,
                """<!--shell sleep 5-->\n<!--shell end-->"""
        ),
        (
                ShellReplacer,
                r"""{{shell sleep 5}}"""
        ),
    ],
)
def test_process_command_timeout(cls, test_input):
    """
    Verify process insertion handles timeout errors for different replacer classes.
    """

    # Run update with a short timeout so the sleep triggers failure
    result = cls(timeout_sec=1).update(content=test_input)

    # Common assertions
    assert "Timeout Error" in result, "Timeout error indication missing in result"
    assert "timed out after 1 seconds" in result, "Specific timeout duration missing"
    assert True


@pytest.mark.parametrize(
    "replacer_class, placeholder, expected",
    [
        (
                ShellReplacer,
                "{{shell echo hello}}\n",
                "```bash\n>> echo hello\nhello\n\n```\n",
        ),
        (
                ShellBlockReplacer,
                "<!--shell echo hello-->\nold stuff\n<!--shell end-->\n",
                "<!--shell echo hello-->\n```bash\n>> echo hello\nhello\n\n```\n<!--shell end-->\n",
        ),
    ],
)
def test_shell_replacers_basic_output(replacer_class, placeholder, expected):
    """
    Test that shell-style process replacers correctly format simple output.

    NOTE: This test is tricky to get just right because of the \n's.

    """
    replacer = replacer_class(timeout_sec=5)  # short timeout for test
    result = replacer.update(placeholder)

    # Check that the output starts with the expected shell block prefix
    assert result == expected


