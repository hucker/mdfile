
import pathlib
import importlib
import tempfile
import datetime as dt
import json
import pytest

from to_md.csv_to_md import CsvToMarkdown
from md_updater import  update_markdown_from_string,update_markdown_file
from updater.process import ProcessBlockReplacer

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

def xxxtest_update_proc_insert():
    content, expected = file_setup("example_proc_insert.md", "example_proc_insert.md")
    result = update_markdown_from_string(content, bold="", auto_break=False)
    assert result == expected

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
def xxxtest_var_version(template, expected):
    result = update_markdown_from_string(template, "", False)
    assert result == expected

def xxxtest_var_with_json_override(tmp_path):
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




def xxxtest_update_file_insert():
    content, expected = file_setup("example_python_insert.md", "example_python_insert.md")
    result = update_markdown_from_string(content, "", False)
    assert result == expected



def xxxtest_update_markdown_csv_file():
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

    # Call the function, processing Markdown with placeholders
    result = update_markdown_from_string(
        content=content,
        bold=False,
        auto_break=False
    )

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match:\n{result}"




def xxxtest_update_markdown_csv_numbers_file():
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
    result = update_markdown_from_string(
        content=content,
        bold=False,
        auto_break=False
    )

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match:\n{result}"


def xxxtest_update_markdown_csv_br_file():
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
    result = update_markdown_from_string(
        content=content,
        bold=False,
        auto_break=True  # Note the auto_break change
    )

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match:\n{result}"




def xxxtest_update_markdown_python_file():
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
    result = update_markdown_from_string(
        content=content,
        bold='',
        auto_break=False,
    )

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
def xxxtest_update_markdown_code_file(lang, code_ext):
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
    result = update_markdown_from_string(
        content=content,
        bold='',
        auto_break=False,
    )

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match for {lang}:\n{result}"



def xxxtest_csv_to_markdown_file_not_found():
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



def xxxtest_file_not_found_error():
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
    test_input = """<!--process "sleep 5"-->\n<!--process end-->"""

    # Execute the update_process_inserts function with a 1-second timeout
    result = ProcessBlockReplacer(timeout_sec=1).update(content=test_input)

    # Check that the result contains a timeout error message
    assert "Timeout Error" in result, "Timeout error indication missing in result"
    assert "timed out after 1 seconds" in result, "Specific timeout duration message missing"

    # Verify the process command was properly formatted in the result
    assert result.startswith("""<!--process "sleep 5"-->"""), "Process command header missing"
    assert "<!--process end-->" in result, "Process command footer missing"

def xxxtest_csv_to_markdown_empty_file():
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


@pytest.mark.parametrize("input_md_filename", [
    "input/example_python_glob.md",  # First test case
    "input/example_python_glob_insert.md",  # Add more cases as needed
])
def xxxtest_glob_pattern_in_file_inserts(input_md_filename):
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



def xxxtest_bad_glob_pattern_error_message():
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
    assert f"<!--file input/XFAF*.py-->" in result, "Original file tag not preserved"
    assert "<!--file end-->" in result, "End file tag not preserved"

    # Make sure no Python code block was included (since no files matched)
    assert "```python" not in result or "```python" in markdown_content, "Python code block should not be added for non-matching glob"




