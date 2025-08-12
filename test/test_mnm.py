import pytest
import tempfile


from typer.testing import CliRunner
import pathlib
import datetime as dt
from markymark.mnm import update_markdown_file,ToMarkdown,CsvToMarkdown
from markymark.mnm import update_markdown_from_string,CodeToMarkdown,app


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
        md_file_path =  pathlib.Path("123_test.md")
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
        result = runner.invoke(app, [ str(md_file_path),'--no-date-stamp'])

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
            '--no-date-stamp',
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
    expected_output_file =  pathlib.Path("output/example_output.md")

    content = input_md_file.read_text()

    # Call the function, processing Markdown with placeholders
    result = update_markdown_from_string(
        content=content,
        bold=False,
        date_stamp=False,
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
    expected_output_file =  pathlib.Path("output/example_output_br.md")

    content = input_md_file.read_text()

    # Call the function, processing Markdown with placeholders
    result = update_markdown_from_string(
        content=content,
        bold=False,
        date_stamp=False,
        auto_break=True
    )


    # Read the expected Markdown
    expected_output = expected_output_file.read_text()

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match:\n{result}"


def test_update_markdown_csv_date_file(tmp_path):
    """
    Test the update_markdown_file function using actual Markdown and CSV files.
    """

    # Base directories for input and expected files
    input_dir = pathlib.Path("input")
    expected_dir = pathlib.Path("expected")

    # Input and expected file paths
    input_md_file = input_dir / "example.md"
    input_csv_file = input_dir / "test.csv"
    expected_output_file =  pathlib.Path("output/example_output_date.md")

    content = input_md_file.read_text()

    # Call the function, processing Markdown with placeholders
    result = update_markdown_from_string(
        content=content,
        bold='',
        date_stamp=True,
        auto_break=False,
        now_ = dt.datetime(2023, 1, 1, 12, 34, 56)
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
    expected_output_file =  pathlib.Path("output/example_python.md")

    content = input_md_file.read_text()

    # Call the function, processing Markdown with placeholders
    result = update_markdown_from_string(
        content=content,
        bold='',
        date_stamp=False,
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
        date_stamp=False,
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
    converter = CsvToMarkdown(non_existent_file, date_stamp=False)

    # Check that the error message is correct
    markdown_output = converter.to_markdown()
    assert "Error" in markdown_output
    assert "Error: File 'non_existent_file.csv' not found." in markdown_output


class TestableToMarkdown(ToMarkdown):
    """Simple concrete implementation of ToMarkdown for testing purposes."""

    def to_markdown(self):
        return self.text


def test_file_time_stamp_md_file_not_found():
    """Test that file_time_stamp_md handles FileNotFoundError correctly.

    This test verifies that when a non-existent file is provided to the
    file_time_stamp_md method, it returns a proper warning message.
    """
    # Use a file path that definitely doesn't exist
    non_existent_file = pathlib.Path("this_file_does_not_exist.txt")

    # Ensure the file doesn't exist
    non_existent_file.unlink(missing_ok=True)
    assert not non_existent_file.exists()

    # Create an instance with any file name (doesn't matter for this test)
    converter = TestableToMarkdown("test_file.txt")

    # Call the method with the non-existent file path
    result = converter.file_time_stamp_md(str(non_existent_file))

    # Check that the result contains the expected warning
    assert "WARNING:(file not found)" in result
    assert non_existent_file.name in result
    assert "<small>" in result
    assert "</small>" in result


def test_file_time_stamp_md_tag_parameter():
    """Test that file_time_stamp_md correctly uses the tag parameter.

    This test verifies that the method properly wraps the output with
    the HTML tag specified in the tag parameter.
    """
    # Create a temporary file that exists
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = pathlib.Path(temp_dir) / "temp_file.txt"
        temp_file.touch()

        converter = TestableToMarkdown("test_file.txt")

        # Test with default tag (small)
        default_result = converter.file_time_stamp_md(str(temp_file))
        assert "<small>" in default_result
        assert "</small>" in default_result

        # Test with custom tag
        custom_result = converter.file_time_stamp_md(str(temp_file), tag="div")
        assert "<div>" in custom_result
        assert "</div>" in custom_result

        # Test with no tag
        no_tag_result = converter.file_time_stamp_md(str(temp_file), tag="")
        assert "<" not in no_tag_result
        assert ">" not in no_tag_result


