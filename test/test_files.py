import pytest
import pathlib
import tempfile
from md_updater import update_markdown_from_string,update_markdown_file
from updater.files import FileReplacer,FileBlockInsertReplacer

def file_setup(
                md_file:str,
                output_file:str,
                input_folder="input",
                output_folder="output",
):
    input_md_file = pathlib.Path(input_folder) / md_file
    output_md_file = pathlib.Path(output_folder) / output_file

    content = input_md_file.read_text()
    expected = output_md_file.read_text()

    return content, expected


def test_update_proc_insert():
    content, expected = file_setup("example_proc_insert.md", "example_proc_insert.md")
    result = update_markdown_from_string(content, bold="", auto_break=False)
    assert result == expected

def test_update_markdown_csv_file():
    """
    Test the update_markdown_file function using actual Markdown and CSV files.
    """
    # Use file_setup helper to get content and expected values
    content, expected_output = file_setup(
        md_file="example.md",
        output_file="example_output.md",
        input_folder="input",
        output_folder="output"
    )

    result = FileBlockInsertReplacer().update(content)

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match:\n{result}"

def test_update_file_insert():
    content, expected = file_setup("example_python_insert.md", "example_python_insert.md")
    result = FileReplacer().update(content)
    assert result == expected

def test_update_markdown_csv_numbers_file():
    """
    Test the update_markdown_file function using actual Markdown and CSV files.
    """

    # Use file_setup helper to get content and expected values
    content, expected_output = file_setup(
        md_file="example_numbers.md",
        output_file="example_output_numbers.md",
        input_folder="input",
        output_folder="output"
    )

    # Call the function, processing Markdown with placeholders
    result = FileBlockInsertReplacer(bold=False, auto_break=False).update(content)

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match:\n{result}"

def test_update_markdown_csv_br_file():
    """
    Test the update_markdown_file function using actual Markdown and CSV files.
    """

    # Use file_setup helper to get content and expected values
    content, expected_output = file_setup(
        md_file="example.md",
        output_file="example_output_br.md",
        input_folder="input",
        output_folder="output"
    )

    # Call the function, processing Markdown with placeholders
    result = FileBlockInsertReplacer(bold=False, auto_break=True).update(content)

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match:\n{result}"

def test_update_markdown_python_file():
    """
    Test the update_markdown_file function using actual Markdown and Python files.
    """

    # Use file_setup helper to get content and expected values
    content, expected_output = file_setup(
        md_file="example_python.md",
        output_file="example_python.md",
        input_folder="input",
        output_folder="output"
    )

    # Call the function, processing Markdown with placeholders
    result = FileBlockInsertReplacer(bold='', auto_break=False).update(content)

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match:\n{result}"

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
def test_update_markdown_code_file(lang, code_ext):
    """
    Test the update_markdown_file function using parameterized Markdown and code files
    for multiple languages.
    """
    # Use file_setup helper to get content and expected values
    content, expected_output = file_setup(
        md_file=f"example_{lang}.md",
        output_file=f"example_{lang}.md",
        input_folder="input",
        output_folder="output"
    )

    # Call the function, processing Markdown with placeholders
    result = FileBlockInsertReplacer(bold='', auto_break=False).update(content)

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match for {lang}:\n{result}"

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

@pytest.mark.parametrize("input_md_filename", [
    "input/example_python_glob.md",  # First test case
    "input/example_python_glob_insert.md",  # Add more cases as needed
])
def test_glob_pattern_in_file_inserts(input_md_filename):
    """
    Test that glob patterns in file insertion tags work correctly,
    matching multiple files according to the pattern.
    """

    # Convert the filename into a Path object
    input_md = pathlib.Path(input_md_filename)

    # Check if the test file exists
    assert input_md.exists(), f"Input file {input_md_filename} does not exist."

    # Create a test Markdown content with a glob pattern
    markdown_content = input_md.read_text()

    # Process the file insertions
    result = update_markdown_from_string(markdown_content, "", False)

    # Verify the results (specific assertions for the filename can be adjusted)
    # Base assertions for all test cases
    assert "```python" in result, "Python code block not found in result"

def test_bad_glob_pattern_error_message():
    """
    Test that when a glob pattern doesn't match any files, an appropriate
    error message is included in the output.
    """
    # Create a Path object for the input file
    input_md = pathlib.Path("input/example_python_bad_glob.md")

    # Read the Markdown content from the file
    markdown_content = input_md.read_text()

    # Process the file insertions
    result = update_markdown_from_string(markdown_content, "", False)

    # Verify that the error message is included in the result
    expected_error = f"<!-- No files found matching pattern 'input/XFAF*.py' -->"
    assert expected_error in result, "Error message for no matching files not found in result"

    # Verify that the original tags are preserved
    assert f'<!--file "input/XFAF*.py"-->' in result, "Original file tag not preserved"
    assert "<!--file end-->" in result, "End file tag not preserved"

    # Make sure no Python code block was included (since no files matched)
    assert "```python" not in result or "```python" in markdown_content, "Python code block should not be added for non-matching glob"


