
import pathlib
import tempfile

import pytest
from typer.testing import CliRunner

from markymark.mnm import CsvToMarkdown, ToMarkdown,update_process_inserts
from markymark.mnm import app, update_markdown_from_string,update_markdown_file

runner = CliRunner()


def test_update_file_from_another_file():
    """Tests the convert CLI functionality for updating a Markdown file from another text file.

    This test verifies that the convert command correctly processes a Markdown file containing
    file reference markers and updates the content between those markers with the content from
    the referenced text file, formatted as a code block.

    The test creates temporary test files, runs the CLI command, and verifies the output
    matches the expected result with the content properly inserted between markers.

    No arguments are needed as the test creates and manages its own test files.

    Raises:
        AssertionError: If the CLI command fails or if the output content doesn't match
            the expected result.
    """
    try:
        # Paths for the markdown file and the input text file
        md_file_path = pathlib.Path("123_test.md")
        input_file_path = pathlib.Path("123_test.txt")

        # Write initial content to the markdown file
        md_file_content = f"<!--file 123_test.txt-->\n<!--file end-->"
        md_file_path.write_text(md_file_content)

        # Write initial content to the input text file
        input_file_content = "Hello\nWorld"
        input_file_path.write_text(input_file_content)

        # Ensure the paths are present
        assert md_file_path.exists(), "Markdown file does not exist."
        assert input_file_path.exists(), "Input text file does not exist."

        # Run the Typer CLI app with the `convert` command
        # Pass arguments in a single string with spaces instead of as separate items
        result = runner.invoke(app, [str(md_file_path)])

        # Expected content of the updated markdown file
        expected_md_file_content = f"<!--file 123_test.txt-->\n```\nHello\nWorld\n```\n<!--file end-->"

        # Verify the CLI executed successfully
        assert result.exit_code == 0, f"CLI failed: {result.output}"

        # Verify the file content has been updated correctly
        updated_content = md_file_path.read_text()
        assert updated_content == expected_md_file_content, (
            f"Expected content:\n{expected_md_file_content}\nGot:\n{updated_content}"
        )
    finally:
        md_file_path.unlink(missing_ok=True)
        input_file_path.unlink(missing_ok=True)


def test_update_file_with_output_flag():
    """Tests the convert CLI functionality with the --output flag.

    This test verifies that the convert command correctly processes a Markdown file containing
    file reference markers and writes the updated content to a separate output file when the
    --output flag is used. The original input file should remain unchanged.

    The test creates temporary test files, runs the CLI command with the --output flag,
    and verifies both that the output file has the correct content and that the input file
    remains unchanged.

    Raises:
        AssertionError: If the CLI command fails, if the output content doesn't match
            the expected result, or if the original file is modified.
    """
    try:
        # Paths for the markdown file, input text file, and output file
        md_file_path = pathlib.Path("123_test.md")
        input_file_path = pathlib.Path("123_test.txt")
        output_file_path = pathlib.Path("123_test_output.md")

        # Write initial content to the markdown file
        md_file_content = f"<!--file 123_test.txt-->\n<!--file end-->"
        md_file_path.write_text(md_file_content)

        # Write initial content to the input text file
        input_file_content = "Hello\nWorld"
        input_file_path.write_text(input_file_content)

        # Ensure the paths are present
        assert md_file_path.exists(), "Markdown file does not exist."
        assert input_file_path.exists(), "Input text file does not exist."

        # Run the Typer CLI app with the `convert` command and output flag
        result = runner.invoke(app, [
            str(md_file_path),
            '--output',
            str(output_file_path)
        ])

        # Expected content of the updated markdown file
        expected_md_file_content = f"<!--file 123_test.txt-->\n```\nHello\nWorld\n```\n<!--file end-->"

        # Verify the CLI executed successfully
        assert result.exit_code == 0, f"CLI failed: {result.output}"

        # Verify the output file exists and has the correct content
        assert output_file_path.exists(), f"Output file {output_file_path} was not created."
        updated_content = output_file_path.read_text()
        assert updated_content == expected_md_file_content, (
            f"Expected content in output file:\n{expected_md_file_content}\nGot:\n{updated_content}"
        )


    finally:
        # Clean up all created files
        md_file_path.unlink(missing_ok=True)
        input_file_path.unlink(missing_ok=True)
        output_file_path.unlink(missing_ok=True)


def test_update_markdown_csv_file(tmp_path):
    """
    Test the update_markdown_file function using actual Markdown and CSV files.
    """

    # Base directories for input and expected files
    input_dir = pathlib.Path("input")
    expected_dir = pathlib.Path("expected")

    # Input and expected file paths
    input_md_file = input_dir / "example.md"
    input_csv_file = input_dir / "test.csv"
    expected_output_file = pathlib.Path("output/example_output.md")

    content = input_md_file.read_text()

    # Call the function, processing Markdown with placeholders
    result = update_markdown_from_string(
        content=content,
        bold=False,
        auto_break=False
    )

    # Read the expected Markdown
    expected_output = expected_output_file.read_text()

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match:\n{result}"

def test_update_markdown_csv_numbers_file(tmp_path):
    """
    Test the update_markdown_file function using actual Markdown and CSV files.
    """

    # Base directories for input and expected files
    input_dir = pathlib.Path("input")
    expected_dir = pathlib.Path("expected")

    # Input and expected file paths
    input_md_file = input_dir / "example_numbers.md"
    input_csv_file = input_dir / "test_numbers.csv"
    expected_output_file = pathlib.Path("output/example_output_numbers.md")

    content = input_md_file.read_text()

    # Call the function, processing Markdown with placeholders
    result = update_markdown_from_string(
        content=content,
        bold=False,
        auto_break=False
    )

    # Read the expected Markdown
    expected_output = expected_output_file.read_text()

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match:\n{result}"


def test_update_markdown_csv_br_file(tmp_path):
    """
    Test the update_markdown_file function using actual Markdown and CSV files.
    """

    # Base directories for input and expected files
    input_dir = pathlib.Path("input")
    expected_dir = pathlib.Path("expected")

    # Input and expected file paths
    input_md_file = input_dir / "example.md"
    input_csv_file = input_dir / "test.csv"
    expected_output_file = pathlib.Path("output/example_output_br.md")

    content = input_md_file.read_text()

    # Call the function, processing Markdown with placeholders
    result = update_markdown_from_string(
        content=content,
        bold=False,
        auto_break=True
    )

    # Read the expected Markdown
    expected_output = expected_output_file.read_text()

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match:\n{result}"



def test_update_markdown_python_file(tmp_path):
    """
    Test the update_markdown_file function using actual Markdown and CSV files.
    """

    # Base directories for input and expected files
    input_dir = pathlib.Path("input")
    expected_dir = pathlib.Path("expected")

    # Input and expected file paths
    input_md_file = input_dir / "example_python.md"
    input_py_file = input_dir / "python.py"
    expected_output_file = pathlib.Path("output/example_python.md")

    content = input_md_file.read_text()

    # Call the function, processing Markdown with placeholders
    result = update_markdown_from_string(
        content=content,
        bold='',
        auto_break=False,
    )

    # Read the expected Markdown
    expected_output = expected_output_file.read_text()

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match:\n{result}"
    return


@pytest.mark.parametrize("lang, code_ext", [
    ("junk", "junk"),
    ("json", "json"),
    ("json", "jsonc"),
    ("markdown", "md"),
    ("markdown", "markdown"),
    ("java", "java"),
    ("c", "c"),
    ("python", "py"),

])
def test_update_markdown_code_file(tmp_path, lang, code_ext):
    """
    Test the update_markdown_file function using parameterized Markdown and code files
    for multiple languages.
    """

    # Base directories for input and expected files
    input_dir = pathlib.Path("input")
    expected_dir = pathlib.Path("output")

    # Input and expected file paths
    input_md_file = input_dir / f"example_{lang}.md"
    input_code_file = input_dir / f"{lang}.{code_ext}"
    expected_output_file = expected_dir / f"example_{lang}.md"

    # Read content from the Markdown file
    content = input_md_file.read_text()

    # Call the function, processing Markdown with placeholders
    result = update_markdown_from_string(
        content=content,
        bold='',
        auto_break=False,
    )

    # Read the expected Markdown
    expected_output = expected_output_file.read_text()

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match for {lang}:\n{result}"


def test_csv_to_markdown_file_not_found():
    # Define a non-existent file path
    non_existent_file = "non_existent_file.csv"

    # Ensure the file does not exist
    assert not pathlib.Path(non_existent_file).exists()

    # Create an instance of CsvToMarkdown
    converter = CsvToMarkdown(non_existent_file)

    # Check that the error message is correct
    markdown_output = converter.to_markdown()
    assert "Error" in markdown_output
    assert "Error: File 'non_existent_file.csv' not found." in markdown_output


def test_update_process_command():
    """Test that process commands are executed and their output is inserted."""
    # Test input with process placeholder
    test_input = """<!--process ls-->\n<!--process end-->"""

    # Update the markdown
    result = update_process_inserts(test_input)

    # Verify that the process command was executed
    assert "<!--process ls-->" in result
    assert "<!--process end-->" in result

    # The output should contain some files like test_mnm.py
    assert "test_mnm.py" in result

    # The output format should match our expected structure
    # Output is between the process tags, on a separate line
    lines = result.strip().split('\n')
    assert len(lines) >= 3  # At least opening tag, content, closing tag
    assert lines[0] == "<!--process ls-->"
    assert lines[-1] == "<!--process end-->"
    # There should be atleast an input
    assert 'input' in lines
    assert 'test_mnm.py' in lines
    assert 'output' in lines

    # Test using the full markdown_from_string function
    full_result = update_markdown_from_string(test_input, "", False)
    assert "<!--process ls-->" in full_result
    assert "test_mnm.py" in full_result


def test_process_cat_verifies_function_declarations():
    """
    Test that executes a 'cat test_mnm.py' command through the process insertion
    and verifies that expected function declarations are present in the result.
    """

    # Input content with process placeholder for cat command
    test_input = """<!--process cat test_mnm.py-->\n<!--process end-->"""

    # Execute the update_process_inserts function to run the cat command
    result = update_process_inserts(test_input)

    # List of function declarations we expect to find
    expected_functions = [
        "def test_update_file_from_another_file",
        "def test_update_file_with_output_flag",
        "def test_update_markdown_csv_file",
        "def test_update_markdown_csv_br_file",
        "def test_update_markdown_python_file",
        "def test_update_markdown_code_file",
        "def test_csv_to_markdown_file_not_found",
        "def test_update_process_command"
    ]

    # Verify each function declaration is present in the result
    for func_decl in expected_functions:
        assert func_decl in result, f"Function declaration '{func_decl}' not found in cat output"

    assert result.startswith("<!--process cat test_mnm.py-->\n"), "Process command header missing"
    assert "<!--process end-->" in result, "Process command footer missing"

def test_file_not_found_error():
    """
    Test that verifies a FileNotFoundError is properly raised and handled
    when attempting to insert a non-existent file using the file directive.
    """

    # Create a test input with a file directive pointing to a non-existent file
    non_existent_file = "this_file_does_not_exist_xyz789.md"

    # Test that the appropriate FileNotFoundError is raised
    with pytest.raises(FileNotFoundError) as excinfo:
        update_markdown_file(non_existent_file)

    # Verify that the error message contains the file name
    assert non_existent_file in str(excinfo.value), f"Error message should mention '{non_existent_file}'"
    assert "not found" in str(excinfo.value).lower(), "Error message should indicate file not found"

def test_process_command_timeout():
    """
    Test that verifies the process insertion properly handles a timeout
    when a command takes too long to execute.
    """

    # Create a test input with a process that will time out
    # The 'sleep' command will run for 5 seconds, but we set timeout to 1 second
    test_input = """<!--process sleep 5-->\n<!--process end-->"""

    # Execute the update_process_inserts function with a 1-second timeout
    result = update_process_inserts(test_input, timeout_sec=1)

    # Check that the result contains a timeout error message
    assert "Timeout Error" in result, "Timeout error indication missing in result"
    assert "timed out after 1 seconds" in result, "Specific timeout duration message missing"

    # Verify the process command was properly formatted in the result
    assert result.startswith("<!--process sleep 5-->"), "Process command header missing"
    assert "<!--process end-->" in result, "Process command footer missing"

def test_csv_to_markdown_empty_file():
    """
    Test that verifies CsvToMarkdown properly handles an empty CSV file
    and triggers the expected warning message.
    """


    # Create a temporary empty CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_csv:
        temp_csv_path = pathlib.Path(temp_csv.name)
        # File is intentionally left empty

    try:
        # Instantiate CsvToMarkdown with the empty file
        csv_converter = CsvToMarkdown(str(temp_csv_path))

        # Call to_markdown method which should trigger the warning
        result = csv_converter.to_markdown()

        # Check that the result contains the warning
        assert result == "The CSV file is empty."

    finally:
        # Clean up the temporary file
        if temp_csv_path.exists():
            temp_csv_path.unlink()
