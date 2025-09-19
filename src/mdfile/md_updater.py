import pathlib


from updater.variables import VariableReplacer
from updater.ignore import IgnoreBlocks
from updater.process import BaseProcessReplacer, ProcessReplacer
from updater.process import ProcessBlockReplacer
from updater.process import ShellReplacer
from updater.process import ShellBlockReplacer
from updater.files import FileBlockInsertReplacer
from updater.files import FileReplacer
from updater.validator import Validator,Tokenizer



CLASSES= (
    ProcessReplacer,
    ProcessBlockReplacer,
    ShellReplacer,
    ShellBlockReplacer,
    FileBlockInsertReplacer,
    FileReplacer,
    VariableReplacer,
    )

def update_markdown_from_string(content: str,
                                bold: str,
                                auto_break: bool,
                                ) -> str:
    """
    Transform the Markdown string with all the class based replacements.

    Supported placeholders:
        1. <!--file <glob_pattern>--> : Replaces with the Markdown tables based on file extension
           for all files matching the glob pattern
        2. <!--process <command>--> : Executes the command and inserts its stdout output

    Args:
        content (str): The Markdown content as a string.
        bold (str): Whether to apply bold styling for certain values.
        auto_break (bool): Whether to auto-wrap content.

    Returns:
        str: The updated Markdown content with placeholders replaced.
    """
    try:
        tokens = list(Tokenizer().tokenize(content))
        validator = Validator()
        validator.validate(tokens)

        ignore = IgnoreBlocks()

        # Extract the ignored blocks.  This should go first.
        content = ignore.extract(content)

        # Apply file insertions
        content = FileBlockInsertReplacer(bold=bold,auto_break=auto_break).update(content)
        content = FileReplacer(bold=bold,auto_break=auto_break).update(content)
        content = ProcessBlockReplacer().update(content)
        content = ProcessReplacer().update(content)
        content = ShellBlockReplacer().update(content)
        content = ShellReplacer().update(content)
        content = VariableReplacer().update(content)

        # Put the ignored blocks back.  This must go after all transforms are complete
        content = ignore.restore(content)

        return content

    except Exception as e:
        return content  # Return original content in the case of error


def update_markdown_file(
        md_file: str,
        bold: str = '',
        auto_break: bool = False,
        out_file: str | None = None,
) -> str:
    """
    Updates a Markdown (.md) file with specified modifications (handled by
    update_markdown_from_string). The file update can be overridden by providing an out_file
    parameter. The normal use case is to update a Markdown file in place.

    Args:
        md_file (str): Path to the Markdown file to be read.
        bold (str, optional): String to be added in bold text format. Defaults to an empty string.
        auto_break (bool): If True, applies automatic line breaking within the content.
        out_file (str, optional): If provided, writes the updated Markdown content to this file.
            Otherwise, updates the original file.

    Returns:
        str: Updated content of the Markdown file after modifications.

    Raises:
        FileNotFoundError: If the specified `md_file` is not found.
        Exception: If an unexpected error occurs during the update process.
    """
    try:
        # Read file content
        with open(md_file, 'r', encoding='utf8') as file:
            content = file.read()

        # Call the string-based update function
        updated_content = update_markdown_from_string(content=content,
                                                      bold=bold,
                                                      auto_break=auto_break,
                                                      )

        # Write updated content to the specified output file
        out_file = out_file or md_file
        with open(out_file, 'w', encoding='utf8') as file_out:
            file_out.write(updated_content)

        return updated_content

    except FileNotFoundError as fnf_error:
        raise FileNotFoundError(f"File '{md_file}' not found.") from fnf_error
